# Casos de uso — SplitWithMe (Diseño IU actualizado)

## 1. Contexto y límites
- **Actor principal:** Persona usuaria (aplicación de escritorio, mono-usuario).
- **Límite del sistema:** Cliente que consume el servidor de la práctica conforme al swagger (Friends, Expenses y Friends↔Expenses solo **lectura** de participantes).
- **Fuera de alcance (otro equipo):** añadir/editar/borrar **amigos** y **participantes de un gasto**.

---

## 2. Lista de casos de uso
```
UC-01  Ver lista de gastos
UC-02  Crear gasto
UC-03  Editar gasto
UC-04  Eliminar gasto
UC-05  Ver detalle de un gasto (lectura de participantes y balances del gasto)
UC-06  Ver lista de amigos (lectura)
UC-07  Ver detalle de un amigo (gastos por amigo y balances por gasto)
UC-08  Ver balance general
UC-09  Buscar (local)
UC-10  Filtrar (local)
UC-11  Ordenar (local)
```

---

## 3. Detalle de casos de uso

### UC-01 — Ver lista de gastos
| Campo | Descripción |
|---|---|
| **Objetivo** | Consultar todos los gastos con `description`, `date (YYYY-MM-DD)`, `amount`, `num friends` y `total credit balance`. |
| **Precondiciones** | Conectividad disponible. |
| **Flujo principal** | 1) Solicitar la lista de gastos. 2) Mostrar lista scrolleable con los campos indicados y acceso al detalle. 3) Permitir orden/filtrado **local**. |
| **Alternativas/errores** | A1: Sin datos → estado “No hay gastos”. A2: Error/timeout → mensaje y acción “Reintentar”. |
| **Postcondición** | La lista queda visible y navegable. |
| **API (lectura)** | `GET /expenses` |

### UC-02 — Crear gasto
| Campo | Descripción |
|---|---|
| **Objetivo** | Registrar un nuevo gasto con `description`, `date`, `amount`. |
| **Precondiciones** | Datos válidos: `description` no vacía; `date` formato `YYYY-MM-DD`; `amount` numérico > 0. |
| **Flujo principal** | 1) Mostrar formulario. 2) Validar. 3) Crear el gasto. 4) Refrescar lista y/o abrir detalle. |
| **Alternativas/errores** | A1: Datos inválidos → validación y bloqueo. A2: Error servidor → mensaje + reintento/cancelar. |
| **Postcondición** | El nuevo gasto existe y es visible. |
| **API (creación)** | `POST /expenses` |

### UC-03 — Editar gasto
| Campo | Descripción |
|---|---|
| **Objetivo** | Modificar `description`, `date` o `amount` de un gasto existente. |
| **Precondiciones** | Gasto existente seleccionado; datos válidos. |
| **Flujo principal** | 1) Mostrar formulario precargado. 2) Validar cambios. 3) Guardar. 4) Refrescar vista. |
| **Alternativas/errores** | Validaciones como en UC-02; error servidor → mensaje + reintento. |
| **Postcondición** | Gasto actualizado y visible. |
| **API (actualización)** | `PUT /expenses/{expense_id}` |

### UC-04 — Eliminar gasto
| Campo | Descripción |
|---|---|
| **Objetivo** | Borrar un gasto existente. |
| **Precondiciones** | Gasto existente seleccionado; confirmación de la persona usuaria. |
| **Flujo principal** | 1) Confirmar borrado. 2) Eliminar. 3) Actualizar lista. |
| **Alternativas/errores** | Error/timeout → mensaje + reintento/cancelar. |
| **Postcondición** | El gasto deja de mostrarse. |
| **API (borrado)** | `DELETE /expenses/{expense_id}` |

### UC-05 — Ver detalle de un gasto (lectura de participantes)
| Campo | Descripción |
|---|---|
| **Objetivo** | Consultar participantes **ya asignados** a ese gasto y sus saldos: `credit balance` (ha pagado) y `debit balance` (debe), además del **balance total del gasto**. |
| **Precondiciones** | Gasto existente. |
| **Flujo principal** | 1) Mostrar resumen del gasto (`id`, `description`, `date`, `amount`, `total credit balance`). 2) Mostrar tabla de participantes con `name`, `credit balance`, `debit balance`. 3) Mostrar totales/reparto si aplica. |
| **Alternativas/errores** | A1: Sin participantes → mensaje informativo. A2: Error/timeout → mensaje + reintento. |
| **Postcondición** | Información visible; **sin** modificar participantes. |
| **API (lectura)** | `GET /expenses/{expense_id}` + `GET /expenses/{expense_id}/friends` |

### UC-06 — Ver lista de amigos (solo lectura)
| Campo | Descripción |
|---|---|
| **Objetivo** | Consultar todos los amigos con `id`, `name`, `total credit balance`, `total debit balance`. |
| **Precondiciones** | Conectividad disponible. |
| **Flujo principal** | 1) Solicitar la lista de amigos. 2) Mostrar lista con campos clave y acceso al detalle. 3) Permitir orden/filtrado **local**. |
| **Alternativas/errores** | Sin datos → estado vacío; error → mensaje + reintento. |
| **Postcondición** | Lista visible. |
| **API (lectura)** | `GET /friends` |

### UC-07 — Ver detalle de un amigo (solo lectura)
| Campo | Descripción |
|---|---|
| **Objetivo** | Consultar la ficha del amigo (`id`, `name`, totales) y la **lista de gastos** en los que participa con sus saldos por gasto (`credit/debit balance`, `num friends`, `amount`, `description`). |
| **Precondiciones** | Amigo existente. |
| **Flujo principal** | 1) Mostrar datos del amigo y su balance agregado (crédito/débito/neto). 2) Listar gastos en los que participa con su saldo por gasto. |
| **Alternativas/errores** | Sin gastos asociados → estado vacío; error → mensaje + reintento. |
| **Postcondición** | Información visible. |
| **API (lectura)** | `GET /friends/{friend_id}` + `GET /friends/{friend_id}/expenses` |

### UC-08 — Ver balance general
| Campo | Descripción |
|---|---|
| **Objetivo** | Visualizar, por amigo, `total credit balance`, `total debit balance` y **neto**. |
| **Precondiciones** | — |
| **Flujo principal** | 1) Agregar información por amigo. 2) Mostrar tabla/resumen con opción de orden (por neto o alfabético). |
| **Alternativas/errores** | Sin datos → estado vacío; error → mensaje + reintento. |
| **Postcondición** | Resumen global visible. |
| **API (lectura)** | `GET /friends` |

### UC-09 — Buscar (local)
| Campo | Descripción |
|---|---|
| **Objetivo** | Localizar rápidamente elementos en listas de amigos o gastos. |
| **Precondiciones** | Lista cargada. |
| **Flujo principal** | Introducir texto en un campo de búsqueda y mostrar coincidencias **localmente** (sin nuevas llamadas de red). |
| **Postcondición** | Resultados visibles; opción de limpiar la búsqueda. |

### UC-10 — Filtrar (local)
| Campo | Descripción |
|---|---|
| **Objetivo** | Reducir los elementos visibles en base a criterios (p. ej., por fecha, por importe, por número de participantes). |
| **Precondiciones** | Lista cargada. |
| **Flujo principal** | Seleccionar uno o varios criterios de filtro y aplicar **localmente** (sin nuevas llamadas de red). |
| **Postcondición** | Lista actualizada; opción de limpiar filtros. |

### UC-11 — Ordenar (local)
| Campo | Descripción |
|---|---|
| **Objetivo** | Cambiar el orden de visualización (p. ej., por fecha, por importe, alfabético, por neto en balances). |
| **Precondiciones** | Lista cargada. |
| **Flujo principal** | Seleccionar criterio/dirección de ordenación y aplicar **localmente**. |
| **Postcondición** | Lista reordenada; opción de revertir/alternar asc/desc. |
