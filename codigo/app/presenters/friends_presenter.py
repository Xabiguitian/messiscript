from typing import Any

class FriendsPresenter:
    def __init__(self, view, api_client):
        self.view = view
        self.api_client = api_client

    def load_friends(self, query: str = ""):
        try:
            friends = self.api_client.list_friends()
            if query:
                q = query.strip().lower()
                friends = [f for f in friends if q in str(f.get("name","")).lower()]
            self.view.show_friends(friends)
        except Exception as e:
            self.view.show_error(f"Error cargando amigos: {e}")

    def select_friend(self, friend_id: Any):
        try:
            friend = self.api_client.get_friend(friend_id)
            # La lógica de mostrar detalles y gastos ahora se maneja en el diálogo
            # por lo que este método puede que ya no sea necesario, dependiendo del flujo
        except Exception as e:
            self.view.show_error(f"Error cargando detalle del amigo: {e}")