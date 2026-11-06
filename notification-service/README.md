# Notification Service

Sends email and in-app notifications.

## Responsibilities

- Booking confirmations, appointment reminders, absence and change alerts
- Channels: email (through the email provider) and in-app
- Schedule reminders and retry failed sends

## Data

- Notification DB: notifications and their status (PENDING, SENT, FAILED)

## Events

- Publishes: none
- Consumes: AppointmentEvent, DoctorAbsenceRecorded

## Requirements

- FR22–FR24, NFR3
