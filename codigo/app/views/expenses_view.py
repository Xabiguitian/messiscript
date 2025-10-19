import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, Gdk
from app.presenters.expenses_presenter import ExpensesPresenter

class ExpensesView(Gtk.Box):
    def __init__(self, api_client):
        super().__init__(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=15,
            margin_top=20, margin_bottom=20, margin_start=20, margin_end=20
        )

        self.presenter = ExpensesPresenter(self, api_client)
        self._expenses_data = []
        self.selected_expense = None

        # --- Título ---
        titulo = Gtk.Label(label="Split - Gastos")
        titulo.add_css_class("section-title")
        self.append(titulo)

        # --- Lista de gastos ---
        self.expenses_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.expenses_box.add_css_class("friends-list")

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_child(self.expenses_box)
        scrolled.set_vexpand(True)
        self.append(scrolled)

        # --- Botones principales ---
        buttons_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        buttons_box.set_halign(Gtk.Align.CENTER)

        self.añadir_gasto = Gtk.Button(label="Create expense")
        self.añadir_gasto.add_css_class("action-button")
        self.añadir_gasto.connect("clicked", self.on_create_expense_clicked)

        self.mostrar_lista_gastos = Gtk.Button(label="Show expense list")
        self.mostrar_lista_gastos.add_css_class("action-button")
        self.mostrar_lista_gastos.connect("clicked", self.on_show_list_clicked)

        buttons_box.append(self.añadir_gasto)
        buttons_box.append(self.mostrar_lista_gastos)
        self.append(buttons_box)

        # Cargar datos iniciales desde la API
        self.presenter.load_expenses()

    def update_expenses_list(self):
        """Actualiza la visualización de la lista de gastos con estilo."""
        # Limpiar lista actual
        child = self.expenses_box.get_first_child()
        while child:
            next_child = child.get_next_sibling()
            self.expenses_box.remove(child)
            child = next_child

        # Añadir gastos recibidos
        for expense in self._expenses_data:
            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            row.add_css_class("friend-row")
            row.set_margin_top(5)
            row.set_margin_bottom(5)
            row.set_margin_start(10)
            row.set_margin_end(10)

            desclabel = Gtk.Label(label=expense.get("description", ""))
            desclabel.set_hexpand(True)
            desclabel.set_halign(Gtk.Align.START)

            amountlabel = Gtk.Label(label=f'${expense.get("amount", 0):.2f}')
            amountlabel.set_halign(Gtk.Align.END)

            row.append(desclabel)
            row.append(amountlabel)

            gesture = Gtk.GestureClick.new()
            gesture.connect("pressed", self.on_expense_selected, expense)
            row.add_controller(gesture)

            self.expenses_box.append(row)

    def on_create_expense_clicked(self, button):
        """Abre diálogo para crear un gasto."""
        # Aquí abrirías un diálogo para crear y luego llamar presenter.create_expense
        pass

    def on_expense_selected(self, gesture, n_press, x, y, expense):
        """Selecciona gasto para edición."""
        self.selected_expense = expense
        self.show_edit_dialog()

    def show_edit_dialog(self):
        """Muestra diálogo para editar gasto."""
        # Conversación similar, después llamar presenter para actualizar o eliminar
        pass

    def on_show_list_clicked(self, button):
        """Muestra listado detallado de gastos en tabla."""
        dialog = Gtk.Dialog(title="Split - Gastos - Lista")
        dialog.set_transient_for(self.get_root())
        dialog.set_modal(True)
        dialog.set_default_size(700, 500)

        content = dialog.get_content_area()
        content.set_spacing(10)

        grid = Gtk.Grid()
        grid.set_row_spacing(5)
        grid.set_column_spacing(10)
        grid.add_css_class("expense-table")

        headers = ["ID", "Description", "Date", "Amount", "Friends", "Credits"]
        for i, header in enumerate(headers):
            label = Gtk.Label(label=header)
            label.add_css_class("table-header")
            grid.attach(label, i, 0, 1, 1)

        for row_idx, expense in enumerate(self._expenses_data, 1):
            values = [
                str(expense.get("id", "")),
                expense.get("description", ""),
                expense.get("date", ""),
                f"${expense.get('amount', 0):.2f}",
                expense.get("friends", ""),
                f"${expense.get('credits', 0):.2f}"
            ]
            for col, value in enumerate(values):
                label = Gtk.Label(label=value)
                label.add_css_class("table-cell")
                grid.attach(label, col, row_idx, 1, 1)

        wrapper = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        wrapper.set_margin_top(16)
        wrapper.append(grid)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_child(wrapper)
        scrolled.set_vexpand(True)
        content.append(scrolled)

        close_btn = Gtk.Button(label="X")
        close_btn.connect("clicked", lambda b: dialog.close())
        close_btn.set_halign(Gtk.Align.END)
        content.append(close_btn)

        dialog.show()

    def show_expenses(self, expenses):
        """Llama el presenter cuando recibe los datos."""
        self._expenses_data = expenses or []
        self.update_expenses_list()

    def show_error(self, message):
        dialog = Gtk.MessageDialog(text=message, transient_for=self.get_root(), modal=True)
        dialog.run()
        dialog.close()
