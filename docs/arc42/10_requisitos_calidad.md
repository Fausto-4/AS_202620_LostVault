# 10. Requisitos de Calidad

## Árbol de utilidad

- **Utilidad**
  - **Disponibilidad**
    - Consulta accesible 24/7 → Escenario 1
    - Recuperación rápida ante caídas
  - **Usabilidad**
    - Publicación sin fricción → Escenario 2
    - Búsqueda intuitiva
  - **Seguridad**
    - Verificación de identidad en la entrega → Escenario 3
    - Prevención de accesos no autorizados
  - **Rendimiento**
    - Tiempo de respuesta en búsquedas → Escenario 4
    - Soporte a carga en horas pico

## Escenarios de calidad

## Escenario 1 — Disponibilidad
- **Fuente:** Estudiante
- **Estímulo:** Intenta consultar el estado de un objeto perdido fuera del horario de atención de la oficina física
- **Artefacto:** Módulo de consulta/búsqueda de LostVault
- **Entorno:** Operación normal, fuera de horario de oficina
- **Respuesta:** El sistema responde a la consulta sin intervención humana
- **Medida:** Disponibilidad del 99% mensual, con inactividad no programada menor a 7 horas/mes

## Escenario 2 — Usabilidad
- **Fuente:** Estudiante que usa la plataforma por primera vez
- **Estímulo:** Intenta publicar un objeto encontrado
- **Artefacto:** Formulario de publicación
- **Entorno:** Uso normal, sin capacitación previa
- **Respuesta:** El estudiante completa la publicación sin ayuda externa
- **Medida:** Al menos 90% de usuarios nuevos completan la publicación en menos de 3 minutos

## Escenario 3 — Seguridad
- **Fuente:** Usuario no autorizado
- **Estímulo:** Intenta reclamar un objeto que no le pertenece
- **Artefacto:** Módulo de verificación de identidad (foto cédula + carné)
- **Entorno:** Operación normal
- **Respuesta:** El sistema rechaza la entrega y marca el intento para revisión
- **Medida:** 100% de los intentos sin verificación válida son bloqueados automáticamente

## Escenario 4 — Rendimiento
- **Fuente:** Estudiante
- **Estímulo:** Realiza una búsqueda por palabra clave en hora pico
- **Artefacto:** Módulo de búsqueda
- **Entorno:** Carga pico, ~200 usuarios concurrentes
- **Respuesta:** El sistema retorna resultados de búsqueda
- **Medida:** 95% de las búsquedas responden en ≤ 2 segundos (p95) con 200 usuarios concurrentes
