import locale

def detect_locale():
    try: lang = (locale.getdefaultlocale()[0] or "").lower()
    except Exception: lang = ""
    code = lang.split("_")[0] if lang else ""
    return "es" if code == "es" else "en"

_active_locale = detect_locale()

def set_locale(locale_code):
    global _active_locale
    if locale_code in ("es", "en"):
        _active_locale = locale_code

def get_locale():
    return _active_locale

_TRANSLATIONS = \
    {
        "es":
        {
            "Welcome to SplitWithMe!": "¡Bienvenido a SplitWithMe!",
            "Split - Friends": "Split - Amigos",
            "Balance": "Saldo",
            "View Expenses": "Ver Gastos",
            "View Friends": "Ver Amigos",
            "Reload": "Recargar",
            "Paid by: ": "Pagado por: ",
            "Split - Expenses": "Split - Gastos",
            "Add Expense": "Añadir Gasto",
            "Show Detailed List": "Mostrar Lista Detallada",
            "Description": "Descripción",
            "Date": "Fecha",
            "Amount": "Cantidad",
            "Participants": "Participantes",
            "Cancel": "Cancelar",
            "Save Changes": "Guardar Cambios",
            "Error loagind expenses.": "Error al cargar los gastos.",
            "Error loading expense details.": "Error al cargar los detalles del gasto.",
            "Error loading friends for selection.": "Error al cargar amigos para la selección.",
            "All values are required, including payer and participants.": "Todos los valores son obligatorios, incluyendo el pagador y los participantes.",
            "Payer must be one of the participants.": "El pagador debe ser uno de los participantes.",
            "Amount must be a positive number.": "La cantidad debe ser un número positivo.",
            "Added expense successfully.": "Gasto añadido con éxito.",
            "Error in expense data.": "Error en los datos del gasto.",
            "Error loading expense.": "Error al cargar el gasto.",
            "Expense updated successfully.": "Gasto actualizado con éxito.",
            "Error updating expense.": "Error al actualizar el gasto.",
            "Expense deleted successfully.": "Gasto eliminado con éxito.",
            "Error deleting expense.": "Error al eliminar el gasto.",
            "Error loading friends.": "Error al cargar los amigos.",
            "Error loading friend details.": "Error al cargar los detalles del amigo.",
            "Currency": "€",
            "No participation in any expense.": "No hay participación en ningún gasto.",
            "Close": "Cerrar",
            "YYYY-MM-DD": "AAAA-MM-DD",
        },
        "en":
        {
            "Welcome to SplitWithMe!": "Welcome to SplitWithMe!",
            "Split - Friends": "Split - Friends",
            "Balance": "Balance",
            "View Expenses": "View Expenses",
            "View Friends": "View Friends",
            "Reload": "Reload",
            "Paid by: ": "Paid by: ",
            "Split - Expenses": "Split - Expenses",
            "Add Expense": "Add Expense",
            "Show Detailed List": "Show Detailed List",
            "Description": "Description",
            "Date": "Date",
            "Amount": "Amount",
            "Participants": "Participants",
            "Cancel": "Cancel",
            "Save Changes": "Save Changes",
            "Error loagind expenses.": "Error loading expenses.",
            "Error loading expense details.": "Error loading expense details.",
            "Error loading friends for selection.": "Error loading friends for selection.",
            "All values are required, including payer and participants.": "All values are required, including payer and participants.",
            "Payer must be one of the participants.": "Payer must be one of the participants.",
            "Amount must be a positive number.": "Amount must be a positive number.",
            "Added expense successfully.": "Added expense successfully.",
            "Error in expense data.": "Error in expense data.",
            "Error loading expense.": "Error loading expense.",
            "Expense updated successfully.": "Expense updated successfully.",
            "Error updating expense.": "Error updating expense.",
            "Expense deleted successfully.": "Expense deleted successfully.",
            "Error deleting expense.": "Error deleting expense.",
            "Error loading friends.": "Error loading friends.",
            "Error loading friend details.": "Error loading friend details.",
            "Currency": "$",
            "No participation in any expense.": "No participation in any expense.",
            "Close": "Close",
            "YYYY-MM-DD": "YYYY-MM-DD",
        }
    }

def t(key: str) -> str:  
    table = _TRANSLATIONS.get(_active_locale, {})
    if key in table:
        return table[key]
    return _TRANSLATIONS["en"].get(key, key)

def _(key: str) -> str: 
    return t(key)
