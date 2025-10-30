import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk
from app.presenters.expenses_presenter import ExpensesPresenter
from gi.repository import GLib

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

        titulo = Gtk.Label(label=_("Split - Expenses"))
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

        self.añadir_gasto = Gtk.Button(label=_("Add Expense"))
        self.añadir_gasto.add_css_class("action-button")
        self.añadir_gasto.connect("clicked", self.on_create_expense_clicked)

        self.mostrar_lista_gastos = Gtk.Button(label=_("Show Detailed List"))
        self.mostrar_lista_gastos.add_css_class("action-button")
        self.mostrar_lista_gastos.connect("clicked", self.on_show_list_clicked)

        buttons_box.append(self.añadir_gasto)
        buttons_box.append(self.mostrar_lista_gastos)

        self.spinner = Gtk.Spinner(spinning=False)
        buttons_box.append(self.spinner)

        self.append(buttons_box)

        self.presenter.load_expenses()
        self.presenter.load_friends_for_selection()

    def start_thinking(self):
        if not self.spinner.get_spinning():
            self.spinner.start()
        self.añadir_gasto.set_sensitive(False)
        self.mostrar_lista_gastos.set_sensitive(False)

    def stop_thinking(self):
        if self.spinner.get_spinning():
            self.spinner.stop()
        self.añadir_gasto.set_sensitive(True)
        self.mostrar_lista_gastos.set_sensitive(True)

    def start_thinking_dialog(self, dialog):
        if dialog:
            ok_button = dialog.get_widget_for_response(Gtk.ResponseType.OK)
            reject_button = dialog.get_widget_for_response(Gtk.ResponseType.REJECT)
            if ok_button: ok_button.set_sensitive(False)
            if reject_button: reject_button.set_sensitive(False)

    def stop_thinking_dialog(self, dialog):
        if dialog:
            ok_button = dialog.get_widget_for_response(Gtk.ResponseType.OK)
            reject_button = dialog.get_widget_for_response(Gtk.ResponseType.REJECT)
            if ok_button: ok_button.set_sensitive(True)
            if reject_button: reject_button.set_sensitive(True)

    def populate_friend_selectors(self, friends_list):
        self._friends_list_for_selection = friends_list or []

    def on_create_expense_clicked(self, button):
        if self.create_dialog:
            self.create_dialog.destroy()
            self.create_dialog = None

        self.create_dialog = Gtk.Dialog(title=_("Add Expense"), transient_for=self.get_root(), modal=True)
        self.create_dialog.set_default_size(400, 450)

        content_area = self.create_dialog.get_content_area()
        content_area.set_spacing(10)
        for margin in ["top", "bottom", "start", "end"]:
            getattr(content_area, f"set_margin_{margin}")(10)

        grid = Gtk.Grid(column_spacing=10, row_spacing=10, hexpand=True)

        desc_entry = Gtk.Entry(placeholder_text=_("Description"), hexpand=True)
        date_entry = Gtk.Entry(placeholder_text="YYYY-MM-DD", hexpand=True)
        amount_adj = Gtk.Adjustment(value=0.01, lower=0.01, upper=1000000, step_increment=0.1, page_increment=10)
        amount_entry = Gtk.SpinButton(adjustment=amount_adj, digits=2, hexpand=True)

        grid.attach(Gtk.Label(label=_("Description") + ":", halign=Gtk.Align.START), 0, 0, 1, 1)
        grid.attach(desc_entry, 1, 0, 1, 1)
        grid.attach(Gtk.Label(label=_("Date") + ":", halign=Gtk.Align.START), 0, 1, 1, 1)
        grid.attach(date_entry, 1, 1, 1, 1)
        grid.attach(Gtk.Label(label=_("Amount") + ":", halign=Gtk.Align.START), 0, 2, 1, 1)
        grid.attach(amount_entry, 1, 2, 1, 1)

        payer_combo = Gtk.ComboBoxText(hexpand=True)
        payer_combo.append("0", _("Select who paid..."))
        for friend in self._friends_list_for_selection:
            payer_combo.append(str(friend.get('id')), friend.get('name'))
        payer_combo.set_active(0)
        grid.attach(Gtk.Label(label=_("Paid by: "), halign=Gtk.Align.START), 0, 3, 1, 1)
        grid.attach(payer_combo, 1, 3, 1, 1)

        grid.attach(Gtk.Label(label=_("Participants") + ":", halign=Gtk.Align.START), 0, 4, 2, 1)
        scrolled_participants = Gtk.ScrolledWindow(height_request=150, hexpand=True, vexpand=True)
        scrolled_participants.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        participants_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        scrolled_participants.set_child(participants_box)

        for friend in self._friends_list_for_selection:
            cb = FriendCheckButton(label=friend.get('name'), friend_id=friend.get('id'))
            participants_box.append(cb)

        grid.attach(scrolled_participants, 0, 5, 2, 1)
        content_area.append(grid)

        self.create_dialog.add_button(_("Cancel"), Gtk.ResponseType.CANCEL)
        self.create_dialog.add_button(_("Save Changes"), Gtk.ResponseType.OK)

        self.create_dialog.connect("response", self.on_create_dialog_response, desc_entry, date_entry, amount_entry, payer_combo, participants_box)
        self.create_dialog.show()

    def on_create_dialog_response(self, dialog, response_id, desc_entry, date_entry, amount_entry, payer_combo, participants_box):
        if response_id == Gtk.ResponseType.OK:
            try:
                description = desc_entry.get_text()
                date_str = date_entry.get_text()
                amount_str = str(amount_entry.get_value())

                payer_id_str = payer_combo.get_active_id()
                payer_id = int(payer_id_str) if payer_id_str and payer_id_str != "0" else None

                participant_ids = []
                child = participants_box.get_first_child()
                while child:
                    if isinstance(child, FriendCheckButton) and child.get_active():
                        participant_ids.append(child.friend_id)
                    child = child.get_next_sibling()

                self.presenter.add_expense(description, date_str, amount_str, payer_id, participant_ids)

            except ValueError:
                self.show_error(_("Error in expense data."))
            except Exception as e:
                self.show_error(_(f"Unexpected error while preparing data: {e}"))

        elif response_id == Gtk.ResponseType.CANCEL:
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

        if not self._expenses_data:
            info_label = Gtk.Label(label=_("No expenses to show."), margin_top=20, margin_bottom=20)
            self.expenses_box.append(info_label)
        else:
            currency = _("Currency")
            paid_by_prefix = _("Paid by: ")

            for expense in self._expenses_data:
                row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
                row.add_css_class("friend-row")
                for margin in ["top", "bottom", "start", "end"]:
                    val = 5 if margin in ["top", "bottom"] else 10
                    getattr(row, f"set_margin_{margin}")(val)

                payer_info = ""
                payer = expense.get("payer")
                if payer and isinstance(payer, dict):
                    payer_info = f" ({paid_by_prefix}{payer.get('name', '?')})"

                desc_text = expense.get("description", "") + payer_info
                desclabel = Gtk.Label(label=desc_text, hexpand=True, halign=Gtk.Align.START)
                amountlabel = Gtk.Label(label=f'{expense.get("amount", 0):.2f} {currency}', halign=Gtk.Align.END)

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
            self.show_error(_("Error loading expense."))
            return

        if self.edit_dialog:
            self.edit_dialog.destroy()
            self.edit_dialog = None

        self.edit_dialog = Gtk.Dialog(title=_("Edit Expense"), transient_for=self.get_root(), modal=True)
        self.edit_dialog.set_default_size(400, 450)

        content_area = self.edit_dialog.get_content_area()
        content_area.set_spacing(10)
        for margin in ["top", "bottom", "start", "end"]:
            getattr(content_area, f"set_margin_{margin}")(10)

        grid = Gtk.Grid(column_spacing=10, row_spacing=10, hexpand=True)

        desc_entry = Gtk.Entry(hexpand=True, text=self.selected_expense.get("description", ""))
        date_entry = Gtk.Entry(hexpand=True, text=self.selected_expense.get("date", ""))
        amount_adj = Gtk.Adjustment(value=self.selected_expense.get("amount", 0.01), lower=0.01, upper=1000000, step_increment=0.1, page_increment=10)
        amount_entry = Gtk.SpinButton(adjustment=amount_adj, digits=2, hexpand=True)

        grid.attach(Gtk.Label(label=_("Description") + ":", halign=Gtk.Align.START), 0, 0, 1, 1)
        grid.attach(desc_entry, 1, 0, 1, 1)
        grid.attach(Gtk.Label(label=_("Date") + ":", halign=Gtk.Align.START), 0, 1, 1, 1)
        grid.attach(date_entry, 1, 1, 1, 1)
        grid.attach(Gtk.Label(label=_("Amount") + ":", halign=Gtk.Align.START), 0, 2, 1, 1)
        grid.attach(amount_entry, 1, 2, 1, 1)

        payer_combo = Gtk.ComboBoxText(hexpand=True)
        payer_combo.append("0", _("Select who paid..."))
        for friend in self._friends_list_for_selection:
            payer_combo.append(str(friend.get('id')), friend.get('name'))

        payer_id_str = str(self.selected_expense.get("payer_id", "0"))
        payer_combo.set_active_id(payer_id_str)
        if payer_combo.get_active_id() != payer_id_str and payer_id_str != "0":
            print(_(f"WARN: Could not activate payer with ID {payer_id_str}"))
            payer_combo.set_active(0)

        grid.attach(Gtk.Label(label=_("Paid by: "), halign=Gtk.Align.START), 0, 3, 1, 1)
        grid.attach(payer_combo, 1, 3, 1, 1)

        grid.attach(Gtk.Label(label=_("Participants") + ":", halign=Gtk.Align.START), 0, 4, 2, 1)
        scrolled_participants = Gtk.ScrolledWindow(height_request=150, hexpand=True, vexpand=True)
        scrolled_participants.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        participants_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        scrolled_participants.set_child(participants_box)

        participant_ids = {link.get('friend_id') for link in self.selected_expense.get("friend_links", []) if link.get('friend_id') is not None}

        for friend in self._friends_list_for_selection:
            cb = FriendCheckButton(label=friend.get('name'), friend_id=friend.get('id'))
            if friend.get('id') in participant_ids:
                cb.set_active(True)
            participants_box.append(cb)

        grid.attach(scrolled_participants, 0, 5, 2, 1)
        content_area.append(grid)

        self.edit_dialog.add_button(_("Cancel"), Gtk.ResponseType.CANCEL)
        self.edit_dialog.add_button(_("Delete"), Gtk.ResponseType.REJECT)
        self.edit_dialog.add_button(_("Save Changes"), Gtk.ResponseType.OK)

        self.edit_dialog.connect("response", self.on_edit_dialog_response, desc_entry, date_entry, amount_entry, payer_combo, participants_box)
        self.edit_dialog.show()

    def on_edit_dialog_response(self, dialog, response_id, desc_entry, date_entry, amount_entry, payer_combo, participants_box):
        expense_id = self.selected_expense.get("id") if self.selected_expense else None

        if response_id == Gtk.ResponseType.REJECT:
            if expense_id:
                self.presenter.delete_expense(expense_id)
            else:
                self.show_error(_("Error deleting expense."))

        elif response_id == Gtk.ResponseType.OK:
            if not expense_id:
                self.show_error(_("Error updating expense."))
                return

            try:
                payer_id_str = payer_combo.get_active_id()
                payer_id = int(payer_id_str) if payer_id_str and payer_id_str != "0" else None

                participant_ids = []
                child = participants_box.get_first_child()
                while child:
                    if isinstance(child, FriendCheckButton) and child.get_active():
                        participant_ids.append(child.friend_id)
                    child = child.get_next_sibling()

                updated_data = {
                    "description": desc_entry.get_text(),
                    "date": date_entry.get_text(),
                    "amount": amount_entry.get_value(),
                    "payer_id": payer_id,
                    "participant_ids": participant_ids
                }

                self.presenter.update_expense(expense_id, updated_data)

            except ValueError:
                self.show_error(_("Error in expense data."))
            except Exception as e:
                self.show_error(_(f"Unexpected error while preparing data: {e}"))

        elif response_id == Gtk.ResponseType.CANCEL:
            dialog.destroy()
            self.edit_dialog = None

    def close_edit_dialog(self):
        if self.edit_dialog:
            self.edit_dialog.destroy()
            self.edit_dialog = None

    def on_show_list_clicked(self, button):
        if not self._expenses_data:
            self.show_status(_("No expenses to show in detail."))
            return

        dialog = Gtk.Dialog(title=_("Split - Expenses - Detailed List"), transient_for=self.get_root(), modal=True)
        dialog.set_default_size(700, 500)

        content = dialog.get_content_area()
        content.set_spacing(10)

        grid = Gtk.Grid(column_spacing=10, row_spacing=5)
        grid.add_css_class("expense-table")

        headers = [_("ID"), _("Description"), _("Date"), _("Amount"), _("Payer"), _("# Participants")]
        for i, header in enumerate(headers):
            label = Gtk.Label(label=header, halign=Gtk.Align.START, hexpand=False)
            label.add_css_class("table-header")
            grid.attach(label, i, 0, 1, 1)

        currency = _("Currency")

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
                f"{expense.get('amount', 0):.2f} {currency}",
                payer_name,
                str(num_participants)
            ]
            for col, value in enumerate(values):
                is_desc = (col == 1)
                label = Gtk.Label(label=value, halign=Gtk.Align.START, hexpand=is_desc, ellipsize=3 if is_desc else 0)
                label.add_css_class("table-cell")
                grid.attach(label, col, row_idx, 1, 1)

        wrapper = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        wrapper.set_margin_top(10)
        wrapper.append(grid)

        scrolled = Gtk.ScrolledWindow(vexpand=True, hexpand=True)
        scrolled.set_child(wrapper)
        content.append(scrolled)

        close_btn = Gtk.Button(label=_("Close"))
        close_btn.connect("clicked", lambda b: dialog.destroy())
        close_btn.set_halign(Gtk.Align.END)
        content.append(close_btn)

        dialog.show()

    def show_expenses(self, expenses):
        self._expenses_data = expenses or []
        self.update_expenses_list()

    def show_error(self, message):
        self.stop_thinking()
        if self.create_dialog: self.stop_thinking_dialog(self.create_dialog)
        if self.edit_dialog: self.stop_thinking_dialog(self.edit_dialog)

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

try:
    from i18n import _
except ImportError:
    _ = lambda x: x
