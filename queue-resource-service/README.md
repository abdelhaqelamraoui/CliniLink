# Queue & Resource Management Service (MS4)

Live waiting queues for doctors and facility resources (rooms, equipment, labs).
Python 3.12 · FastAPI · PostgreSQL · RabbitMQ (consumer) · Redis (real-time fan-out) · WebSocket.

## Responsibilities

- One queue per doctor per day, and one per resource per day
- Queue entries: WAITING, CALLED, IN_CONSULTATION, DONE, REMOVED
- Keep queues in sync with appointments, from RabbitMQ events (FR9)
- Show doctor queues (FR19) and resource queues (FR20)
- Call the next patient
- Push real-time updates over WebSocket to patients and waiting-room screens (FR21, NFR9)

## Run

With the rest of the platform (from the `CliniLink` folder):

```bash
docker compose -f infra/docker-compose.yml up -d --build
```

The service listens on http://localhost:8004. Swagger UI: http://localhost:8004/api/v1/queues/docs

The container runs the database migrations (`alembic upgrade head`) at start. With several
replicas, set `RUN_MIGRATIONS=false` and run the migration once (for example as a Kubernetes Job).

## Tests

18 tests run in Docker against a throwaway PostgreSQL. They cover migrations up and down,
duplicate and out-of-order events, rescheduling, dead-lettering, permissions, concurrent
call-next and the WebSocket push:

```bash
docker compose -f compose.test.yaml up --build --abort-on-container-exit --exit-code-from tests
docker compose -f compose.test.yaml down -v
```

## API (`/api/v1`)

All endpoints need `Authorization: Bearer <JWT>` (Keycloak). Errors use RFC 7807 Problem Details
with a `code` and `correlation_id`. `X-Correlation-ID` is read from the request, or generated.

| Method | Path | Who | Description |
|---|---|---|---|
| GET | `/queues/doctors/{doctor_id}?date=` | any user | Doctor queue for a day (default today) |
| GET | `/queues/resources/{resource_id}?date=` | any user | Resource queue for a day |
| GET | `/queues/me` | any user | The caller's own entries and positions, today and later |
| POST | `/queues/{queue_id}/call-next` | queue's doctor, staff | Calls the earliest waiting patient (`409 QUEUE_EMPTY` if none) |
| PATCH | `/queues/{queue_id}/entries/{entry_id}` | queue's doctor, staff | `{"status": "..."}`, allowed moves below |

What each caller sees: the queue's doctor and STAFF/ADMIN/SUPER_ADMIN get `patient_id` and
`appointment_id`. Patients get anonymized entries, with `is_mine: true` on their own.
A doctor is matched to a queue by token `sub` = `doctor_id`, and roles are read from `realm_access.roles`.

Manual status changes:

```
WAITING ──> CALLED ──> IN_CONSULTATION ──> DONE
   │          │  └──> WAITING (patient not there yet)
   └──────────┴─────> REMOVED
```

Positions: `0` = being served (CALLED / IN_CONSULTATION), then `1, 2, ...` by appointment time.
`estimated_time` is the appointment's scheduled time.

### WebSocket

```
ws://<host>/api/v1/ws/queues/doctors/{doctor_id}?date=YYYY-MM-DD
ws://<host>/api/v1/ws/queues/resources/{resource_id}?date=YYYY-MM-DD
```

No login is needed, and the data is always anonymized (for waiting-room screens). The client gets
the current snapshot on connect, then a new snapshot after every change. Changes go through Redis
pub/sub, so clients on any instance receive them.

### Health

- `GET /health/live`: the process is up (used by the Docker healthcheck)
- `GET /health/ready`: `503` if the database is down. `200` with `DEGRADED` if RabbitMQ or Redis is
  down: queues are still served, but may be stale until the broker comes back (report 4.3.4).

## Events consumed

From queue `queue-resource-service.appointment-events` (bound to `appointment.*` on
`clinilink.events`, see `infra/rabbitmq`). The envelope is the common one (report 6.5).

| Routing key | Effect |
|---|---|
| `appointment.booked` | Add a WAITING entry to the doctor's queue (and to the resource's queue if `resource_id` is set) |
| `appointment.rescheduled` | Move the entry to the new day / doctor / resource, or update its time |
| `appointment.cancelled`, `.auto_cancelled_late`, `.cancelled_doctor_absent`, `.no_show`, `.expired` | REMOVED |
| `appointment.checked_in` | Mark the entry as checked in |
| `appointment.completed` | DONE |
| anything else | Acknowledged and ignored |

`payload` expected for `booked` / `rescheduled`:

```json
{ "patient_id": "uuid", "doctor_id": "uuid", "appointment_date": "2026-11-10",
  "start_time": "10:00", "end_time": "10:30", "facility_id": "uuid?", "resource_id": "uuid?" }
```

Delivery guarantees:
- **Exactly-once effect:** the `event_id` is stored in the same transaction as the change, and the
  message is acked only after the commit. A redelivered event is ignored.
- **Out-of-order events:** the last `aggregate_version` per appointment is stored, and older events
  are ignored. A cancellation that arrives before its booking keeps the patient out of the queue.
- **Failures:** malformed messages go straight to the dead-letter queue. Processing errors are
  requeued with a backoff, and RabbitMQ dead-letters them after 3 attempts.
- **Concurrency:** call-next uses `SELECT ... FOR UPDATE SKIP LOCKED`, so two staff members
  calling at the same moment never call the same patient.

## Data (Queue DB, PostgreSQL)

| Table | Content |
|---|---|
| `queues` | type (DOCTOR/RESOURCE), owner_id (doctor or resource), facility_id, date; unique per owner and day |
| `queue_entries` | appointment, patient, scheduled time, status, check-in / call times |
| `appointment_versions` | last applied `aggregate_version` per appointment |
| `processed_events` | `event_id`s already applied |

Schema changes go through Alembic migrations in `migrations/versions/`.

## Configuration

| Variable | Default | Notes |
|---|---|---|
| `DATABASE_URL` | `postgresql+asyncpg://queue:queue@localhost:5432/queue_db` | |
| `RABBITMQ_URL` | `amqp://clinilink:clinilink@localhost:5672/clinilink` | |
| `RABBITMQ_QUEUE` | `queue-resource-service.appointment-events` | declared by the broker, not the service |
| `REDIS_URL` | empty | empty = in-process updates (single instance only) |
| `AUTH_JWKS_URL` | empty | Keycloak JWKS URL; turns on signature checks |
| `AUTH_ISSUER`, `AUTH_AUDIENCE` | empty | checked when set |
| `AUTH_ALLOW_UNVERIFIED` | `false` | dev only, accepts unsigned tokens (no Keycloak yet) |
| `TIMEZONE` | `Europe/Paris` | for "today" and `estimated_time` |
| `RUN_MIGRATIONS` | `true` | run `alembic upgrade head` at container start |

## Requirements

- FR9, FR19–FR21, NFR9
