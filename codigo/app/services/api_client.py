import requests

class ApiClient:

    def __init__(self, base_url: str = "http://127.0.0.1:8000", timeout_s: float = 10.0):
        self._base_url = base_url.rstrip("/")
        self._timeout_s = timeout_s
        self._session = requests.Session()

    def _url(self, endpoint: str) -> str:
        return f"{self._base_url}/{endpoint.lstrip('/')}"

    def list_friends(self):
        r = self._session.get(self._url("/friends/"), timeout=self._timeout_s)
        r.raise_for_status()
        return r.json()

    def get_friend(self, friend_id: int | str):
        r = self._session.get(self._url(f"/friends/{friend_id}/"), timeout=self._timeout_s)
        r.raise_for_status()
        return r.json()

    def list_friend_expenses(self, friend_id: int | str):
        r = self._session.get(self._url(f"/friends/{friend_id}/expenses/"), timeout=self._timeout_s)
        r.raise_for_status()
        return r.json()

    def list_expenses(self, query: str | None = None):
        if query:
            if query.isdigit():
                r = self._session.get(self._url(f"/expenses/{query}"), timeout=self._timeout_s)
                r.raise_for_status()
                return [r.json()]
            else:
                r = self._session.get(self._url("/expenses/"), params={"search": query}, timeout=self._timeout_s)
                r.raise_for_status()
                return r.json()
        else:
            r = self._session.get(self._url("/expenses/"), timeout=self._timeout_s)
            r.raise_for_status()
            return r.json()

    def get_expense(self, expense_id: int | str):
        r = self._session.get(self._url(f"/expenses/{expense_id}/"), timeout=self._timeout_s)
        r.raise_for_status()
        return r.json()

    def create_expense(self, description: str, date: str, amount: float, payer_id: int, participant_ids: list[int]):
        data = {
            "description": description,
            "date": date,
            "amount": amount,
            "payer_id": payer_id,
            "participant_ids": participant_ids
        }
        r = self._session.post(self._url("/expenses/"), json=data, timeout=self._timeout_s)
        r.raise_for_status()
        return r.json()

    def update_expense(self, expense_id: int | str, data: dict):
        # Asegurarse que 'data' tenga la estructura de ExpenseCreate
        # (description, date, amount, payer_id, participant_ids)
        # Se asume que el presentador construye el 'data' correctamente
        data.pop("id", None) # No se envía el id en el body del PUT
        r = self._session.put(self._url(f"/expenses/{expense_id}/"), json=data, timeout=self._timeout_s)
        r.raise_for_status()
        return r.json() if r.text else {} # PUT suele devolver 204 sin body

    def delete_expense(self, expense_id: int | str):
        r = self._session.delete(self._url(f"/expenses/{expense_id}/"), timeout=self._timeout_s)
        r.raise_for_status()
        return {"deleted": expense_id}

    def close(self):
        try:
            self._session.close()
        except Exception:
            pass

    def __del__(self):
        self.close()