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
