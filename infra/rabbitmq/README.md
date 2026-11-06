# RabbitMQ

Message broker for asynchronous events between CliniLink services.
The whole topology is declared in `definitions.json` and loaded when the broker starts,
so services only connect, publish and consume. They do not declare exchanges or queues.

## Run

The broker is a Docker image (`clinilink/rabbitmq`) built from `Dockerfile`, with `rabbitmq.conf`
and `definitions.json` copied into it. It needs no files from the host.

```bash
# with compose (from the CliniLink folder)
docker compose -f infra/docker-compose.yml up -d --build rabbitmq

# or the image on its own
docker build -t clinilink/rabbitmq:1.0 infra/rabbitmq
docker run -d -p 5672:5672 -p 15672:15672 -v rabbitmq-data:/var/lib/rabbitmq clinilink/rabbitmq:1.0
```

After changing `rabbitmq.conf` or `definitions.json`, rebuild the image (`--build`).

- AMQP: `amqp://clinilink:clinilink@localhost:5672/clinilink`
- Management UI: http://localhost:15672 (user `clinilink`, password `clinilink`, dev only)

## Topology

| Exchange | Type | Purpose |
|---|---|---|
| `clinilink.events` | topic | All domain events |
| `clinilink.dlx` | direct | Dead-letter exchange for messages that keep failing |

### Routing keys (published to `clinilink.events`)

| Event | Publisher | Routing key |
|---|---|---|
| AppointmentEvent | appointment-service | `appointment.<type>`: `booked`, `rescheduled`, `cancelled`, `checked_in`, `completed`, `auto_cancelled_late`, `cancelled_doctor_absent` |
| DoctorAbsenceRecorded | doctor-availability-service | `doctor.absence.recorded` |
| DoctorRated | feedback-service | `doctor.rated` |
| User events (to be defined) | user-auth-service | `user.<type>` (no consumer yet) |

### Queues (one per consumer and event)

| Queue | Consumer | Binding |
|---|---|---|
| `appointment-service.doctor-absence` | appointment-service | `doctor.absence.recorded` |
| `notification-service.appointment-events` | notification-service | `appointment.*` |
| `notification-service.doctor-absence` | notification-service | `doctor.absence.recorded` |
| `queue-resource-service.appointment-events` | queue-resource-service | `appointment.*` |
| `doctor-availability-service.doctor-rated` | doctor-availability-service | `doctor.rated` |

Every service has its own queue, so each one gets its own copy of an event, and a slow or
stopped consumer does not affect the others. Messages wait in the queue until the service comes back.

## Reliability

- **Durable:** all queues are quorum queues (replicated, stored on disk). Publishers send
  persistent messages (`delivery_mode = 2`) and should use publisher confirms.
- **Retries and dead-letter queue:** a consumer acks a message only after processing it. A failed
  message is nacked and requeued. After 5 failed deliveries (`x-delivery-limit`) it moves through
  `clinilink.dlx` to `<queue>.dlq`, where it can be inspected and replayed from the management UI.
- **Idempotency:** a message can be delivered more than once, so every event carries an `eventId`
  and consumers ignore IDs they have already processed.

## Message format

JSON body, with `content_type = application/json`:

```json
{
  "eventId": "6f1c2a3e-...",
  "type": "appointment.booked",
  "occurredAt": "2026-11-06T09:30:00Z",
  "version": 1,
  "data": { "appointmentId": "...", "patientId": "...", "doctorId": "...", "start": "..." }
}
```

The `data` fields of each event are defined in `shared/`.

## Adding a consumer

Add a queue `<service>.<event>` with the same arguments as the existing ones, its `.dlq`,
a binding on `clinilink.events`, and a binding on `clinilink.dlx`, all in `definitions.json`.
Then rebuild the image (`docker compose up -d --build`). To load definitions again on an existing volume, remove the
volume (`docker compose down -v`) or import the file from the management UI.
