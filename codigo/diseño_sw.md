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
```mermaid
sequenceDiagram
    participant main as main.py
    participant app as SplitWithMeApp(Gtk.Application)
    participant window as MainWindow(Gtk.ApplicationWindow)
    participant api as ApiClient
    participant friendsView as FriendsView(Gtk.Box)
    participant expensesView as ExpensesView(Gtk.Box)
    participant friendsPresenter as FriendsPresenter
    participant expensesPresenter as ExpensesPresenter

    main ->> app: create SplitWithMeApp()
    main ->> app: run(sys.argv)

    note right of app: GTK inicializa y emite 'activate'

    app ->> app: do_activate()
    app ->> window: create MainWindow(self=app)
    window ->> window: Carga CSS
    window ->> api: create ApiClient()
    window ->> friendsView: create FriendsView(api)
    friendsView ->> friendsPresenter: create FriendsPresenter(self=friendsView, api_client=api)
    friendsView ->> friendsPresenter: load_friends()
    friendsPresenter ->> api: list_friends()
    api -->> friendsPresenter: lista_amigos
    friendsPresenter ->> friendsView: show_friends(lista_amigos)

    window ->> expensesView: create ExpensesView(api)
    expensesView ->> expensesPresenter: create ExpensesPresenter(self=expensesView, api_client=api)
    expensesView ->> expensesPresenter: load_expenses()
    expensesPresenter ->> api: list_expenses()
    api -->> expensesPresenter: lista_gastos
    expensesPresenter ->> expensesView: show_expenses(lista_gastos)
    expensesView ->> expensesPresenter: load_friends_for_selection()
    expensesPresenter ->> api: list_friends()
    api -->> expensesPresenter: lista_amigos_sel
    expensesPresenter ->> expensesView: populate_friend_selectors(lista_amigos_sel)


    window ->> window: Configura Stack (añade vistas)
    window ->> window: Conecta botones navegación a show_friends/show_expenses

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

    User ->> CreateDialog: Introduce Descripción, Fecha, Monto
    User ->> CreateDialog: Selecciona Pagador (ComboBox)
    User ->> CreateDialog: Marca Participantes (CheckButtons)
    User ->> CreateDialog: Clic en "Guardar"

    CreateDialog ->> ExpensesView: response(OK)
    ExpensesView ->> ExpensesView: on_create_dialog_response()
    ExpensesView ->> ExpensesView: Recoge datos del diálogo (desc, date, amount, payer_id, participant_ids)
    alt Validación en Vista OK
        ExpensesView ->> ExpensesPresenter: add_expense(desc, date, amount, payer_id, participants)
        ExpensesPresenter ->> ExpensesPresenter: Valida datos (requeridos, payer in participants, amount > 0)
        alt Validación Presenter OK
            ExpensesPresenter ->> ApiClient: create_expense(desc, date, amount, payer, participants)
            ApiClient -->> ExpensesPresenter: GastoCreado
            ExpensesPresenter ->> ExpensesView: show_status("Gasto añadido...")
            ExpensesPresenter ->> ExpensesPresenter: load_expenses()
            ExpensesPresenter ->> ApiClient: list_expenses()
            ApiClient -->> ExpensesPresenter: ListaGastosActualizada
            ExpensesPresenter ->> ExpensesView: show_expenses(ListaGastosActualizada)
            ExpensesPresenter ->> ExpensesView: close_create_dialog()
            ExpensesView ->> CreateDialog: destroy()
        else Validación Presenter Falla
            ExpensesPresenter ->> ExpensesView: show_error("Error en los datos...")
            note right of ExpensesView: Diálogo NO se cierra (should_close=False)
        end
    else Validación en Vista Falla (e.g., no seleccionó pagador)
        ExpensesView ->> ExpensesView: show_error("Error en el formulario...")
        note right of ExpensesView: Diálogo NO se cierra (should_close=False)
    end

    alt Error en llamada API
        ApiClient -->> ExpensesPresenter: Exception (ej: HTTPError)
        ExpensesPresenter ->> ExpensesPresenter: Extrae detalle del error
        ExpensesPresenter ->> ExpensesView: show_error("Error creando gasto: [detalle]")
        note right of ExpensesView: Diálogo NO se cierra (should_close=False)
    end

    alt Usuario Clic "Cancelar"
        CreateDialog ->> ExpensesView: response(CANCEL)
        ExpensesView ->> ExpensesView: on_create_dialog_response()
        ExpensesView ->> CreateDialog: destroy()
    end
``

