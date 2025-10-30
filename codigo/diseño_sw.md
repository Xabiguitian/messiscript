# Patron usado
Hemos usado el patrón MVP (Model-View-Presenter) para estructurar la aplicación.
# Diagramas
Diagrama de clases:
```mermaid
classDiagram
    direction LR
    class ApiClient {
        -str _base_url
        -float _timeout_s
        -Session _session
        +list_friends() List
        +get_friend(id) Dict
        +list_friend_expenses(id) List
        +list_expenses(query) List
        +get_expense(id) Dict
        +create_expense(desc, date, amount) Dict
        +update_expense(id, data) Dict
        +delete_expense(id) Dict
        +list_expense_friends(expense_id) List
        +add_friend_to_expense(expense_id, friend_id) Dict
        +close() void
    }

    class ExpensesPresenter {
        -ExpensesView view
        -ApiClient api_client
        +load_expenses(query) void
        +select_expense(expense_id) void
        +add_expense(desc, amount, date) void
        +update_expense(id, data) void
        +delete_expense(id) void
        +get_friends_not_in_expense(expense_id) List
        +add_friend_to_expense(expense_id, friend_id) void
    }

    class FriendsPresenter {
        -FriendsView view
        -ApiClient api
        +load_friends(query) void
        +select_friend(friend_id) void
    }

    class ExpensesView {
        +presenter: ExpensesPresenter
        -_expenses_data: list
        +selected_expense: dict
        -_current_detail_dialog: Gtk.Dialog
        -_current_detail_expense_id: int
        +show_expenses(expenses) void
        +update_expenses_list() void
        +on_create_expense_clicked(button) void
        +on_expense_selected(gesture, n, x, y, expense) void
        +refresh_expense_details() void
        +show_expense_detail_dialog(expense) void
        +on_add_friend_confirm(button, combo, expense_id) void
        +on_show_list_clicked(button) void
        +show_status(message) void
        +show_error(message) void
    }

     class FriendsView {
        +presenter: FriendsPresenter
        -_friends_data: list
        +selected_friend: dict
        +show_friends(friends) void
        +on_reload_clicked(button) void
        +show_friend_expenses(button, friend) void
        +show_error(message) void
    }

    class MainWindow {
     +api_client: ApiClient
     +friends_view: FriendsView
     +expenses_view: ExpensesView
     +stack: Gtk.Stack
     +show_friends(button) void
     +show_expenses(button) void
    }

    class SplitWithMeApp {
      +config: AppConfig
      +window: MainWindow
      +do_activate() void
    }

    class AppConfig {
      +api_base_url: str
      +request_timeout_s: float
      +load() AppConfig
    }


    SplitWithMeApp --> AppConfig : uses
    SplitWithMeApp --> MainWindow : creates/manages
    MainWindow o-- ApiClient
    MainWindow o-- FriendsView
    MainWindow o-- ExpensesView
    ExpensesView --> ExpensesPresenter : interactúa con
    FriendsView --> FriendsPresenter : interactúa con
    ExpensesPresenter --> ApiClient : usa
    FriendsPresenter --> ApiClient : usa
    ExpensesPresenter ..> ExpensesView : actualiza
    FriendsPresenter ..> FriendsView : actualiza
```

Diagrama de flujo dinamico:   crear gasto:

``` mermaid 
flowchart TD
    A[Usuario en ExpensesView] --> B{"Clic en Crear Gasto"}
    B --> C[ExpensesView.on_create_expense_clicked]
    C --> D["Muestra Diálogo Crear Nuevo Gasto"]
    D --> E["Usuario introduce Descripción e Importe"]
    E --> F{"Clic en Crear en Diálogo"}
    F --> G["ExpensesView maneja respuesta OK"]
    G --> H["Llama a ExpensesPresenter.add_expense(desc, amount_str)"]
    H --> I{"Presenter Valida Datos (desc!= '', amount>0)"}
    I -->|"Datos Válidos"| J["Presenter llama a ApiClient.create_expense con fecha por defecto"]
    J -->|"Éxito API"| K["Presenter llama a View.show_status"]
    K --> L["View muestra Gasto añadido..."]
    J -->|"Éxito API"| M["Presenter llama a Presenter.load_expenses"]
    M --> N["Presenter llama a ApiClient.list_expenses"]
    N -->|"Éxito API"| O["Presenter llama a View.show_expenses"]
    O --> P["View actualiza la lista principal"]
    I -->|"Datos Inválidos"| Q["Presenter llama a View.show_error"]
    Q --> R["View muestra Datos inválidos..."]
    J -->|"Error API"| S["Presenter extrae error detallado y llama a View.show_error"]
    S --> T["View muestra Error creando gasto... con detalle"]
    F -->|"Clic Cancelar"| U["Diálogo se cierra"]
    D -->|"Clic Cancelar"| U
```
Diagrama de flujo dinamico:
```mermaid
flowchart TD
    A[Usuario en ExpensesView] --> B{Selecciona Gasto};
    B --> C[ExpensesView.on_expense_selected];
    C --> D[View guarda Gasto y ID, llama a show_expense_detail_dialog];
    subgraph Preparar Diálogo
        D --> E[View llama a Presenter.get_friends_not_in_expense];
        E --> F[Presenter llama a ApiClient.list_friends];
        E --> G[Presenter llama a ApiClient.list_expense_friends];
        F & G -- Datos OK --> H[Presenter calcula amigos elegibles];
        H --> I[View recibe amigos elegibles];
        F -- Error API --> Err1[Presenter llama a View.show_error];
        G -- Error API --> Err1;
    end
    I --> J[Diálogo de Detalle se muestra con ComboBox poblado];
    J --> K[Usuario selecciona Amigo];
    K --> L{Clic en 'Añadir'};
    L --> M[View.on_add_friend_confirm];
    M --> N{Valida Selección};
    N -- Válido --> O[View llama a Presenter.add_friend_to_expense];
    O --> P[Presenter llama a ApiClient.add_friend_to_expense];
    subgraph Respuesta API Añadir Amigo
        P -- Éxito --> Q[Presenter llama a View.show_status];
        Q --> R[View muestra 'Amigo añadido...'];
        P -- Éxito --> S[Presenter llama a View.refresh_expense_details];
        S --> T{View verifica si diálogo está abierto};
        T -- Sí --> U[View pide datos actualizados a API];
        U -- Datos OK --> V[View cierra diálogo viejo];
        V --> W[View llama a show_expense_detail_dialog con datos nuevos];
        U -- Error API Refresh --> Err2[View cierra diálogo viejo y muestra error];
        T -- No --> X[Solo refresca lista principal];
        W --> X;
        P -- Error API --> Y[Presenter extrae error detallado y llama a View.show_error];
        Y --> Z[View muestra 'Error añadiendo amigo...' con detalle];
    end
    N -- Inválido --> AA[View llama a View.show_error];
    AA --> BB[View muestra 'Selecciona amigo...'];
```
``` mermaid
sequenceDiagram
    participant main as main.py
    participant app as SplitWithMeApp(Gtk.Application)
    participant i18n as I18n
    participant window as MainWindow(Gtk.ApplicationWindow)
    participant api as ApiClient
    participant friendsView as FriendsView
    participant expensesView as ExpensesView
    participant friendsPresenter as FriendsPresenter
    participant expensesPresenter as ExpensesPresenter

    main ->> app: create SplitWithMeApp()
    main ->> i18n: setup_i18n()
    main ->> app: run(sys.argv)

    note right of app: GTK inicializa y emite 'activate'

    app ->> app: do_activate()
    app ->> window: create MainWindow(self=app)
    window ->> api: create ApiClient()
    window ->> friendsView: create FriendsView(api)
    friendsView ->> friendsPresenter: create FriendsPresenter(self=friendsView, api_client=api)
    friendsView ->> friendsPresenter: load_friends()
    
    loop Carga Inicial Amigos
        friendsPresenter ->> api: list_friends()
        alt Éxito
            api -->> friendsPresenter: lista_amigos
            friendsPresenter ->> friendsView: show_friends(lista_amigos)
        else Error del Servidor (ej: 500)
            api -->> friendsPresenter: Lanza HTTPError
            friendsPresenter ->> friendsPresenter: Captura Excepción
            friendsPresenter ->> friendsView: show_error(_("Error al cargar amigos..."))
        end
    end

    window ->> expensesView: create ExpensesView(api)
    expensesView ->> expensesPresenter: create ExpensesPresenter(self=expensesView, api_client=api)
    expensesView ->> expensesPresenter: load_expenses()
    
    loop Carga Inicial Gastos
        expensesPresenter ->> api: list_expenses()
        alt Éxito
            api -->> expensesPresenter: lista_gastos
            expensesPresenter ->> expensesView: show_expenses(lista_gastos)
        else Error del Servidor
            api -->> expensesPresenter: Lanza HTTPError
            expensesPresenter ->> expensesPresenter: Captura Excepción
            expensesPresenter ->> expensesView: show_error(_("Error al cargar gastos..."))
        end
    end
    
    expensesView ->> expensesPresenter: load_friends_for_selection()
    
    app ->> window: present()
```
```mermaid
sequenceDiagram
    actor User as Usuario
    participant ExpensesView as ExpensesView
    participant CreateDialog as DialogoCrearGasto(Gtk.Dialog)
    participant ExpensesPresenter as ExpensesPresenter
    participant ApiClient as ApiClient

    User ->> ExpensesView: Clic en "Crear Gasto"
    ExpensesView ->> ExpensesView: on_create_expense_clicked()
    ExpensesView ->> CreateDialog: create()
    note right of ExpensesView: Pobla ComboBox Pagador y CheckButtons Participantes con _friends_list_for_selection
    ExpensesView ->> CreateDialog: show()

    User ->> CreateDialog: Introduce datos (Desc, Fecha, Monto)
    User ->> CreateDialog: Selecciona Pagador (Payer)
    User ->> CreateDialog: Marca Participantes
    User ->> CreateDialog: Clic en "Guardar"

    CreateDialog ->> ExpensesView: response(OK)
    ExpensesView ->> ExpensesView: on_create_dialog_response()
    ExpensesView ->> ExpensesView: Recoge datos (desc, date, amount, payer_id, participant_ids)
    
    alt Validación en Vista (Frontend) OK
        ExpensesView ->> ExpensesPresenter: add_expense(datos...)
        ExpensesPresenter ->> ExpensesPresenter: Valida datos (ej: payer_id in participant_ids, amount > 0)
        
        alt Validación Presenter OK
            ExpensesPresenter ->> ApiClient: create_expense(datos_api...)
            
            alt Éxito (Servidor responde 200/201)
                ApiClient -->> ExpensesPresenter: GastoCreado
                ExpensesPresenter ->> ExpensesView: show_status(_("Gasto añadido..."))
                ExpensesPresenter ->> ExpensesPresenter: load_expenses()
                ExpensesPresenter ->> ExpensesView: close_create_dialog()
                ExpensesView ->> CreateDialog: destroy()
            
            else Error del Servidor (ej: 422 Validación Backend o 500)
                ApiClient -->> ExpensesPresenter: Lanza HTTPError(response)
                ExpensesPresenter ->> ExpensesPresenter: Captura Excepción
                ExpensesPresenter ->> ExpensesPresenter: _(str(e)) (Traduce error)
                ExpensesPresenter ->> ExpensesView: show_error("Error API: [detalle del error]")
                note right of ExpensesView: Diálogo NO se cierra (should_close=False)
            end

        else Validación Presenter Falla (Lógica de negocio)
            ExpensesPresenter ->> ExpensesView: show_error(_("El pagador debe ser participante..."))
            note right of ExpensesView: Diálogo NO se cierra (should_close=False)
        end

    else Validación en Vista Falla (Datos básicos)
        ExpensesView ->> ExpensesView: show_error(_("Faltan campos obligatorios..."))
        note right of ExpensesView: Diálogo NO se cierra (should_close=False)
    end
```
```mermaid
classDiagram
    direction LR
    class ApiClient {
        -str _base_url
        -float _timeout_s
        -Session _session
        +list_friends() List
        +get_friend(id) Dict
        +list_friend_expenses(id) List
        +list_expenses(query) List
        +get_expense(id) Dict
        +create_expense(desc, date, amount, payer_id, participants) Dict
        +update_expense(id, data) Dict
        +delete_expense(id) Dict
        +close() void
    }

    class ExpensesPresenter {
        -ExpensesView view
        -ApiClient api_client
        -_friends: list
        +load_expenses(query) void
        +load_friends_for_selection() void
        +add_expense(desc, date, amount, payer, participants) void
        +update_expense(id, data) void
        +delete_expense(id) void
    }

    class FriendsPresenter {
        -FriendsView view
        -ApiClient api
        +load_friends(query) void
    }

    class ExpensesView {
        +presenter: ExpensesPresenter
        -_expenses_data: list
        -_friends_list_for_selection: list
        +selected_expense: dict
        +create_dialog: Gtk.Dialog
        +edit_dialog: Gtk.Dialog
        +populate_friend_selectors(friends) void
        +on_create_expense_clicked(button) void
        +on_create_dialog_response(...) void
        +on_expense_selected(...) void
        +show_edit_dialog() void
        +on_edit_dialog_response(...) void
        +show_expenses(expenses) void
        +show_status(message) void
        +show_error(message) void
    }

     class FriendsView {
        +presenter: FriendsPresenter
        -_friends_data: list
        +show_friends(friends) void
        +on_reload_clicked(button) void
        +show_friend_expenses_dialog(button, friend) void
        +show_error(message) void
    }

    class MainWindow {
     +api_client: ApiClient
     +friends_view: FriendsView
     +expenses_view: ExpensesView
     +stack: Gtk.Stack
     +show_friends(button) void
     +show_expenses(button) void
    }

    class SplitWithMeApp {
      +config: AppConfig
      +window: MainWindow
      +do_activate() void
    }

    class AppConfig {
      +api_base_url: str
      +request_timeout_s: float
      +load() AppConfig
    }

    class I18n {
      <<Module>>
      -_active_locale: str
      -_TRANSLATIONS: dict
      +setup_i18n() void
      +_(key) str
    }

    note "Flujo de Error del Servidor:\n1. ApiClient lanza HTTPError (ej: 404, 422, 500).\n2. El Presenter (Expenses/Friends) captura la excepción.\n3. El Presenter extrae el 'detail' del JSON de error.\n4. El Presenter llama a view.show_error(detalle) para notificar al usuario."

    SplitWithMeApp --> AppConfig : usa
    SplitWithMeApp --> MainWindow : crea/maneja
    SplitWithMeApp ..> I18n : setup
    MainWindow o-- ApiClient
    MainWindow o-- FriendsView
    MainWindow o-- ExpensesView
    ExpensesView --> ExpensesPresenter : interactúa con
    FriendsView --> FriendsPresenter : interactúa con
    ExpensesPresenter --> ApiClient : usa
    FriendsPresenter --> ApiClient : usa
    ExpensesPresenter ..> ExpensesView : actualiza / muestra errores
    FriendsPresenter ..> FriendsView : actualiza / muestra errores
    ExpensesPresenter ..> I18n : usa _()
    FriendsPresenter ..> I18n : usa _()
    ExpensesView ..> I18n : usa _()
```

