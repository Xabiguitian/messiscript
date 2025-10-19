import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, Gdk

from app.presenters.friends_presenter import FriendsPresenter

class FriendsView(Gtk.Box):
    def __init__(self, api_client):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=15,
                         margin_top=20, margin_bottom=20, margin_start=20, margin_end=20)
        self.presenter = FriendsPresenter(self, api_client)
        self._friends_data = []
        self.selected_friend = None

        # --- Título ---
        title_label = Gtk.Label(label="Split - Amigos")
        title_label.add_css_class("section-title")
        self.append(title_label)

        # --- Lista de amigos ---
        self.friends_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.friends_box.add_css_class("friends-list")
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_child(self.friends_box)
        scrolled.set_vexpand(True)
        self.append(scrolled)

        # --- Botones principales ---
        buttons_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        buttons_box.set_halign(Gtk.Align.CENTER)
        self.reload_btn = Gtk.Button(label="Reload")
        self.reload_btn.add_css_class("action-button")
        self.reload_btn.connect("clicked", self.on_reload_clicked)
        buttons_box.append(self.reload_btn)
        self.append(buttons_box)

        # Cargar datos iniciales desde la API
        self.presenter.load_friends()

    def on_reload_clicked(self, button):
        """Recarga amigos desde la API."""
        self.presenter.load_friends()

    def show_friends(self, friends):
        """Recibe lista desde el presenter y la muestra."""
        self._friends_data = friends or []
        # Limpiar lista actual
        child = self.friends_box.get_first_child()
        while child:
            next_child = child.get_next_sibling()
            self.friends_box.remove(child)
            child = next_child

        # Pintar amigos recibidos
        for friend in self._friends_data:
            friend_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            friend_row.add_css_class("friend-row")
            name_label = Gtk.Label(label=friend.get("name", ""))
            name_label.set_hexpand(True)
            name_label.set_halign(Gtk.Align.START)
            expense_btn = Gtk.Button(label="Expense list")
            expense_btn.connect("clicked", self.show_friend_expenses, friend)
            friend_row.append(name_label)
            friend_row.append(expense_btn)
            self.friends_box.append(friend_row)

    def show_friend_expenses(self, button, friend):
        """Diálogo con los gastos del amigo seleccionado.
        Este ejemplo asume que el presenter expone un método para obtener los gastos del amigo."""
        dialog = Gtk.Dialog(title="Split - Amigos - Gastos por amigo")
        dialog.set_transient_for(self.get_root())
        dialog.set_modal(True)
        dialog.set_default_size(400, 300)
        content = dialog.get_content_area()
        content.set_spacing(10)

        # Aquí deberías pedir al presenter los gastos de ese amigo, de manera asíncrona si es necesario
        expenses = friend.get("expenses", [])
        for expense in expenses:
            expense_label = Gtk.Label(label=expense.get("description", ""))
            content.append(expense_label)
        close_btn = Gtk.Button(label="Close")
        close_btn.connect("clicked", lambda b: dialog.close())
        close_btn.set_margin_start(10)
        close_btn.set_margin_end(10)
        content.append(close_btn)
        dialog.show()

    def show_error(self, message):
        dialog = Gtk.MessageDialog(text=message, transient_for=self.get_root(), modal=True)
        dialog.run()
        dialog.close()
