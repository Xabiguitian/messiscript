# Asegúrate de importar ApiClient, threading y GLib
from app.services.api_client import ApiClient
import threading
from gi.repository import GLib

class ExpensesPresenter:
    def __init__(self, view, api_client: ApiClient):
        self.view = view
        self.api_client = api_client
        self._friends = [] # Cache de amigos para los selectores

    def load_expenses(self, query=None):
        """Inicia la carga asíncrona de gastos."""
        GLib.idle_add(self.view.start_thinking)
        threading.Thread(
            target=self._slow_load_expenses,
            args=(query,),
            daemon=True
        ).start()

    def _slow_load_expenses(self, query=None):
        """Método en hilo secundario para cargar gastos."""
        try:
            # La API parece devolver lista incluso buscando por ID, adaptamos
            # Nota: list_expenses ya maneja la lógica de buscar por ID si query es dígito
            expenses = self.api_client.list_expenses(query) # Llamada de red
            GLib.idle_add(self.view.show_expenses, expenses)
        except Exception as e:
            GLib.idle_add(self.view.show_error, f"Error cargando gastos: {e}")
        finally:
            GLib.idle_add(self.view.stop_thinking)

    def select_expense(self, expense_id):
        """
        Esta función ya no parece necesaria si la selección de gasto
        solo abre el diálogo de edición con datos ya cargados.
        Si necesitara recargar datos específicos del gasto, se haría asíncrona.
        """
        pass

    def load_friends_for_selection(self):
        """Inicia la carga asíncrona de amigos para los diálogos."""
        # Podríamos no mostrar spinner aquí si se carga al inicio y no molesta
        # GLib.idle_add(self.view.start_thinking)
        threading.Thread(
            target=self._slow_load_friends_for_selection,
            daemon=True
        ).start()

    def _slow_load_friends_for_selection(self):
        """Método en hilo secundario para cargar amigos."""
        try:
            self._friends = self.api_client.list_friends() # Llamada de red
            GLib.idle_add(self.view.populate_friend_selectors, self._friends)
        except Exception as e:
            GLib.idle_add(self.view.show_error, f"Error cargando amigos para selección: {e}")
            # Asegurarse de poblar con lista vacía en caso de error
            GLib.idle_add(self.view.populate_friend_selectors, [])
        # finally:
        #     GLib.idle_add(self.view.stop_thinking) # Solo si iniciamos spinner

    def add_expense(self, description: str, date_str: str, amount_str: str, payer_id: int, participant_ids: list[int]):
        """Valida datos e inicia la creación asíncrona del gasto."""
        try:
            # Validaciones síncronas primero
            if not all([description, date_str, amount_str, payer_id is not None, participant_ids]):
                raise ValueError("Todos los campos son requeridos, incluyendo pagador y participantes.")
            if payer_id not in participant_ids:
                 raise ValueError("El pagador debe estar en la lista de participantes.")

            amount = float(amount_str) # Puede lanzar ValueError
            if amount <= 0:
                 raise ValueError("El monto debe ser positivo.")
            # Podríamos añadir validación de formato de fecha aquí también si quisiéramos

            # Si validaciones OK, lanzar hilo
            GLib.idle_add(self.view.start_thinking_dialog, self.view.create_dialog) # Feedback en diálogo
            threading.Thread(
                target=self._slow_add_expense,
                args=(description, date_str, amount, payer_id, participant_ids),
                daemon=True
            ).start()

        except ValueError as ve:
             # Error de validación, mostrar en vista (síncrono)
             self.view.show_error(f"Error en los datos: {ve}")
        except Exception as e:
            # Otro error síncrono (ej, conversión a float)
            self.view.show_error(f"Error procesando datos: {e}")

    def _slow_add_expense(self, description, date_str, amount, payer_id, participant_ids):
        """Método en hilo secundario para crear el gasto."""
        try:
            created_expense = self.api_client.create_expense( # Llamada de red
                description=description,
                date=date_str,
                amount=amount,
                payer_id=payer_id,
                participant_ids=participant_ids
            )
            # Éxito: pedir al hilo principal mostrar mensaje, recargar lista y cerrar diálogo
            desc = created_expense.get('description', 'Nuevo')
            GLib.idle_add(self.view.show_status, f"Gasto '{desc}' añadido correctamente.")
            GLib.idle_add(self.load_expenses) # Inicia recarga asíncrona
            GLib.idle_add(self.view.close_create_dialog)

        except Exception as e:
            # Error: pedir al hilo principal mostrar el error detallado
            detail = self._extract_error_detail(e)
            GLib.idle_add(self.view.show_error, f"Error creando gasto: {detail}")
        finally:
            # Siempre: pedir al hilo principal detener feedback del diálogo
            GLib.idle_add(self.view.stop_thinking_dialog, self.view.create_dialog)

    def update_expense(self, expense_id, data: dict):
        """Valida datos e inicia la actualización asíncrona del gasto."""
        try:
            # Añadir validaciones síncronas si son necesarias (ej. monto > 0)
            amount = data.get('amount', 0)
            if float(amount) <= 0:
                raise ValueError("El monto debe ser positivo.")
            if data.get('payer_id') not in data.get('participant_ids', []):
                raise ValueError("El pagador debe estar en la lista de participantes.")
            if not data.get('participant_ids'):
                raise ValueError("Debe haber al menos un participante.")
            # Podríamos validar formato fecha también

            # Si validaciones OK, lanzar hilo
            GLib.idle_add(self.view.start_thinking_dialog, self.view.edit_dialog)
            threading.Thread(
                target=self._slow_update_expense,
                args=(expense_id, data),
                daemon=True
            ).start()
        except ValueError as ve:
            self.view.show_error(f"Error en los datos: {ve}")
        except Exception as e:
            self.view.show_error(f"Error procesando datos para actualizar: {e}")


    def _slow_update_expense(self, expense_id, data: dict):
        """Método en hilo secundario para actualizar el gasto."""
        try:
            self.api_client.update_expense(expense_id, data) # Llamada de red
            # Éxito: pedir al hilo principal mostrar mensaje, recargar y cerrar
            GLib.idle_add(self.view.show_status, "Gasto actualizado correctamente.")
            GLib.idle_add(self.load_expenses) # Recarga asíncrona
            GLib.idle_add(self.view.close_edit_dialog)
        except Exception as e:
            # Error: pedir al hilo principal mostrar error detallado
            detail = self._extract_error_detail(e)
            GLib.idle_add(self.view.show_error, f"Error al actualizar gasto: {detail}")
        finally:
            # Siempre: pedir al hilo principal detener feedback del diálogo
            GLib.idle_add(self.view.stop_thinking_dialog, self.view.edit_dialog)

    def delete_expense(self, expense_id):
        """Inicia la eliminación asíncrona del gasto."""
        GLib.idle_add(self.view.start_thinking_dialog, self.view.edit_dialog) # Asume que se llama desde edit
        threading.Thread(
            target=self._slow_delete_expense,
            args=(expense_id,),
            daemon=True
        ).start()

    def _slow_delete_expense(self, expense_id):
        """Método en hilo secundario para eliminar el gasto."""
        try:
            self.api_client.delete_expense(expense_id) # Llamada de red
            # Éxito: pedir al hilo principal mostrar mensaje, recargar y cerrar
            GLib.idle_add(self.view.show_status, "Gasto eliminado.")
            GLib.idle_add(self.load_expenses) # Recarga asíncrona
            GLib.idle_add(self.view.close_edit_dialog)
        except Exception as e:
            # Error: pedir al hilo principal mostrar error detallado
            detail = self._extract_error_detail(e)
            GLib.idle_add(self.view.show_error, f"Error al eliminar gasto: {detail}")
        finally:
            # Siempre: pedir al hilo principal detener feedback del diálogo
            GLib.idle_add(self.view.stop_thinking_dialog, self.view.edit_dialog)

    def _extract_error_detail(self, e: Exception) -> str:
        """Función auxiliar para obtener un mensaje de error más útil desde la API."""
        detail = str(e)
        # Intenta obtener el 'detail' del JSON de error de FastAPI si existe
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_data = e.response.json()
                detail = error_data.get('detail', e.response.text)
            except:
                # Si no es JSON, usa el texto plano de la respuesta
                detail = e.response.text if e.response.text else detail
        return detail
