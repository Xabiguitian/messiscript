# INTERFACES PERSONA-MÁQUINA
# Informe del Facilitador-Administrador - Semana 2

**Grupo:** Guns N' Roses
**Integrantes:**
* Pedro Gómez Osorio
* Miguel Fraga Pico
* Xabier Guitián Lopez

---

## 1. Resumen de Mejoras Funcionales

Durante esta semana, el equipo ha mejorado significativamente centrándose en completar y robustecer la gestión de gastos, así como en mejorar la información presentada al usuario, abordando aspectos clave de la Tarea 2.

---

## 2. Mejoras Implementadas Recientemente

* **Gestión Completa de Gastos:**
    * Ahora es posible **crear, editar y eliminar** gastos directamente desde la interfaz gráfica.
    * Al crear o editar un gasto, la aplicación permite especificar **quién realizó el pago** y **quiénes participaron** en él, seleccionándolos de la lista de amigos existentes. Esto hace que el registro de gastos sea mucho más preciso y útil para el reparto.
    * Se han añadido **validaciones** importantes para asegurar la coherencia de los datos, como verificar que quien paga también participe en el gasto y que los importes sean válidos.

* **Claridad en la Información:**
    * La lista principal de gastos ahora indica **quién pagó** cada uno, facilitando una visión rápida de la información clave.
    * En la vista de "Amigos", se muestra el **balance neto** (lo que ha pagado menos lo que le corresponde pagar) de cada amigo, ofreciendo una visión consolidada de su situación financiera.
    * Se ha añadido la posibilidad de ver un **desglose de los gastos** en los que participa cada amigo, mostrando su balance individual para cada gasto.

* **Robustez y Experiencia de Usuario:**
    * Se ha mejorado la forma en que la aplicación **comunica los errores** al usuario. Ahora, si ocurre un problema al interactuar con el servidor (ej: datos inválidos, error de conexión), se presenta un mensaje más descriptivo indicando la causa. Esto cumple con uno de los objetivos de la Tarea 2.
    * La aplicación confirma las acciones exitosas (crear, editar, eliminar gasto) mediante mensajes informativos.

---

## 3. Dinámica del Equipo y Facilitación

El equipo ha colaborado eficazmente para integrar estas nuevas funcionalidades, asegurando que los cambios en el modelo de datos y la lógica del servidor se reflejaran correctamente en la interfaz de usuario. La comunicación ha sido fluida y se han abordado los desafíos técnicos conjuntamente. Como facilitador, se comprobó el avance y se medió en la resolución de pequeñas dudas técnicas.

---

## 4. Estado General y Próximos Pasos (Desde Perspectiva Funcional)

La aplicación ahora permite una gestión de gastos mucho más completa y realista. Se ha mejorado la robustez frente a errores y la información presentada es más útil para el usuario.

Los siguientes pasos se centrarán en:
* Verificar que la aplicación siga siendo **responsiva** durante las operaciones de red (revisión de la concurrencia - Tarea 2).
* Comenzar la adaptación de la interfaz para **internacionalizarla** (Tarea 3).
* Realizar pruebas de usuario para asegurar que los nuevos flujos de creación/edición sean intuitivos.