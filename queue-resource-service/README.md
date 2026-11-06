# Queue & Resource Management Service

Live waiting queues for doctors and resources.

## Responsibilities

- Doctor queues and resource queues
- Queue entries: WAITING, CALLED, IN_CONSULTATION, DONE, REMOVED
- Call the next patient
- Push real-time queue updates over WebSocket (patients, waiting-room screens)

## Data

- Queue DB: queues, queue entries (Redis for live state)

## Events

- Publishes: none
- Consumes: AppointmentEvent

## Requirements

- FR9, FR19–FR21, NFR9
