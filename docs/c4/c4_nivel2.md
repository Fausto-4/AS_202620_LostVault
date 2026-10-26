# C4 nivel 2 — Contenedores de LostVault

Diagrama como código (Mermaid, se ve directamente en GitHub). Es la versión
única del C4 nivel 2: reúne lo que ya mostraba el diagrama anterior (`C4 nivel
2.jpg`, retirado en S12) —dos interfaces, el encargado administrando objetos
desde la web y las notificaciones— y le agrega la estrategia de datos de la S12:
caché, base de datos según el ADR 0006 y el publicador de eventos.

Cada almacén de datos y el mecanismo de mensajería aparecen como **contenedores
propios**. Línea continua = existe hoy; línea punteada = decidido en un ADR,
pendiente de implementar.

```mermaid
flowchart TB
    student["👤 Estudiante<br/>Pierde o encuentra un objeto"]
    staff["👤 Encargado de oficina<br/>Administra y entrega objetos"]

    subgraph lostvault["LostVault (sistema)"]
        mobile["<b>Aplicación móvil</b><br/>[Flutter]<br/>UI para estudiantes:<br/>buscar, publicar y reclamar"]
        web["<b>Aplicación web</b><br/>[Flutter web]<br/>UI para encargados:<br/>administrar objetos entregados"]
        cdn[("<b>Caché HTTP</b><br/>[CDN de Vercel]<br/>Solo GET /objects<br/>s-maxage 30 s + SWR 60 s")]
        api["<b>API LostVault</b><br/>[FastAPI, función serverless en Vercel]<br/>Lógica de negocio: objects, search,<br/>claims, identity_verification"]
        db[("<b>Base de datos</b><br/>[PostgreSQL gestionado]<br/>objects, claims,<br/>idempotency_keys, users, outbox<br/><i>ADR 0006 — hoy: memoria del proceso</i>")]
        publisher["<b>Publicador de outbox</b><br/>[Trabajo programado, cada 15 min]<br/>Entrega eventos al menos una vez<br/><i>diseñado</i>"]
    end

    mail["Servicio de correo<br/>[Sistema externo]"]

    student -->|"Busca, publica y reclama (HTTPS)"| mobile
    staff -->|"Administra objetos (HTTPS)"| web
    mobile -->|"GET /objects (HTTPS/JSON)"| cdn
    web -->|"GET /objects (HTTPS/JSON)"| cdn
    cdn -->|"Fallo de caché o revalidación"| api
    mobile -->|"POST /v1/objects/{id}/claims<br/>(HTTPS/JSON, no-store)"| api
    web -->|"Gestión de objetos<br/>(HTTPS/JSON, no-store)"| api
    api -.->|"Transacción local: reclamar +<br/>clave de idempotencia + evento (SQL)"| db
    publisher -.->|"Lee eventos pendientes<br/>FOR UPDATE SKIP LOCKED (SQL)"| db
    publisher -.->|"ClaimCreated / ClaimRejected"| mail
    mail -.->|"Aviso de reclamación (email)"| staff

    classDef planned stroke-dasharray: 5 5
    class db,publisher,mail planned
```

| Contenedor | Tecnología | Estado | Decisión |
|---|---|---|---|
| Aplicación móvil | Flutter | Corre en local; adaptadores in-memory | [ADR 0001](../adr/0001-estilo-arquitectonico.md) |
| Aplicación web | Flutter web (mismo código base) | Corre en local (`flutter run -d chrome`); no publicada | [ADR 0001](../adr/0001-estilo-arquitectonico.md), [arc42 §7](../arc42/07_vista_despliegue.md) |
| Caché HTTP | CDN de Vercel (cabeceras `Cache-Control`) | Implementado en `backend/main.py` | [cache.md](../datos/cache.md) |
| API LostVault | FastAPI en Vercel | Desplegado | [ADR 0002](../adr/0002-integracion-reclamacion-api.md), [ADR 0003](../adr/0003-plataforma-despliegue-vercel.md) |
| Base de datos | PostgreSQL gestionado | Decidido, pendiente | [ADR 0006](../adr/0006-postgresql-fuente-de-verdad.md) |
| Publicador de outbox | Trabajo programado (GitHub Actions `schedule:` o Vercel Cron) | Diseñado | [eventos.md](../datos/eventos.md) |

Notas:

- Las dos aplicaciones comparten el mismo código Flutter; se muestran separadas
  porque atienden a usuarios y funciones distintas.
- Los endpoints de gestión de objetos para el encargado aún no existen en la API;
  hoy solo están `GET /objects` y la reclamación.
- **`api/` no es un contenedor.** Es una segunda implementación de la
  reclamación (FastAPI, `api/app/`) que no está desplegada ni se ejecuta en CI;
  el contenedor "API LostVault" corresponde a `backend/`. Si el equipo decide
  desplegar `api/`, debe aparecer aquí como contenedor propio. Ver R10 en
  [arc42 §11](../arc42/11_riesgos.md).
