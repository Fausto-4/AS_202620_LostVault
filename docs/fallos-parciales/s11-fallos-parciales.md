# Evidencia S11 — Fallos parciales de la integración principal

## 1. Integración analizada

La integración principal de LostVault es la frontera HTTP definida en el
[ADR 0002](../adr/0002-integracion-reclamacion-api.md):

```text
Cliente (Flutter) ──HTTPS/JSON──▶ POST /v1/objects/{objectId}/claims ──▶ API FastAPI en Vercel (función serverless)
```

Es la operación que **cambia estado** (`available → claimed`) y la que tiene
mayor riesgo según el árbol de utilidad (Seguridad: impacto H / riesgo H, ver
[arc42 §10](../arc42/10_requisitos_calidad.md)). `GET /objects` es solo lectura:
si falla, basta con reintentar y no deja nada a medias, por eso no se analiza
aparte.

Contexto real que condiciona el análisis:

- El proveedor es `backend/main.py`, desplegado en Vercel
  ([ADR 0003](../adr/0003-plataforma-despliegue-vercel.md)). Las instancias
  frías aparecen con el tráfico espaciado del proyecto ([arc42 §7](../arc42/07_vista_despliegue.md)).
- El estado vive en memoria del proceso; no hay base de datos todavía.
- El cliente Flutter aún usa adaptadores in-memory (`lib/features/*/infrastructure/`);
  todavía no existe el adaptador HTTP que llame a la API. Por eso las tácticas
  del lado del cliente quedan **especificadas** aquí y marcadas como pendientes,
  y las del lado del proveedor quedan **implementadas y probadas**.

## 2. Tabla de modos de fallo

| # | Modo de fallo | Qué pasa hoy (sin mitigar) | Mitigación | Estado en el repo |
|---|---|---|---|---|
| F1 | **El otro lado no responde** (Vercel caído, red de la universidad sin salida) | La UI queda esperando sin límite; el estudiante no sabe si reclamó o no. | **Timeout explícito de 5 s** en el cliente (p95 objetivo 2 s + margen para arranque en frío). Al vencer, la UI muestra "No pudimos confirmar; reintenta" y **no** marca nada como reclamado. Errores de red/5xx se muestran distinto de `401/404/409/422`, como exige el ADR 0002. | Pendiente en cliente (no hay adaptador HTTP aún). Contrato y semántica listos. |
| F2 | **Responde tarde** (arranque en frío, latencia alta) | El cliente agota el timeout y reintenta, pero **el servidor sí alcanzó a crear la reclamación**. El reintento recibía `409 OBJECT_ALREADY_CLAIMED`: al dueño legítimo se le decía que otra persona se llevó su objeto. | **Operación idempotente** (sección 3): el cliente envía `Idempotency-Key` y la reusa en el reintento; el servidor devuelve la respuesta original (`201` + `Idempotent-Replayed: true`) sin crear otra reclamación. | **Implementado**: `backend/main.py` (`create_claim`), pruebas `test_retry_with_same_key_replays_original_201_without_duplicating`. |
| F3 | **Responde dos veces / llega dos veces** (doble toque en el botón, reintento automático del cliente, reenvío de un proxy) | Igual que F2: segunda petición → `409` al propio dueño; en un diseño menos cuidadoso, dos reclamaciones del mismo objeto. | **Deduplicación natural**: si el objeto ya está reclamado por *el mismo usuario*, se devuelve la reclamación existente con `200`, aunque no venga clave. Si es *otro* usuario, sigue siendo `409`. | **Implementado**: prueba `test_same_user_repeating_without_key_gets_200_not_409` y `test_idempotency_does_not_let_another_user_take_the_object`. |
| F4 | **Reintentos en avalancha** durante una caída | Si todos los clientes reintentan de inmediato y en bucle, prolongan la caída (y cada reintento despierta una instancia fría). | **Reintento con retroceso exponencial + jitter**: máximo 3 intentos (≈0,5 s, 1 s, 2 s ± aleatorio), **solo** ante timeout, error de red o 5xx; **nunca** ante `4xx`, que son respuestas de negocio definitivas. Siempre con la misma `Idempotency-Key`. | Pendiente en cliente. El servidor ya hace seguro el reintento (F2/F3). |
| F5 | **Fallo sostenido del proveedor** | Cada clic espera 5 s × 3 intentos = hasta ~15 s de espera inútil. | **Circuit breaker en el cliente**: tras 5 fallos técnicos seguidos se abre 30 s; mientras está abierto, la UI responde al instante "Servicio no disponible, intenta en unos minutos" sin llamar a la API; luego deja pasar una petición de prueba (semiabierto). | Pendiente en cliente. |
| F6 | **Dos instancias serverless a la vez** | El `threading.Lock` protege solo dentro de un proceso. Si Vercel atiende dos reclamaciones del mismo objeto en instancias distintas, cada una ve su propio `_objects` y ambas podrían responder `201`. Las claves de idempotencia tampoco se comparten. | **Persistencia compartida con restricción única**: `claims.object_id UNIQUE` y tabla `idempotency_keys (user_id, key) PRIMARY KEY` en PostgreSQL; la reserva del objeto y el registro de la clave en **la misma transacción local**. | **Riesgo aceptado y declarado** (R1 en [arc42 §11](../arc42/11_riesgos.md)). Dentro de un proceso sí está probado: `test_concurrent_claims_produce_exactly_one_201`. Depende de conectar PostgreSQL (pendiente ya anotado en `backend/main.py`). |
| F7 | **El reintento con clave reusada para otro objeto** (error del cliente) | Sin control, una clave podría devolver la reclamación de un objeto distinto al pedido. | La clave se asocia al `objectId`; reutilizarla para otro objeto → `422 IDEMPOTENCY_KEY_REUSED`, sin tocar el objeto. Clave vacía o > 255 caracteres → `400 INVALID_IDEMPOTENCY_KEY`. | **Implementado**: `test_key_reused_for_another_object_is_rejected`, `test_invalid_idempotency_key_is_400`. |

## 3. Diseño de la operación idempotente

### Regla

> Reclamar el mismo objeto, el mismo usuario, una o N veces, produce **una sola
> reclamación** y la misma respuesta de éxito.

### Mecanismo (dos capas)

1. **`Idempotency-Key` (explícita).** El cliente genera un UUID v4 cuando el
   estudiante pulsa "Reclamar" y lo envía en todos los reintentos de *esa*
   intención. El servidor guarda `(userId, key) → {objectId, respuesta, hora}`
   solo cuando la operación termina en `201`.
   - Se guarda únicamente el `201`: los `404/409/422` son deterministas y se
     recalculan; un `5xx` nunca se guarda para que el reintento sí vuelva a
     intentar (`test_failed_claim_is_not_cached_so_retry_can_succeed`).
   - La clave se acota por usuario: otro usuario con la misma clave no puede
     "heredar" una reclamación ajena.
   - Vigencia 24 h; las vencidas se purgan (`test_expired_key_is_purged`).
2. **Deduplicación natural (implícita).** Aunque no llegue clave (cliente
   antiguo, doble toque), si el objeto ya está reclamado por el mismo `userId`
   se responde `200` con la reclamación existente.

La comprobación y la escritura ocurren dentro del mismo `with _lock:`, así que
no hay ventana entre "verificar si existe" y "crear".

### Secuencia del caso F2 (responde tarde)

```text
Cliente                               API (Vercel)
  │ POST /claims  Idempotency-Key: K    │
  │────────────────────────────────────▶│ crea claim, objeto → claimed, guarda (user,K)
  │        (5 s sin respuesta: timeout) │── 201 se pierde / llega tarde ──X
  │ espera ~0,5 s (backoff + jitter)    │
  │ POST /claims  Idempotency-Key: K    │
  │────────────────────────────────────▶│ encuentra (user,K) → misma respuesta
  │◀──── 201 {..} Idempotent-Replayed ──│ (sin segunda reclamación)
  │ UI: "Reclamación confirmada"        │
```

### Cambios en el contrato

`docs/contracts/lostvault-api.yaml` agrega, de forma compatible hacia atrás:
cabecera opcional `Idempotency-Key`, cabecera de respuesta `Idempotent-Replayed`,
respuesta `200` (repetición del mismo usuario), `400 INVALID_IDEMPOTENCY_KEY` y el
código `IDEMPOTENCY_KEY_REUSED` en `422`. Ninguna respuesta existente cambia, por
eso `test/api_contract_test.dart` sigue pasando.

## 4. ¿Hace falta una saga?

**Hoy no.** La reclamación toca `claims`, `objects` e `identity_verification`,
pero los tres son módulos del mismo proceso (monolito modular, [ADR 0001](../adr/0001-estilo-arquitectonico.md)).
En el proveedor, "verificar + crear reclamación + marcar objeto" ocurre bajo el
mismo candado, y cuando exista PostgreSQL será **una transacción local**. Una
saga solo se justifica cuando los pasos viven en servicios con bases de datos
distintas.

**Sí haría falta si se extrae `identity_verification`** (la alternativa que
evalúa el [ADR 0005](../adr/0005-no-extraer-verificacion-identidad.md)). El diseño
sería una saga **orquestada** por `claims`, porque el flujo es corto, tiene un
dueño claro y el orden importa:

| Paso | Acción | Compensación si un paso posterior falla |
|---|---|---|
| 1 | `claims` reserva el objeto: `available → pending_verification` y crea la reclamación en estado `PENDING` | Liberar el objeto (`→ available`) y marcar la reclamación `CANCELLED` |
| 2 | `claims` pide la verificación al servicio de identidad (con `Idempotency-Key` = id de la reclamación) | — (la verificación no cambia estado del objeto) |
| 3a | Verificación válida → reclamación `VERIFIED`, objeto `claimed` | — (paso final) |
| 3b | Verificación inválida o sin respuesta tras el timeout y los reintentos → ejecutar la compensación del paso 1 | — |

Se descarta la coreografía (cada servicio reaccionando a eventos del otro)
porque con dos participantes no aporta desacople real y dispersa la lógica del
flujo, que hoy está en un solo lugar (`ClaimObjectUseCase`).

Coste visible para el usuario: aparece el estado intermedio "pendiente de
verificación" y la confirmación deja de ser inmediata, que es justo lo que el
ADR 0002 decidió evitar.

## 5. Patrón outbox: dónde aplicaría

Ninguna operación actual publica eventos, así que el outbox no se implementa.
Aplicará cuando se agreguen efectos secundarios (notificar a la oficina o al
estudiante, auditoría), que el ADR 0002 ya anticipa como asíncronos: la
reclamación y el registro `ClaimCreated` se escriben en la **misma transacción**
en una tabla `outbox`, y un proceso aparte lo publica después. Así no puede
quedar una reclamación sin notificación (o una notificación de algo que se
deshizo) si el envío falla justo después de guardar.

## 6. Cómo verificar

```bash
cd backend
JWT_SECRET=una-clave-de-prueba-de-32-caracteres pytest test_api.py -k "idempot or retry or same_user or concurrent or key"
```

El workflow `.github/workflows/backend.yml` ejecuta estas pruebas en cada push.
