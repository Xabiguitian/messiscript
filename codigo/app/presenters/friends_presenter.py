from typing import Any
import threading
from gi.repository import GLib
# Asegúrate de importar ApiClient según tu estructura, por ejemplo:
# from app.services.api_client import ApiClient

class FriendsPresenter:
    def __init__(self, view, api_client):
        self.view = view
        self.api_client = api_client

    def load_friends(self, query: str = ""):
        """Inicia la carga asíncrona de amigos."""
        # Avisa a la Vista para mostrar feedback (spinner)
        GLib.idle_add(self.view.start_thinking)
        # Lanza la operación de red en un hilo separado
        threading.Thread(
            target=self._slow_load_friends,
            args=(query,),
            daemon=True
        ).start()

    def _slow_load_friends(self, query: str):
        """Método ejecutado en hilo secundario para cargar amigos."""
        try:
            friends = self.api_client.list_friends() # Llamada de red
            if query:
                q = query.strip().lower()
                friends = [f for f in friends if q in str(f.get("name","")).lower()]

            # Pide al hilo principal actualizar la UI con los datos
            GLib.idle_add(self.view.show_friends, friends)
        except Exception as e:
            # Pide al hilo principal mostrar el error
            GLib.idle_add(self.view.show_error, f"Error cargando amigos: {e}")
        finally:
            # Pide al hilo principal ocultar feedback (spinner)
            GLib.idle_add(self.view.stop_thinking)

    def select_friend(self, friend_id: Any):
        """
        Si esta función necesitara cargar datos detallados del amigo
        desde la API, también debería hacerse asíncrona.
        Actualmente, la lógica de detalle se maneja en el diálogo de gastos.
        """
        # Ejemplo si necesitara cargar datos:
        # GLib.idle_add(self.view.start_thinking)
        # threading.Thread(target=self._slow_select_friend, args=(friend_id,), daemon=True).start()
        pass # No hace nada actualmente

    # def _slow_select_friend(self, friend_id):
    #     try:
    #         friend_details = self.api_client.get_friend(friend_id)
    #         GLib.idle_add(self.view.show_friend_details, friend_details) # Necesitaría método en la vista
    #     except Exception as e:
    #         GLib.idle_add(self.view.show_error, f"Error cargando detalle del amigo: {e}")
    #     finally:
    #         GLib.idle_add(self.view.stop_thinking)


    def load_friend_expenses(self, friend_id: int, dialog_expenses_box: Any, dialog_spinner: Any):
        """Inicia la carga asíncrona de gastos para el diálogo de un amigo."""
        # El spinner del diálogo ya se muestra al crearlo en la vista
        threading.Thread(
            target=self._slow_load_friend_expenses,
            args=(friend_id, dialog_expenses_box, dialog_spinner),
            daemon=True
        ).start()

    def _slow_load_friend_expenses(self, friend_id: int, expenses_box: Any, spinner: Any):
        """Método ejecutado en hilo secundario para cargar gastos del amigo."""
        try:
            expenses = self.api_client.list_friend_expenses(friend_id) # Llamada de red
            # Pide al hilo principal rellenar el contenido del diálogo
            GLib.idle_add(self.view.populate_friend_expenses_dialog, expenses_box, expenses)
        except Exception as e:
            # Pide al hilo principal mostrar el error DENTRO del diálogo
            GLib.idle_add(self.view.populate_friend_expenses_error, expenses_box, str(e))
        finally:
            # Pide al hilo principal detener el spinner DEL diálogo
            GLib.idle_add(spinner.stop)