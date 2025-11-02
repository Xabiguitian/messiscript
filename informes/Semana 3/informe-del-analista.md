# Informe del Analista - Semana 3

**Analista:** Pedro Gómez Osorio

## Evaluación del Equipo

- **Evaluación Cuantitativa:**
    - Xabier Guitián: 5
    - Miguel Fraga: 5

- **Evaluación Cualitativa:**
    - **Xabier Guitián (5/5):** Se encargó de corregir la **concurrencia** y la gestión de errores del servidor. Su implementación fue excelente y vital. Gracias a su trabajo, la aplicación ya no se bloquea al esperar datos de la red, lo que mejora la fluidez y la experiencia de usuario de forma notable.

    - **Miguel Fraga (5/5):** Lideró la corrección de la **internacionalización (i18n)**. Fue un trabajo meticuloso que adaptó toda la interfaz (botones, etiquetas, menús y errores) para que se muestre en inglés o español según el sistema, lo que da a la aplicación un acabado profesional.

Ambos han completado sus tareas con alta calidad y cumpliendo los plazos.

---

## Retrospectiva de la Semana

a) **¿Qué ha sido lo mejor de la práctica?**
   Ver el salto de calidad de la aplicación. Ahora es fluida (no se bloquea) y es bilingüe.

b) **¿Qué fue lo peor?**
   La complejidad técnica. Depurar la concurrencia (hilos) fue difícil, y refactorizar todos los textos de la UI para traducirlos fue un proceso muy repetitivo.

c) **¿Cuál fue el mejor momento de cada semana durante el trabajo del equipo?**
   El momento en que cambiamos el idioma del sistema operativo y vimos que la aplicación se tradujo perfectamente al instante.

d) **¿Cuál ha sido el peor?**
   Los intentos fallidos de actualizar la interfaz GTK desde un hilo secundario y los problemas iniciales para configurar `gettext`.

e) **¿Qué has aprendido?**
   Que la concurrencia y la internacionalización no son "extras", sino requisitos esenciales. Una UI que se bloquea parece rota, y una UI que no se traduce tiene un alcance limitado.

f) **¿Qué necesitáis conservar -como equipo- para las próximas semanas?**
   La confianza para dividir tareas complejas (concurrencia, i18n) y que cada miembro las resuelva de forma autónoma.

g) **¿Qué tenéis que mejorar -como equipo- para las próximas semanas?**
   Nuestro proceso de pruebas finales. Ahora que la aplicación es más compleja, debemos probar todos los flujos (errores, idiomas) antes de la entrega final.

h) **¿Cómo se relaciona ESTE contenido con otros del curso y con tu titulación?**
   Totalmente. Hemos aplicado conceptos de **Sistemas Operativos** (hilos/concurrencia), **Ingeniería de Software** (i18n, patrones) y **Redes** (gestión de errores HTTP).