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

_TRANSLATIONS =
    {
        "es":
        { # Ejemplos, luego los hay que completar
            "app_title": "SplitWithMe",
            "friends_section": "Amigos",
            "expenses_section": "Gastos",
        },
        "en":
        {
            "app_title": "SplitWithMe",
            "friends_section": "Friends",
            "expenses_section": "Expenses",
        }
    }

def t(key str) -> str:
    table = _TRANSLATIONS.get(_active_locale, {})
    if key in table:
        return table[key]
    return _TRANSLATIONS["en"].get(key, key)

def _(key:str) -> str:
    return t(key)
