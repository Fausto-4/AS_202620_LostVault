# Matriz Comparativa de Estilos Arquitectónicos — LostVault

## Estilos evaluados

### Arquitectura en capas
Se organiza el sistema en niveles jerárquicos (Presentación → Aplicación → Dominio → Infraestructura), donde cada capa solo se comunica con la adyacente.

**Ventajas:** simple de entender e implementar, apropiada para equipos pequeños, Bajo esfuerzo de configuración inicial.
**Desventajas:** riesgo de acoplamiento progresivo entre capas; los cambios en infraestructura pueden propagarse hacia el resto del sistema.

### Arquitectura hexagonal
Aísla el dominio (reglas de negocio) del resto del sistema mediante puertos y adaptadores, de forma que la lógica de negocio no dependa de tecnologías concretas.

**Ventajas:** alta testeabilidad, facilita sustituir mecanismos de persistencia o servicios externos.
**Desventajas:** mayor complejidad inicial, más interfaces y puertos que mantener; puede ser un esfuerzo excesivo para funcionalidades sencillas.

### Monolito modular
Mantiene la aplicación como una única unidad desplegable, pero organizada internamente en módulos independientes (Objects, Search, Claims, Identity Verification, Users).

**Ventajas:** despliegue sencillo, separación clara de funcionalidades, facilita el trabajo paralelo de un equipo pequeño, no introduce complejidad de sistemas distribuidos.
**Desventajas:** todos los módulos comparten la misma aplicación, o sea que un fallo grave de infraestructura puede afectarlos a todos, requiere disciplina para no romper los límites entre módulos.

## Tabla comparativa

| Criterio | Capas | Hexagonal | Monolito modular |
|---|---|---|---|
| Simplicidad | Alta | Media | Alta |
| Facilidad para equipo pequeño | Alta | Media | Alta |
| Separación de responsabilidades | Alta | Muy alta | Muy alta |
| Testabilidad | Alta | Muy alta | Muy alta |
| Facilidad de evolución | Media | Muy alta | Muy alta |
| Complejidad inicial | Baja | Alta | Media |
| Facilidad de despliegue | Alta | Media | Alta |
| Adecuación al plazo del semestre | Muy alta | Media | Muy alta |
| Adecuación a LostVault | Alta | Alta | **Muy alta** |

## Conclusión de la comparación

El monolito modular ofrece el mejor equilibrio entre simplicidad de despliegue y separación de responsabilidades, se ajusta a las restricciones reales del proyecto (equipo de 4 personas, infraestructura gratuita, plazo académico fijo).
La arquitectura hexagonal se aplicará de forma selectiva en los módulos con reglas de negocio críticas (como la verificación de identidad), sin adoptarla de forma completa en todo el sistema.

*Nota: la decisión final, con sus alternativas y consecuencias detalladas, se documenta en `docs/adr/0001-estilo-arquitectonico.md`.*
