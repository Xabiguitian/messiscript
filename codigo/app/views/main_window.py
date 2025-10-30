import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, Gio, Gdk

from app.views.friends_view import FriendsView
from app.views.expenses_view import ExpensesView
from app.services.api_client import ApiClient
# 1. Importar la función de traducción
from app.i18n import _ 

class MainWindow(Gtk.ApplicationWindow):

    def __init__(self, self_app):
        # 2. Traducir el título de la ventana
        super().__init__(application=self_app, title=_("Split"))
        self.set_default_size(900, 600)

        # --- CSS ---
        css_provider = Gtk.CssProvider()
        css_provider.load_from_path("style.css")
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        # --- Layout principal ---
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.set_child(main_box)

        # --- Header ---
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        header_box.set_margin_top(10)
        header_box.set_margin_bottom(10)
        header_box.set_margin_start(20)
        header_box.set_margin_end(20)
        header_box.add_css_class("header")

        # 3. Traducir etiqueta del título
        title_label = Gtk.Label(label=_("Split"))
        title_label.add_css_class("main-title")

        # 4. Traducir etiquetas de botones de navegación
        self.friends_button = Gtk.Button(label=_("View Friends"))
        self.friends_button.add_css_class("nav-button")
        
        self.expenses_button = Gtk.Button(label=_("View Expenses"))
        self.expenses_button.add_css_class("nav-button")

        header_box.append(title_label)
        header_box.append(self.friends_button)
        header_box.append(self.expenses_button)

        # --- Área principal ---
        self.stack = Gtk.Stack()
        self.stack.set_vexpand(True)
        self.stack.set_hexpand(True)

        # API client
        self.api_client = ApiClient("http://127.0.0.1:8000")

        # Vistas
        self.friends_view = FriendsView(self.api_client)
        self.expenses_view = ExpensesView(self.api_client)

        # 5. Traducir nombres de pestañas (el Gtk.Stack usa la label para los títulos)
        self.stack.add_titled(self.friends_view, "friends", _("Friends"))
        self.stack.add_titled(self.expenses_view, "expenses", _("Expenses"))
        self.stack.set_visible_child_name("friends")

        self.friends_button.connect("clicked", self.show_friends)
        self.expenses_button.connect("clicked", self.show_expenses)

        main_box.append(header_box)
        main_box.append(self.stack)

    # --- Acciones ---
    def show_friends(self, button):
        self.stack.set_visible_child_name("friends")

    def show_expenses(self, button):
        self.stack.set_visible_child_name("expenses")
