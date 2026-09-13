# Tabla Módulo → Datos (Con único dueño)

| Módulo (dueño) | Dato que posee | Quién puede leerlo |
|---|---|---|
| authentication | Credenciales, estado de sesión, tokens | claims, objects |
| users | Perfil (nombre, carné, tipo de usuario) | authentication, identity_verification |
| objects | Objeto publicado (descripción, foto, estado) | search, claims |
| search | (no posee datos propios; solo consulta objects) | — |
| claims | Solicitud de reclamación (estado, reclamante, objeto) | *(nadie lee directamente; invoca comando en `objects.public` para actualizar estado)* |
| identity_verification | Evidencia y resultado de verificación | claims |

**Regla aplicada:** cada dato tiene un único módulo con permiso de escritura; los demás
solo leen a través del `public/` del módulo dueño, nunca acceden al almacenamiento interno.

**Verificación en código:** confirmado en `lib/features/claims/application/claim_object_use_case.dart`,
donde `claims` invoca `_objects.markAsClaimed(object.id)` a través de `objects/public/objects.dart`
en vez de acceder directamente al estado de `objects`.
