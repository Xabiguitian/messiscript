INTERFACES PERSONA-MÁQUINA
Informe del Facilitador-Administrador
Grupo Guns'Roses
Integrantes:
Pedro Gómez Osorio
Miguel Fraga Pico
Xabier Guitián Lopez

	1.	Resumen y alcance acordado
La práctica exige: definir el conjunto de casos de uso y el diseño de la interfaz; no incluir altas/ediciones/borrados de participantes (esa parte la desarrolla otro equipo); construir el diseño a partir de la práctica individual y la puesta en común; entregar “diseño-iu.pdf” (IU) y “diseño_sw.md” (diseño software en UML con Mermaid); implementar en Python con GTK 4, separando la aplicación en módulos según la arquitectura; usar el servidor de la asignatura; y crear scripts para poblar la BD con datos de prueba.

	2.	Registro de lo realizado esta semana
• Se ha definido el conjunto de casos de uso alineado con el swagger y con el alcance acordado (sin CRUD de participantes):
— UC-01 Ver lista de gastos.
— UC-02 Crear gasto (sale desde la lista de gastos).
— UC-03 Editar gasto (sale desde la lista de gastos).
— UC-04 Eliminar gasto (sale desde la lista de gastos).
— UC-05 Detalle de gasto (lectura de participantes y balances del gasto).
— UC-06 Lista de amigos (lectura).
— UC-07 Detalle de amigo (lectura).
— UC-08 Balance general.
— UC-09 Buscar (local).
— UC-10 Filtrar (local).
— UC-11 Ordenar (local).
• Se ha preparado un diagrama de relación entre casos de uso (Mermaid, flowchart) donde Crear/Editar/Eliminar dependen de Ver lista de gastos, tal como queda reflejado en el croquis consensuado por el equipo.
• Se ha consolidado un borrador de diseño de la IU: aplicación de escritorio con secciones “Gastos”, “Amigos” y “Balance”. En “Gastos” se visualiza la lista y, desde ella, se accede a crear, editar y eliminar. Los detalles de gasto muestran únicamente información de participantes y saldos (solo lectura). En “Amigos” se consulta listado y fichas (solo lectura). En “Balance” se ofrece un resumen por persona (crédito, débito, neto).
• Se ha generado una versión en texto de los casos de uso para integrarla en diseño-iu.pdf.
• Se ha avanzado un prototipo funcional de la interfaz (navegación y pantallas principales) con datos provisionales no conectados al servidor, útil para validar flujos y rótulos antes de la integración.

	3.	Asignación de responsables (acordado por el equipo)
• Pedro: responsable del diagrama (relación de casos de uso en Mermaid y coherencia de dependencias).
• Xabi y Miguel: responsables del resto de tareas de esta semana (conjunto de casos de uso, redacción para diseño-iu.pdf y preparación del prototipo de interfaz).

	4.	Estado de completud (estimación)
• Diseño de IU (casos de uso + diagrama): completado.
• Diseño SW (UML estático y dinámico): en curso (selección de patrón y esbozos; faltan diagramas finales).
• Prototipo de interfaz (pantallas y navegación): en curso (listas y vistas principales operativas a nivel de maqueta).
• Integración con servidor y datos de prueba: pendiente.

	5.	Patrón arquitectónico seleccionado y criterios
Se adopta MVP (Model-View-Presenter) por:
• Independencia real de la Vista respecto del estado/modelo: la vista solo muestra datos y emite eventos; la lógica y el estado viven fuera.
• Adecuación a una aplicación de escritorio con GTK 4 y Python, favoreciendo prueba de la lógica (Presenter) y sustitución de la vista.
• Encaje con los requisitos de modularidad y con el uso de un servidor externo para datos.

	6.	Diseño software previsto (alineado con MVP)
• Parte estática (UML, a describir en Mermaid en diseño_sw.md):
— Vistas (ventana principal y vistas de “Gastos”, “Amigos”, “Balance”) expresadas como interfaces de presentación.
— Presenters específicos por sección, responsables de orquestar cada caso de uso (carga de listas; crear/editar/eliminar gasto; cálculo y presentación de balances; búsqueda/filtrado/orden locales).
— Servicios de acceso al servidor (cliente HTTP y mapeo de datos) y modelos de dominio simples (Gasto, Amigo, Balance).
• Parte dinámica (UML, secuencias por UC clave):
— Ver lista de gastos: vista solicita → presenter recupera del servicio → presenter aplica orden/filtrado local → vista muestra.
— Crear/editar/eliminar gasto: vista confirma → presenter valida y solicita al servicio → presenter actualiza el estado → vista refresca.
— Detalle de gasto (solo lectura): vista solicita → presenter obtiene datos del gasto y de sus participantes (lectura) → vista muestra.
— Balance general: vista solicita → presenter agrega por persona a partir de la información disponible → vista muestra.
— Buscar/filtrar/ordenar: interacciones locales gestionadas por el presenter y reflejadas en la vista.

	7.	Próximos pasos y compromisos para la semana 2
• diseño-iu.pdf: compilar documento con casos de uso, diagrama, y capturas/anotaciones de la interfaz (incluyendo estados de carga/vacío/error como notas de diseño, no como casos de uso).
• diseño_sw.md: completar los diagramas UML en Mermaid (clases y secuencias) para cubrir todos los casos de uso definidos.
• Integración con el servidor: preparar la capa de acceso y conectar los flujos de “Gastos” y “Balances”.
• Búsqueda/filtrado/orden: consolidarlos como operaciones locales sobre las listas.
• Scripts de datos de prueba: preparar y ejecutar el seed mínimo (grupo de amigos, varios gastos y participaciones realistas) para validar la aplicación con el servidor de la asignatura.

8.-Estado general del repositorio (visión funcional)
Se cuenta ya con los artefactos clave para la entrega: casos de uso consolidados, diagrama de relación entre casos de uso que refleja las dependencias correctas, y un prototipo de interfaz navegable que materializa el diseño acordado. Resta incorporar los documentos finales (diseño-iu.pdf y diseño_sw.md) y avanzar en la integración con el servidor y en los scripts de datos de prueba.