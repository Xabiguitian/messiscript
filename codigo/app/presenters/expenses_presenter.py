from app.services.api_client import ApiClient

class ExpensesPresenter:
    def __init__(self, view, api_client: ApiClient):
        self.view = view
        self.api_client = api_client
        self._friends = []

    def load_expenses(self, query=None):
        try:
            if query:
                expenses = [self.api_client.get_expense(query)]
            else:
                expenses = self.api_client.list_expenses()
            self.view.show_expenses(expenses)
        except Exception as e:
            self.view.show_error(f"Error cargando gastos: {e}")

    def select_expense(self, expense_id):
        try:
            expense = self.api_client.get_expense(expense_id)
            self.view.show_expense_detail(expense)
        except Exception as e:
            self.view.show_error(f"Error cargando detalle del gasto: {e}")

    def load_friends_for_selection(self):
        try:
            self._friends = self.api_client.list_friends()
            self.view.populate_friend_selectors(self._friends)
        except Exception as e:
            self.view.show_error(f"Error cargando amigos para selección: {e}")
            self.view.populate_friend_selectors([])

    def add_expense(self, description: str, date_str: str, amount_str: str, payer_id: int, participant_ids: list[int]):
        try:
            if not description or not date_str or not amount_str or payer_id is None or not participant_ids:
                raise ValueError("Todos los campos son requeridos, incluyendo pagador y participantes.")
            if payer_id not in participant_ids:
                 raise ValueError("El pagador debe estar en la lista de participantes.")

            amount = float(amount_str)
            if amount <= 0:
                 raise ValueError("El monto debe ser positivo.")

            created_expense = self.api_client.create_expense(
                description=description,
                date=date_str,
                amount=amount,
                payer_id=payer_id,
                participant_ids=participant_ids
            )
            self.view.show_status(f"Gasto '{created_expense.get('description')}' añadido correctamente.")
            self.load_expenses()
            self.view.close_create_dialog()

        except ValueError as ve:
             self.view.show_error(f"Error en los datos: {ve}")
        except Exception as e:
            detail = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    detail = error_data.get('detail', e.response.text)
                except:
                    detail = e.response.text
            self.view.show_error(f"Error creando gasto: {detail}")

    def update_expense(self, expense_id, data: dict):
        try:
            self.api_client.update_expense(expense_id, data)
            self.view.show_status("Gasto actualizado correctamente.")
            self.load_expenses()
            self.view.close_edit_dialog()
        except Exception as e:
            detail = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    detail = error_data.get('detail', e.response.text)
                except:
                    detail = e.response.text
            self.view.show_error(f"Error al actualizar gasto: {detail}")

    def delete_expense(self, expense_id):
        try:
            self.api_client.delete_expense(expense_id)
            self.load_expenses()
            self.view.show_status("Gasto eliminado.")
        except Exception as e:
            detail = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    detail = error_data.get('detail', e.response.text)
                except:
                    detail = e.response.text
            self.view.show_error(f"Error al eliminar gasto: {detail}")