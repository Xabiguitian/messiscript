# Informe del Analista - Semana 2

## Evaluación del Equipo

- **Analista:** Xabier Guitián López

- **Evaluación Cuantitativa:**
    - Miguel Fraga: 5
    - Pedro Gómez: 5

- **Evaluación Cualitativa:**
    - **Miguel Fraga:** Ha participado activamente en la implementación de la gestión de errores y concurrencia, asegurando que las llamadas a la API no bloqueen la interfaz y que los errores se muestren adecuadamente al usuario. Ha cumplido con sus tareas a tiempo y con calidad.
    - **Pedro Gómez:** Contribuyó significativamente a la identificación de operaciones bloqueantes y a la refactorización del código para implementar la concurrencia. Su trabajo fue esencial para mejorar la respuesta de la aplicación y cumplió con los plazos establecidos.

---

## Retrospectiva de la Semana 2

a)  **¿Qué ha sido lo mejor de la práctica?**
    Ver cómo la aplicación ahora maneja mejor los tiempos de espera y los errores de conexión con el servidor. La interfaz se siente más fluida al no bloquearse durante las llamadas a la API.

b)  **¿Qué fue lo peor?**
    Entender los conceptos de concurrencia en GTK y cómo integrarlos correctamente con las llamadas `requests` sin causar problemas de hilos fue complejo. Depurar los errores relacionados con la concurrencia también llevó tiempo.

c)  **¿Cuál fue el mejor momento de cada semana durante el trabajo del equipo?**
    Cuando conseguimos implementar la primera operación concurrente correctamente y vimos que la interfaz seguía respondiendo mientras se cargaban los datos del servidor. Fue un gran avance.

d)  **¿Cuál ha sido el peor?**
    Los momentos de frustración al intentar solucionar errores intermitentes causados por la gestión incorrecta de hilos o callbacks desde hilos secundarios a la interfaz principal de GTK.

e)  **¿Qué has aprendido?**
    Hemos aprendido a identificar operaciones bloqueantes en una IGU, a implementar concurrencia usando hilos o tareas asíncronas en Python, y la importancia de manejar los errores de E/S para informar al usuario y ofrecer alternativas. También hemos reforzado el patrón MVP.

f)  **¿Qué necesitáis conservar -como equipo- para las próximas semanas?**
    La comunicación constante y la división clara de tareas que hemos mantenido. La paciencia para depurar problemas complejos también sigue siendo clave.

g)  **¿Qué tenéis que mejorar -como equipo- para las próximas semanas?**
    Podríamos mejorar en la planificación inicial de cómo abordar tareas complejas como la concurrencia, quizás investigando más a fondo las mejores prácticas antes de empezar a codificar.

h)  **¿Cómo se relaciona ESTE contenido con otros del curso y con tu titulación?**
    Este contenido se relaciona directamente con **Sistemas Operativos** (gestión de hilos y concurrencia), **Redes de Computadores** (manejo de peticiones HTTP y errores de red) y, por supuesto, con **Diseño Software** (aplicación de patrones arquitectónicos como MVP y principios de diseño robusto). Es fundamental para desarrollar aplicaciones de escritorio modernas y responsivas.