# ADR 0005: No extraer `identity_verification` a un servicio propio (todavía)

- **Estado**: Aceptado
- **Fecha**: 2026-10-18
- **Decisores**: Equipo LostVault
- **Relacionado**: [ADR 0001](0001-estilo-arquitectonico.md) (monolito modular),
  [ADR 0002](0002-integracion-reclamacion-api.md) (reclamación síncrona),
  [ADR 0003](0003-plataforma-despliegue-vercel.md) (Vercel),
  [Evidencia S11](../fallos-parciales/s11-fallos-parciales.md),
  [arc42 §11](../arc42/11_riesgos.md)

## Contexto

El [ADR 0001](0001-estilo-arquitectonico.md) dejó prevista esta revisión: si un
módulo necesita un ciclo de vida, escalamiento o equipo propio, se evalúa
extraerlo usando su carpeta `public/` como punto de corte.

De los seis módulos (`authentication`, `users`, `objects`, `search`, `claims`,
`identity_verification`), el candidato más fuerte es **`identity_verification`**:

- Maneja los datos más sensibles del sistema (foto con cédula y carné), sujetos
  a la Ley 1581 de 2012 ([arc42 §2](../arc42/02_restricciones.md)). Aislarlos en
  un servicio con su propio almacenamiento y permisos es un argumento real.
- Es el módulo que más probablemente cambie de implementación: hoy es un
  adaptador in-memory que solo valida que el id no esté vacío; una verificación
  documental real (procesar imágenes, quizá un proveedor externo) tendría
  latencias y dependencias distintas al resto.
- Ya tiene una frontera limpia: `IdentityVerificationService.verify(userId)` en
  `lib/features/identity_verification/public/`.

`search` se descartó como candidato en este ADR: su única presión diferente es
el p95 ≤ 2 s del Escenario 4, que hoy se cumple dentro de la misma función, y su
análisis de plataforma ya se hizo como ejercicio en el ADR 000.3.

La pregunta es si conviene extraer `identity_verification` **ahora**.

## Opciones evaluadas

### A. No extraer: mantenerlo como módulo del monolito (elegida)

Sigue en el mismo proceso y la misma función de Vercel. La verificación,
la creación de la reclamación y el marcado del objeto ocurren en una sola
operación atómica, como exige el [ADR 0002](0002-integracion-reclamacion-api.md).
Para preparar una extracción futura sin pagar su costo hoy, se mantiene la
regla de dependencia: `claims` solo usa `identity_verification/public`.

### B. Extraer como servicio síncrono (HTTP entre `claims` y verificación)

`claims` llamaría por red a un servicio de verificación antes de reservar el
objeto. Mantiene la respuesta inmediata al usuario, pero agrega a la operación
crítica una segunda llamada remota con **todos** los modos de fallo de la
[Evidencia S11](../fallos-parciales/s11-fallos-parciales.md) (no responde, responde
tarde, responde dos veces) multiplicados: timeout, reintentos, idempotencia y
circuit breaker también entre servicios. La disponibilidad de la reclamación pasa
a ser el producto de la disponibilidad de dos funciones.

### C. Extraer con saga orquestada (asíncrono)

`claims` reserva el objeto en estado `PENDING`, pide la verificación y compensa
(libera el objeto) si falla. El diseño está en la
[sección 4 de la Evidencia S11](../fallos-parciales/s11-fallos-parciales.md#4-hace-falta-una-saga).
Desacopla en el tiempo, pero introduce un estado intermedio visible para el
usuario y cambia la decisión del ADR 0002 de confirmar la reclamación de
inmediato.

## Criterios

| Criterio | A. No extraer | B. Servicio síncrono | C. Saga |
|---|---|---|---|
| **Necesidad de escalar distinto** | No hay: el tráfico es de curso/demostración ([ADR 0003](0003-plataforma-despliegue-vercel.md)). | No aporta hoy. | No aporta hoy. |
| **Ritmo de despliegue o equipo propio** | Un solo equipo de 4 personas a tiempo parcial ([arc42 §2](../arc42/02_restricciones.md)). | Dos pipelines y dos despliegues para el mismo equipo. | Igual que B, más el coordinador de la saga. |
| **Acoplamiento de datos** | La reclamación necesita verificar y reservar juntas; se resuelve con una transacción local. | Requiere coordinar datos entre dos procesos. | Requiere estado `PENDING` y compensación. |
| **Aislamiento de fallos** | Un fallo de la función afecta a todo (costo aceptado en ADR 0001). | Mejor aislamiento de la verificación, pero si cae, la reclamación tampoco funciona. | Mejor aislamiento; la reclamación queda pendiente en vez de fallar. |
| **Modos de fallo nuevos** | Ninguno. | F1–F5 de la Evidencia S11 aparecen también entre servicios. | Los mismos, más compensaciones fallidas y reclamaciones atascadas en `PENDING`. |
| **Protección de datos sensibles** | Depende de controles dentro del mismo proceso; hoy no se almacenan imágenes. | Mejor: almacenamiento y permisos propios. | Mejor, igual que B. |
| **Costo y operación** | Una función, sin costo adicional en el plan gratuito. | Segunda función, otro secreto, otros logs y métricas que hoy ya no acumulan ([arc42 §7](../arc42/07_vista_despliegue.md)). | Igual que B, más una cola o almacén para el estado de la saga. |
| **Precondición técnica** | Ninguna. | Sin base de datos, cada servicio seguiría con estado en memoria efímero. | Imposible de hacer bien sin persistencia: el estado de la saga se perdería entre invocaciones. |

## Decisión

**No se extrae `identity_verification` en este corte (opción A).**

El único criterio que favorece la extracción es la protección de datos
sensibles, y hoy no aplica en la práctica: el adaptador actual no recibe ni
guarda imágenes. Todos los demás criterios favorecen mantenerlo dentro: no hay
presión de escala, el equipo es uno solo, la operación de reclamar necesita
atomicidad, y extraer antes de tener persistencia obligaría a construir una saga
sobre estado que se pierde con cada instancia fría.

## Consecuencias

**Positivas**

- La reclamación sigue siendo una operación atómica con respuesta inmediata
  (ADR 0002), sin saga ni estado pendiente.
- Los modos de fallo a mitigar se quedan en una sola frontera (cliente ↔ API),
  ya cubierta por la idempotencia implementada en S11.
- Sin costo ni operación adicionales en Vercel.

**Costos aceptados**

- La verificación comparte proceso, credenciales y despliegue con el resto de la
  API; un fallo de la función afecta a todos los módulos.
- Cuando se implemente la verificación documental real, los datos sensibles
  vivirán en la misma aplicación; habrá que aplicar controles de acceso y cifrado
  dentro del monolito.

## Disparadores para revisar esta decisión

Se abre un ADR nuevo que reevalúe B o C si ocurre **cualquiera** de estos:

1. La verificación empieza a recibir y **almacenar imágenes de documentos** y la
   revisión de cumplimiento (Ley 1581) exige aislarlas de la base de datos general.
2. La verificación real tarda **más de 2 s en p95**, lo que rompería la respuesta
   inmediata de la reclamación y haría preferible el flujo asíncrono (opción C).
3. Otro equipo o sistema (por ejemplo, la oficina de objetos perdidos de la
   universidad) necesita **consumir la verificación** de forma independiente.
4. Ya existe **persistencia compartida** (PostgreSQL) y uno de los puntos
   anteriores se cumple; sin persistencia, la extracción no se considera.

Nota: integrar un **proveedor externo** de verificación no es por sí solo un
disparador. Se resuelve con un nuevo adaptador en
`identity_verification/infrastructure/` aplicando las mismas tácticas de la
Evidencia S11 (timeout, reintento con backoff, circuit breaker) dentro del
monolito.
