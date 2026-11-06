# Appointment Service (core)

Books, reschedules and cancels appointments. This is the core service.

## Responsibilities

- Book an appointment atomically (no double booking, optimistic locking on time slots)
- Reschedule and cancel, following the scheduling rules (minimum notice)
- Appointment status: CONFIRMED, CHECKED_IN, COMPLETED, CANCELLED, AUTO_CANCELLED_LATE, CANCELLED_DOCTOR_ABSENT
- Patient history and a doctor's daily list
- Scheduled job that auto-cancels late appointments
- Cancel affected appointments when a doctor records an absence

## Data

- Appointments DB: appointments, time slots

## Events

- Publishes: AppointmentEvent
- Consumes: DoctorAbsenceRecorded

## Requirements

- FR4–FR12, FR16, FR24, NFR7
