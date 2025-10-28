import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk
# Asegúrate de importar Presenter y GLib
from app.presenters.expenses_presenter import ExpensesPresenter
from gi.repository import GLib
# No necesitas importar threading aquí

class FriendCheckButton(Gtk.CheckButton):
    """Checkbox personalizado para almacenar el ID del amigo."""
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
        self._expenses_data = [] # Datos locales de gastos
        self.selected_expense = None # Gasto seleccionado para editar/ver

        self._friends_list_for_selection = [] # Cache local de amigos
        self.create_dialog = None # Referencia al diálogo de creación
        self.edit_dialog = None # Referencia al diálogo de edición

        titulo = Gtk.Label(label="Split - Gastos")
        titulo.add_css_class("section-title")
        self.append(titulo)

        # Contenedor para la lista de gastos
        self.expenses_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.expenses_box.add_css_class("friends-list") # Reutilizamos estilo

        # Scroll para la lista
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_child(self.expenses_box)
        scrolled.set_vexpand(True)
        self.append(scrolled)

        # Contenedor para botones inferiores
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

        # Spinner principal para feedback
        self.spinner = Gtk.Spinner(spinning=False)
        buttons_box.append(self.spinner)

        self.append(buttons_box)

        # Peticiones iniciales (asíncronas) al presentador
        self.presenter.load_expenses()
        self.presenter.load_friends_for_selection()

    def start_thinking(self):
        """Método llamado por el presentador para iniciar feedback principal."""
        if not self.spinner.get_spinning():
            self.spinner.start()
        self.añadir_gasto.set_sensitive(False)
        self.mostrar_lista_gastos.set_sensitive(False)
        # Podrías deshabilitar clics en la lista aquí

    def stop_thinking(self):
        """Método llamado por el presentador para detener feedback principal."""
        if self.spinner.get_spinning():
            self.spinner.stop()
        self.añadir_gasto.set_sensitive(True)
        self.mostrar_lista_gastos.set_sensitive(True)

    def start_thinking_dialog(self, dialog):
        """Método llamado por el presentador para iniciar feedback en un diálogo."""
        if dialog:
            # Podríamos añadir un spinner al diálogo o simplemente deshabilitar botones
            ok_button = dialog.get_widget_for_response(Gtk.ResponseType.OK)
            reject_button = dialog.get_widget_for_response(Gtk.ResponseType.REJECT) # Para delete
            if ok_button: ok_button.set_sensitive(False)
            if reject_button: reject_button.set_sensitive(False)
            # Considera añadir un spinner pequeño cerca de los botones del diálogo si prefieres

    def stop_thinking_dialog(self, dialog):
        """Método llamado por el presentador para detener feedback en un diálogo."""
        if dialog:
            ok_button = dialog.get_widget_for_response(Gtk.ResponseType.OK)
            reject_button = dialog.get_widget_for_response(Gtk.ResponseType.REJECT)
            if ok_button: ok_button.set_sensitive(True)
            if reject_button: reject_button.set_sensitive(True)

    def populate_friend_selectors(self, friends_list):
        """Método llamado por el presentador para actualizar la lista de amigos local."""
        self._friends_list_for_selection = friends_list or []
        # Si los diálogos estuvieran abiertos, habría que actualizar sus ComboBox/CheckButtons aquí
        # Pero como se crean cada vez, no es estrictamente necesario, usarán la lista actualizada.

    def on_create_expense_clicked(self, button):
        """Muestra el diálogo para crear un nuevo gasto."""
        if self.create_dialog: # Destruir si ya existe (poco probable)
            self.create_dialog.destroy()
            self.create_dialog = None

        self.create_dialog = Gtk.Dialog(title="Crear Nuevo Gasto", transient_for=self.get_root(), modal=True)
        self.create_dialog.set_default_size(400, 450)

        content_area = self.create_dialog.get_content_area()
        content_area.set_spacing(10)
        # Márgenes
        for margin in ["top", "bottom", "start", "end"]:
            getattr(content_area, f"set_margin_{margin}")(10)

        grid = Gtk.Grid(column_spacing=10, row_spacing=10, hexpand=True)

        # --- Campos del formulario ---
        desc_entry = Gtk.Entry(placeholder_text="Descripción", hexpand=True)
        date_entry = Gtk.Entry(placeholder_text="YYYY-MM-DD", hexpand=True) # Validar formato sería bueno
        amount_adj = Gtk.Adjustment(value=0.01, lower=0.01, upper=1000000, step_increment=0.1, page_increment=10)
        amount_entry = Gtk.SpinButton(adjustment=amount_adj, digits=2, hexpand=True)

        grid.attach(Gtk.Label(label="Descripción:", halign=Gtk.Align.START), 0, 0, 1, 1)
        grid.attach(desc_entry, 1, 0, 1, 1)
        grid.attach(Gtk.Label(label="Fecha:", halign=Gtk.Align.START), 0, 1, 1, 1)
        grid.attach(date_entry, 1, 1, 1, 1)
        grid.attach(Gtk.Label(label="Monto:", halign=Gtk.Align.START), 0, 2, 1, 1)
        grid.attach(amount_entry, 1, 2, 1, 1)

        # --- Selector de Pagador ---
        payer_combo = Gtk.ComboBoxText(hexpand=True)
        payer_combo.append("0", "Selecciona quién pagó...") # Opción por defecto inválida
        for friend in self._friends_list_for_selection:
            payer_combo.append(str(friend.get('id')), friend.get('name'))
        payer_combo.set_active(0) # Activar la opción por defecto
        grid.attach(Gtk.Label(label="Pagado por:", halign=Gtk.Align.START), 0, 3, 1, 1)
        grid.attach(payer_combo, 1, 3, 1, 1)

        # --- Selector de Participantes ---
        grid.attach(Gtk.Label(label="Participantes:", halign=Gtk.Align.START), 0, 4, 2, 1)
        scrolled_participants = Gtk.ScrolledWindow(height_request=150, hexpand=True, vexpand=True)
        scrolled_participants.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        participants_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        scrolled_participants.set_child(participants_box)

        for friend in self._friends_list_for_selection:
            # Usar nuestro CheckButton personalizado
            cb = FriendCheckButton(label=friend.get('name'), friend_id=friend.get('id'))
            participants_box.append(cb)

        grid.attach(scrolled_participants, 0, 5, 2, 1)
        content_area.append(grid)

        # --- Botones del diálogo ---
        self.create_dialog.add_button("Cancelar", Gtk.ResponseType.CANCEL)
        self.create_dialog.add_button("Guardar", Gtk.ResponseType.OK)

        # Conectar señal de respuesta
        self.create_dialog.connect("response", self.on_create_dialog_response, desc_entry, date_entry, amount_entry, payer_combo, participants_box)
        self.create_dialog.show()

    def on_create_dialog_response(self, dialog, response_id, desc_entry, date_entry, amount_entry, payer_combo, participants_box):
        """Manejador de respuesta del diálogo de creación."""
        if response_id == Gtk.ResponseType.OK:
            # Recoger datos y pasarlos al presentador (que validará y hará llamada async)
            try:
                description = desc_entry.get_text()
                date_str = date_entry.get_text()
                # El presentador convertirá a float y validará > 0
                amount_str = str(amount_entry.get_value())

                payer_id_str = payer_combo.get_active_id()
                # El presentador validará que no sea "0"
                payer_id = int(payer_id_str) if payer_id_str and payer_id_str != "0" else None

                participant_ids = []
                child = participants_box.get_first_child()
                while child:
                    if isinstance(child, FriendCheckButton) and child.get_active():
                        participant_ids.append(child.friend_id)
                    child = child.get_next_sibling()
                # El presentador validará que no esté vacía y que incluya al pagador

                # Llamar al presentador SIN try-except aquí para la llamada de red
                self.presenter.add_expense(description, date_str, amount_str, payer_id, participant_ids)
                # NO cerramos el diálogo aquí. El presentador lo hará si todo va bien.

            except ValueError:
                # Error SÍNCRONO (ej. int(payer_id_str) si es inválido)
                 self.show_error("Error: Revisa los datos del formulario (pagador).")
            except Exception as e:
                # Otro error síncrono inesperado
                 self.show_error(f"Error inesperado al preparar datos: {e}")

        elif response_id == Gtk.ResponseType.CANCEL:
            # Si cancela, sí cerramos directamente
            dialog.destroy()
            self.create_dialog = None

    def close_create_dialog(self):
        """Método llamado por el presentador para cerrar el diálogo."""
        if self.create_dialog:
            self.create_dialog.destroy()
            self.create_dialog = None

    def update_expenses_list(self):
        """Refresca la lista de gastos en la UI principal."""
        # Limpiar lista anterior
        child = self.expenses_box.get_first_child()
        while child:
            next_child = child.get_next_sibling()
            self.expenses_box.remove(child)
            child = next_child

        # Añadir filas nuevas
        if not self._expenses_data:
             info_label = Gtk.Label(label="No hay gastos para mostrar.", margin_top=20, margin_bottom=20)
             self.expenses_box.append(info_label)
        else:
            for expense in self._expenses_data:
                row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
                row.add_css_class("friend-row") # Reutilizar estilo
                # Márgenes
                for margin in ["top", "bottom", "start", "end"]:
                    val = 5 if margin in ["top", "bottom"] else 10
                    getattr(row, f"set_margin_{margin}")(val)

                payer_info = ""
                payer = expense.get("payer") # Esperamos un dict aquí según el modelo Read
                if payer and isinstance(payer, dict):
                     payer_info = f" (Pagó: {payer.get('name', '?')})"

                desc_text = expense.get("description", "") + payer_info
                desclabel = Gtk.Label(label=desc_text, hexpand=True, halign=Gtk.Align.START)
                amountlabel = Gtk.Label(label=f'{expense.get("amount", 0):.2f} €', halign=Gtk.Align.END)

                row.append(desclabel)
                row.append(amountlabel)

                # Gesto para seleccionar la fila
                gesture = Gtk.GestureClick.new()
                # Pasamos el diccionario completo del gasto al manejador
                gesture.connect("pressed", self.on_expense_selected, expense)
                row.add_controller(gesture)

                self.expenses_box.append(row)

    def on_expense_selected(self, gesture, n_press, x, y, expense):
        """Guarda el gasto seleccionado y muestra el diálogo de edición."""
        self.selected_expense = expense
        # print(f"DEBUG: Gasto seleccionado: {self.selected_expense}") # Para depurar
        self.show_edit_dialog()

    def show_edit_dialog(self):
        """Muestra el diálogo para editar el gasto seleccionado."""
        if not self.selected_expense:
            self.show_error("Error: No hay ningún gasto seleccionado.")
            return

        if self.edit_dialog: # Destruir si ya existe
            self.edit_dialog.destroy()
            self.edit_dialog = None

        self.edit_dialog = Gtk.Dialog(title="Editar Gasto", transient_for=self.get_root(), modal=True)
        self.edit_dialog.set_default_size(400, 450)

        content_area = self.edit_dialog.get_content_area()
        content_area.set_spacing(10)
        for margin in ["top", "bottom", "start", "end"]:
            getattr(content_area, f"set_margin_{margin}")(10)

        grid = Gtk.Grid(column_spacing=10, row_spacing=10, hexpand=True)

        # --- Campos precargados ---
        desc_entry = Gtk.Entry(hexpand=True, text=self.selected_expense.get("description", ""))
        date_entry = Gtk.Entry(hexpand=True, text=self.selected_expense.get("date", ""))
        amount_adj = Gtk.Adjustment(value=self.selected_expense.get("amount", 0.01), lower=0.01, upper=1000000, step_increment=0.1, page_increment=10)
        amount_entry = Gtk.SpinButton(adjustment=amount_adj, digits=2, hexpand=True)

        grid.attach(Gtk.Label(label="Descripción:", halign=Gtk.Align.START), 0, 0, 1, 1)
        grid.attach(desc_entry, 1, 0, 1, 1)
        # ... (resto de attach igual que en crear) ...
        grid.attach(Gtk.Label(label="Fecha:", halign=Gtk.Align.START), 0, 1, 1, 1)
        grid.attach(date_entry, 1, 1, 1, 1)
        grid.attach(Gtk.Label(label="Monto:", halign=Gtk.Align.START), 0, 2, 1, 1)
        grid.attach(amount_entry, 1, 2, 1, 1)

        # --- Selector de Pagador (precargado) ---
        payer_combo = Gtk.ComboBoxText(hexpand=True)
        payer_combo.append("0", "Selecciona quién pagó...")
        for friend in self._friends_list_for_selection:
            payer_combo.append(str(friend.get('id')), friend.get('name'))

        # Usar 'payer_id' del gasto seleccionado para activar
        payer_id_str = str(self.selected_expense.get("payer_id", "0"))
        # print(f"DEBUG: Payer ID a activar: {payer_id_str}") # Depuración
        payer_combo.set_active_id(payer_id_str)
        # Verificar si la activación funcionó (set_active_id puede fallar si el ID no existe)
        if payer_combo.get_active_id() != payer_id_str and payer_id_str != "0":
             print(f"WARN: No se pudo activar el pagador con ID {payer_id_str}")
             payer_combo.set_active(0) # Volver a la opción por defecto si falla

        grid.attach(Gtk.Label(label="Pagado por:", halign=Gtk.Align.START), 0, 3, 1, 1)
        grid.attach(payer_combo, 1, 3, 1, 1)

        # --- Selector de Participantes (precargado) ---
        grid.attach(Gtk.Label(label="Participantes:", halign=Gtk.Align.START), 0, 4, 2, 1)
        scrolled_participants = Gtk.ScrolledWindow(height_request=150, hexpand=True, vexpand=True)
        scrolled_participants.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        participants_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        scrolled_participants.set_child(participants_box)

        # Obtener IDs de participantes actuales del gasto seleccionado
        # Asumiendo que 'friend_links' es una lista de dicts con 'friend_id'
        participant_ids = {link.get('friend_id') for link in self.selected_expense.get("friend_links", []) if link.get('friend_id') is not None}
        # print(f"DEBUG: IDs participantes actuales: {participant_ids}") # Depuración

        for friend in self._friends_list_for_selection:
            cb = FriendCheckButton(label=friend.get('name'), friend_id=friend.get('id'))
            # Marcar si el amigo está en la lista de participantes
            if friend.get('id') in participant_ids:
                cb.set_active(True)
            participants_box.append(cb)

        grid.attach(scrolled_participants, 0, 5, 2, 1)
        content_area.append(grid)

        # --- Botones del diálogo de edición ---
        self.edit_dialog.add_button("Cancelar", Gtk.ResponseType.CANCEL)
        self.edit_dialog.add_button("Eliminar", Gtk.ResponseType.REJECT) # Usamos REJECT para eliminar
        self.edit_dialog.add_button("Guardar Cambios", Gtk.ResponseType.OK)

        self.edit_dialog.connect("response", self.on_edit_dialog_response, desc_entry, date_entry, amount_entry, payer_combo, participants_box)
        self.edit_dialog.show()

    def on_edit_dialog_response(self, dialog, response_id, desc_entry, date_entry, amount_entry, payer_combo, participants_box):
        """Manejador de respuesta del diálogo de edición."""
        expense_id = self.selected_expense.get("id") if self.selected_expense else None

        if response_id == Gtk.ResponseType.REJECT:
            if expense_id:
                # Confirmación antes de borrar sería ideal aquí
                # Por ahora, llamamos directamente al presentador (asíncrono)
                self.presenter.delete_expense(expense_id)
                # El presentador cerrará el diálogo
            else:
                 self.show_error("Error: No se puede eliminar un gasto no identificado.")

        elif response_id == Gtk.ResponseType.OK:
            if not expense_id:
                 self.show_error("Error: No se puede guardar un gasto no identificado.")
                 return # Salir si no hay ID

            # Recoger datos y pasarlos al presentador (que validará y hará llamada async)
            try:
                payer_id_str = payer_combo.get_active_id()
                # El presentador validará que no sea "0"
                payer_id = int(payer_id_str) if payer_id_str and payer_id_str != "0" else None

                participant_ids = []
                child = participants_box.get_first_child()
                while child:
                    if isinstance(child, FriendCheckButton) and child.get_active():
                        participant_ids.append(child.friend_id)
                    child = child.get_next_sibling()
                # El presentador validará participantes

                updated_data = {
                    "description": desc_entry.get_text(),
                    "date": date_entry.get_text(),
                    # El presentador convertirá y validará
                    "amount": amount_entry.get_value(),
                    "payer_id": payer_id,
                    "participant_ids": participant_ids
                }

                # Llamar al presentador SIN try-except para la llamada de red
                self.presenter.update_expense(expense_id, updated_data)
                # NO cerramos el diálogo aquí.

            except ValueError:
                self.show_error("Error: Revisa los datos del formulario (pagador).")
            except Exception as e:
                self.show_error(f"Error inesperado al preparar datos: {e}")

        elif response_id == Gtk.ResponseType.CANCEL:
            dialog.destroy()
            self.edit_dialog = None

    def close_edit_dialog(self):
        """Método llamado por el presentador para cerrar el diálogo."""
        if self.edit_dialog:
            self.edit_dialog.destroy()
            self.edit_dialog = None

    def on_show_list_clicked(self, button):
        """Muestra el diálogo con la lista detallada (acción síncrona)."""
        if not self._expenses_data:
            self.show_status("No hay gastos para mostrar en detalle.")
            return

        dialog = Gtk.Dialog(title="Split - Gastos - Lista Detallada", transient_for=self.get_root(), modal=True)
        dialog.set_default_size(700, 500)

        content = dialog.get_content_area()
        content.set_spacing(10)

        grid = Gtk.Grid(column_spacing=10, row_spacing=5)
        grid.add_css_class("expense-table") # Usar CSS para estilo de tabla

        # Cabeceras
        headers = ["ID", "Descripción", "Fecha", "Monto", "Pagador", "# Participantes"]
        for i, header in enumerate(headers):
            label = Gtk.Label(label=header, halign=Gtk.Align.START, hexpand=False)
            label.add_css_class("table-header")
            grid.attach(label, i, 0, 1, 1)

        # Filas de datos
        for row_idx, expense in enumerate(self._expenses_data, 1): # Empezar en fila 1
            payer_name = "?"
            payer = expense.get("payer") # Espera dict
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
                # Hacer descripción expandible
                is_desc = (col == 1)
                label = Gtk.Label(label=value, halign=Gtk.Align.START, hexpand=is_desc, ellipsize=3 if is_desc else 0) # EllipsizeMode.END
                label.add_css_class("table-cell")
                grid.attach(label, col, row_idx, 1, 1)

        # Poner la tabla en un Box para añadir margen superior
        wrapper = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        wrapper.set_margin_top(10) # Margen sobre la tabla
        wrapper.append(grid)

        # Añadir Scroll
        scrolled = Gtk.ScrolledWindow(vexpand=True, hexpand=True)
        scrolled.set_child(wrapper)
        content.append(scrolled)

        # Botón Cerrar
        close_btn = Gtk.Button(label="Cerrar")
        close_btn.connect("clicked", lambda b: dialog.destroy())
        close_btn.set_halign(Gtk.Align.END)
        content.append(close_btn)

        dialog.show()

    def show_expenses(self, expenses):
        """Método llamado por el presentador para actualizar la lista principal."""
        self._expenses_data = expenses or []
        self.update_expenses_list() # Llama al método que redibuja la lista

    def show_error(self, message):
        """Método llamado por el presentador para mostrar error general."""
        # Asegurarse de parar spinners
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
        """Método llamado por el presentador para mostrar mensaje informativo."""
        # Los spinners se paran en el finally del presentador
        dialog = Gtk.MessageDialog(
            transient_for=self.get_root(),
            modal=True,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text=message
        )
        dialog.connect("response", lambda d, response_id: d.destroy())
        dialog.show()