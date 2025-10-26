import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, Gdk
from app.presenters.expenses_presenter import ExpensesPresenter

class FriendCheckButton(Gtk.CheckButton):
    def __init__(self, friend_id, **kwargs):
        super().__init__(**kwargs)
        self.friend_id = friend_id

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

        self._friends_list_for_selection = []
        self.create_dialog = None
        self.edit_dialog = None
        
        titulo = Gtk.Label(label="Split - Gastos")
        titulo.add_css_class("section-title")
        self.append(titulo)

        self.expenses_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.expenses_box.add_css_class("friends-list")

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_child(self.expenses_box)
        scrolled.set_vexpand(True)
        self.append(scrolled)

        buttons_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        buttons_box.set_halign(Gtk.Align.CENTER)

        self.añadir_gasto = Gtk.Button(label="Crear Gasto")
        self.añadir_gasto.add_css_class("action-button")
        self.añadir_gasto.connect("clicked", self.on_create_expense_clicked)

        self.mostrar_lista_gastos = Gtk.Button(label="Mostrar Lista Detallada")
        self.mostrar_lista_gastos.add_css_class("action-button")
        self.mostrar_lista_gastos.connect("clicked", self.on_show_list_clicked)

        buttons_box.append(self.añadir_gasto)
        buttons_box.append(self.mostrar_lista_gastos)
        self.append(buttons_box)

        self.presenter.load_expenses()
        self.presenter.load_friends_for_selection()

    def populate_friend_selectors(self, friends_list):
        self._friends_list_for_selection = friends_list

    def on_create_expense_clicked(self, button):
        if self.create_dialog:
            self.create_dialog.destroy()

        self.create_dialog = Gtk.Dialog(title="Crear Nuevo Gasto", transient_for=self.get_root(), modal=True)
        self.create_dialog.set_default_size(400, 450)

        content_area = self.create_dialog.get_content_area()
        content_area.set_spacing(10)
        content_area.set_margin_top(10)
        content_area.set_margin_bottom(10)
        content_area.set_margin_start(10)
        content_area.set_margin_end(10)

        grid = Gtk.Grid(column_spacing=10, row_spacing=10, hexpand=True)

        desc_entry = Gtk.Entry(placeholder_text="Descripción", hexpand=True)
        date_entry = Gtk.Entry(placeholder_text="YYYY-MM-DD", hexpand=True)
        amount_adj = Gtk.Adjustment(value=0.01, lower=0.01, upper=1000000, step_increment=0.1, page_increment=10)
        amount_entry = Gtk.SpinButton(adjustment=amount_adj, digits=2, hexpand=True)

        grid.attach(Gtk.Label(label="Descripción:", halign=Gtk.Align.START), 0, 0, 1, 1)
        grid.attach(desc_entry, 1, 0, 1, 1)
        grid.attach(Gtk.Label(label="Fecha:", halign=Gtk.Align.START), 0, 1, 1, 1)
        grid.attach(date_entry, 1, 1, 1, 1)
        grid.attach(Gtk.Label(label="Monto:", halign=Gtk.Align.START), 0, 2, 1, 1)
        grid.attach(amount_entry, 1, 2, 1, 1)

        payer_combo = Gtk.ComboBoxText(hexpand=True)
        payer_combo.append("0", "Selecciona quién pagó...")
        for friend in self._friends_list_for_selection:
            payer_combo.append(str(friend.get('id')), friend.get('name'))
        payer_combo.set_active(0)
        grid.attach(Gtk.Label(label="Pagado por:", halign=Gtk.Align.START), 0, 3, 1, 1)
        grid.attach(payer_combo, 1, 3, 1, 1)

        grid.attach(Gtk.Label(label="Participantes:", halign=Gtk.Align.START), 0, 4, 2, 1)
        scrolled_participants = Gtk.ScrolledWindow(height_request=150, hexpand=True, vexpand=True)
        scrolled_participants.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        participants_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        scrolled_participants.set_child(participants_box)

        for friend in self._friends_list_for_selection:
            cb = FriendCheckButton(label=friend.get('name'), friend_id=friend.get('id'))
            participants_box.append(cb)

        grid.attach(scrolled_participants, 0, 5, 2, 1)
        content_area.append(grid)

        self.create_dialog.add_button("Cancelar", Gtk.ResponseType.CANCEL)
        self.create_dialog.add_button("Guardar", Gtk.ResponseType.OK)

        self.create_dialog.connect("response", self.on_create_dialog_response, desc_entry, date_entry, amount_entry, payer_combo, participants_box)
        self.create_dialog.show()

    def on_create_dialog_response(self, dialog, response_id, desc_entry, date_entry, amount_entry, payer_combo, participants_box):
        should_close = True
        if response_id == Gtk.ResponseType.OK:
            try:
                description = desc_entry.get_text()
                date_str = date_entry.get_text()
                amount_str = str(amount_entry.get_value())

                payer_id_str = payer_combo.get_active_id()
                if not payer_id_str or payer_id_str == "0":
                    raise ValueError("Debes seleccionar quién pagó el gasto.")
                payer_id = int(payer_id_str)

                participant_ids = []
                child = participants_box.get_first_child()
                while child:
                    if isinstance(child, FriendCheckButton) and child.get_active():
                        participant_ids.append(child.friend_id)
                    child = child.get_next_sibling()

                if not participant_ids:
                     raise ValueError("Debes seleccionar al menos un participante.")

                self.presenter.add_expense(description, date_str, amount_str, payer_id, participant_ids)

            except ValueError as ve:
                self.show_error(f"Error en el formulario: {ve}")
                should_close = False
            except Exception as e:
                self.show_error(f"Error inesperado al procesar datos: {e}")
                should_close = False

        if should_close:
            dialog.destroy()
            self.create_dialog = None

    def close_create_dialog(self):
        if self.create_dialog:
            self.create_dialog.destroy()
            self.create_dialog = None

    def update_expenses_list(self):
        child = self.expenses_box.get_first_child()
        while child:
            next_child = child.get_next_sibling()
            self.expenses_box.remove(child)
            child = next_child

        for expense in self._expenses_data:
            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            row.add_css_class("friend-row")
            row.set_margin_top(5)
            row.set_margin_bottom(5)
            row.set_margin_start(10)
            row.set_margin_end(10)

            payer_info = ""
            payer = expense.get("payer")
            if payer and isinstance(payer, dict):
                 payer_info = f" (Pagó: {payer.get('name', '?')})"

            desclabel = Gtk.Label(label=expense.get("description", "") + payer_info, hexpand=True, halign=Gtk.Align.START)
            amountlabel = Gtk.Label(label=f'{expense.get("amount", 0):.2f} €', halign=Gtk.Align.END)

            row.append(desclabel)
            row.append(amountlabel)

            gesture = Gtk.GestureClick.new()
            gesture.connect("pressed", self.on_expense_selected, expense)
            row.add_controller(gesture)

            self.expenses_box.append(row)

    def on_expense_selected(self, gesture, n_press, x, y, expense):
        self.selected_expense = expense
        self.show_edit_dialog()

    def show_edit_dialog(self):
        if not self.selected_expense:
            return
        
        if self.edit_dialog:
            self.edit_dialog.destroy()

        self.edit_dialog = Gtk.Dialog(title="Editar Gasto", transient_for=self.get_root(), modal=True)
        self.edit_dialog.set_default_size(400, 450)

        content_area = self.edit_dialog.get_content_area()
        content_area.set_spacing(10)
        content_area.set_margin_top(10)
        content_area.set_margin_bottom(10)
        content_area.set_margin_start(10)
        content_area.set_margin_end(10)

        grid = Gtk.Grid(column_spacing=10, row_spacing=10, hexpand=True)

        desc_entry = Gtk.Entry(hexpand=True, text=self.selected_expense.get("description", ""))
        date_entry = Gtk.Entry(hexpand=True, text=self.selected_expense.get("date", ""))
        amount_adj = Gtk.Adjustment(value=self.selected_expense.get("amount", 0.01), lower=0.01, upper=1000000, step_increment=0.1, page_increment=10)
        amount_entry = Gtk.SpinButton(adjustment=amount_adj, digits=2, hexpand=True)

        grid.attach(Gtk.Label(label="Descripción:", halign=Gtk.Align.START), 0, 0, 1, 1)
        grid.attach(desc_entry, 1, 0, 1, 1)
        grid.attach(Gtk.Label(label="Fecha:", halign=Gtk.Align.START), 0, 1, 1, 1)
        grid.attach(date_entry, 1, 1, 1, 1)
        grid.attach(Gtk.Label(label="Monto:", halign=Gtk.Align.START), 0, 2, 1, 1)
        grid.attach(amount_entry, 1, 2, 1, 1)

        payer_combo = Gtk.ComboBoxText(hexpand=True)
        payer_combo.append("0", "Selecciona quién pagó...")
        for friend in self._friends_list_for_selection:
            payer_combo.append(str(friend.get('id')), friend.get('name'))
        
        payer_id_str = str(self.selected_expense.get("payer_id", "0"))
        payer_combo.set_active_id(payer_id_str)
        
        grid.attach(Gtk.Label(label="Pagado por:", halign=Gtk.Align.START), 0, 3, 1, 1)
        grid.attach(payer_combo, 1, 3, 1, 1)

        grid.attach(Gtk.Label(label="Participantes:", halign=Gtk.Align.START), 0, 4, 2, 1)
        scrolled_participants = Gtk.ScrolledWindow(height_request=150, hexpand=True, vexpand=True)
        scrolled_participants.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        participants_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        scrolled_participants.set_child(participants_box)
        
        participant_ids = {link['friend_id'] for link in self.selected_expense.get("friend_links", [])}

        for friend in self._friends_list_for_selection:
            cb = FriendCheckButton(label=friend.get('name'), friend_id=friend.get('id'))
            if friend.get('id') in participant_ids:
                cb.set_active(True)
            participants_box.append(cb)

        grid.attach(scrolled_participants, 0, 5, 2, 1)
        content_area.append(grid)

        self.edit_dialog.add_button("Cancelar", Gtk.ResponseType.CANCEL)
        self.edit_dialog.add_button("Eliminar", Gtk.ResponseType.REJECT)
        self.edit_dialog.add_button("Guardar Cambios", Gtk.ResponseType.OK)

        self.edit_dialog.connect("response", self.on_edit_dialog_response, desc_entry, date_entry, amount_entry, payer_combo, participants_box)
        self.edit_dialog.show()

    def on_edit_dialog_response(self, dialog, response_id, desc_entry, date_entry, amount_entry, payer_combo, participants_box):
        should_close = True
        expense_id = self.selected_expense.get("id")

        if response_id == Gtk.ResponseType.REJECT:
            self.presenter.delete_expense(expense_id)
        elif response_id == Gtk.ResponseType.OK:
            try:
                if not expense_id:
                    raise ValueError("No se pudo identificar el gasto a editar.")

                payer_id_str = payer_combo.get_active_id()
                if not payer_id_str or payer_id_str == "0":
                    raise ValueError("Debes seleccionar un pagador.")

                participant_ids = []
                child = participants_box.get_first_child()
                while child:
                    if isinstance(child, FriendCheckButton) and child.get_active():
                        participant_ids.append(child.friend_id)
                    child = child.get_next_sibling()
                
                if not participant_ids:
                    raise ValueError("Debe haber al menos un participante.")

                updated_data = {
                    "description": desc_entry.get_text(),
                    "date": date_entry.get_text(),
                    "amount": amount_entry.get_value(),
                    "payer_id": int(payer_id_str),
                    "participant_ids": participant_ids
                }
                
                self.presenter.update_expense(expense_id, updated_data)

            except ValueError as ve:
                self.show_error(f"Error en el formulario: {ve}")
                should_close = False
            except Exception as e:
                self.show_error(f"Error inesperado al guardar: {e}")
                should_close = False

        if should_close:
            dialog.destroy()
            self.edit_dialog = None

    def close_edit_dialog(self):
        if self.edit_dialog:
            self.edit_dialog.destroy()
            self.edit_dialog = None

    def on_show_list_clicked(self, button):
        dialog = Gtk.Dialog(title="Split - Gastos - Lista Detallada", transient_for=self.get_root(), modal=True)
        dialog.set_default_size(700, 500)

        content = dialog.get_content_area()
        content.set_spacing(10)

        grid = Gtk.Grid(column_spacing=10, row_spacing=5)
        grid.add_css_class("expense-table")

        headers = ["ID", "Descripción", "Fecha", "Monto", "Pagador", "# Participantes"]
        for i, header in enumerate(headers):
            label = Gtk.Label(label=header, halign=Gtk.Align.START)
            label.add_css_class("table-header")
            grid.attach(label, i, 0, 1, 1)

        for row_idx, expense in enumerate(self._expenses_data, 1):
            payer_name = "?"
            payer = expense.get("payer")
            if payer and isinstance(payer, dict):
                payer_name = payer.get('name', '?')

            num_participants = len(expense.get("friend_links", []))

            values = [
                str(expense.get("id", "")),
                expense.get("description", ""),
                expense.get("date", ""),
                f"{expense.get('amount', 0):.2f} €",
                payer_name,
                str(num_participants)
            ]
            for col, value in enumerate(values):
                label = Gtk.Label(label=value, halign=Gtk.Align.START, hexpand=(col==1))
                label.add_css_class("table-cell")
                grid.attach(label, col, row_idx, 1, 1)

        wrapper = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        wrapper.set_margin_top(16)
        wrapper.append(grid)

        scrolled = Gtk.ScrolledWindow(vexpand=True)
        scrolled.set_child(wrapper)
        content.append(scrolled)

        close_btn = Gtk.Button(label="Cerrar")
        close_btn.connect("clicked", lambda b: dialog.destroy())
        close_btn.set_halign(Gtk.Align.END)
        content.append(close_btn)

        dialog.show()

    def show_expenses(self, expenses):
        self._expenses_data = expenses or []
        self.update_expenses_list()

    def show_error(self, message):
        dialog = Gtk.MessageDialog(
            transient_for=self.get_root(),
            modal=True,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.CLOSE,
            text=message
        )
        dialog.connect("response", lambda d, response_id: d.destroy())
        dialog.show()

    def show_status(self, message):
        dialog = Gtk.MessageDialog(
            transient_for=self.get_root(),
            modal=True,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text=message
        )
        dialog.connect("response", lambda d, response_id: d.destroy())
        dialog.show()