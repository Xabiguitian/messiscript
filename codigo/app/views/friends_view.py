import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk
# Asegúrate de importar el Presenter y GLib
from app.presenters.friends_presenter import FriendsPresenter
from gi.repository import GLib
# No necesitas importar threading aquí normalmente

class FriendsView(Gtk.Box):
    def __init__(self, api_client):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=15,
                         margin_top=20, margin_bottom=20, margin_start=20, margin_end=20)
        self.presenter = FriendsPresenter(self, api_client)
        self._friends_data = []
        # selected_friend no parece usarse globalmente, se puede quitar si no es necesario
        # self.selected_friend = None

        title_label = Gtk.Label(label="Split - Amigos")
        title_label.add_css_class("section-title")
        self.append(title_label)

        self.friends_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.friends_box.add_css_class("friends-list")
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_child(self.friends_box)
        scrolled.set_vexpand(True)
        self.append(scrolled)

        buttons_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        buttons_box.set_halign(Gtk.Align.CENTER)

        self.reload_btn = Gtk.Button(label="Recargar")
        self.reload_btn.add_css_class("action-button")
        self.reload_btn.connect("clicked", self.on_reload_clicked)
        buttons_box.append(self.reload_btn)

        # Spinner principal para feedback de carga
        self.spinner = Gtk.Spinner(spinning=False)
        buttons_box.append(self.spinner)

        self.append(buttons_box)

        # La carga inicial la dispara el presentador de forma asíncrona
        self.presenter.load_friends()

    def start_thinking(self):
        """Método llamado por el presentador (vía GLib.idle_add) para iniciar feedback."""
        if not self.spinner.get_spinning():
            self.spinner.start()
        self.reload_btn.set_sensitive(False)
        # Podrías deshabilitar también clics en la lista si lo ves necesario

    def stop_thinking(self):
        """Método llamado por el presentador (vía GLib.idle_add) para detener feedback."""
        if self.spinner.get_spinning():
            self.spinner.stop()
        self.reload_btn.set_sensitive(True)

    def on_reload_clicked(self, button):
        """Al pulsar Recargar, pide al presentador que cargue (asíncronamente)."""
        self.presenter.load_friends()

    def show_friends(self, friends):
        """Método llamado por el presentador (vía GLib.idle_add) para mostrar amigos."""
        self._friends_data = friends or []

        # Limpiar lista anterior
        child = self.friends_box.get_first_child()
        while child:
            next_child = child.get_next_sibling()
            self.friends_box.remove(child)
            child = next_child

        # Añadir filas nuevas
        if not self._friends_data:
            info_label = Gtk.Label(label="No hay amigos para mostrar.", margin_top=20, margin_bottom=20)
            self.friends_box.append(info_label)
        else:
            for friend in self._friends_data:
                friend_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
                friend_row.add_css_class("friend-row")
                friend_row.set_margin_top(5)
                friend_row.set_margin_bottom(5)
                friend_row.set_margin_start(10)
                friend_row.set_margin_end(10)

                name_label = Gtk.Label(label=friend.get("name", ""), hexpand=True, halign=Gtk.Align.START)

                credit = friend.get('credit_balance', 0)
                debit = friend.get('debit_balance', 0)
                net_balance = credit - debit
                balance_info = f"Balance: {net_balance:+.2f}€"
                balance_label = Gtk.Label(label=balance_info, halign=Gtk.Align.END)

                # Botón para abrir diálogo de gastos (síncrono, pero carga datos asíncronamente)
                expense_btn = Gtk.Button(label="Ver Gastos")
                expense_btn.connect("clicked", self.show_friend_expenses_dialog, friend)

                friend_row.append(name_label)
                friend_row.append(balance_label)
                friend_row.append(expense_btn)

                self.friends_box.append(friend_row)

    def show_friend_expenses_dialog(self, button, friend):
        """Muestra el diálogo y pide al presentador que cargue los datos."""
        friend_id = friend.get("id")
        friend_name = friend.get("name", "Amigo")
        dialog = Gtk.Dialog(title=f"Gastos de {friend_name}", transient_for=self.get_root(), modal=True)
        dialog.set_default_size(450, 350)

        content = dialog.get_content_area()
        content.set_spacing(10)
        content.set_margin_top(10)
        content.set_margin_bottom(10)
        content.set_margin_start(10)
        content.set_margin_end(10)

        scrolled = Gtk.ScrolledWindow(height_request=250)
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        # Box que contendrá el spinner y luego los datos o el error
        expenses_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5, vexpand=True, valign=Gtk.Align.START)
        scrolled.set_child(expenses_box)
        content.append(scrolled)

        # Spinner específico para este diálogo
        dialog_spinner = Gtk.Spinner(spinning=True, halign=Gtk.Align.CENTER, margin_top=20, margin_bottom=20)
        expenses_box.append(dialog_spinner) # Añadirlo primero

        # Petición asíncrona al presentador
        self.presenter.load_friend_expenses(friend_id, expenses_box, dialog_spinner)

        close_btn = Gtk.Button(label="Cerrar")
        close_btn.connect("clicked", lambda b: dialog.destroy())
        close_btn.set_halign(Gtk.Align.END)
        content.append(close_btn)
        dialog.show()

    def populate_friend_expenses_dialog(self, expenses_box: Gtk.Box, expenses: list):
        """Método llamado por el presentador (vía GLib.idle_add) para rellenar el diálogo."""
        # Limpiar spinner si aún está
        child = expenses_box.get_first_child()
        if isinstance(child, Gtk.Spinner):
             expenses_box.remove(child)

        if expenses:
            for expense in expenses:
                debit = expense.get('debit_balance', 0)
                credit = expense.get('credit_balance', 0)
                net_balance = credit - debit
                balance_str = f"{net_balance:+.2f}€"
                expense_label = Gtk.Label(label=f"{expense.get('description', '')}: {balance_str}", halign=Gtk.Align.START)
                expenses_box.append(expense_label)
        else:
            expenses_box.append(Gtk.Label(label="No participa en ningún gasto.", halign=Gtk.Align.CENTER))

    def populate_friend_expenses_error(self, expenses_box: Gtk.Box, error_message: str):
        """Método llamado por el presentador (vía GLib.idle_add) para mostrar error en diálogo."""
        # Limpiar spinner si aún está
        child = expenses_box.get_first_child()
        if isinstance(child, Gtk.Spinner):
             expenses_box.remove(child)

        error_label = Gtk.Label(label=f"Error al cargar gastos: {error_message}", halign=Gtk.Align.START, wrap=True)
        error_label.add_css_class("error-label") # Podrías añadir estilo CSS para errores
        expenses_box.append(error_label)

    def show_error(self, message):
        """Método llamado por el presentador (vía GLib.idle_add) para mostrar error general."""
        # Asegurarse de parar el spinner principal
        self.stop_thinking()

        dialog = Gtk.MessageDialog(
            transient_for=self.get_root(),
            modal=True,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.CLOSE,
            text=message
        )
        dialog.connect("response", lambda d, response_id: d.destroy())
        dialog.show()