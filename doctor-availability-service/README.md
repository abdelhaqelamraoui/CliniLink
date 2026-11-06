# Doctor & Availability Service

Doctor profiles and their availability.

## Responsibilities

- Search doctors by name, location, specialty, price and rating
- Define and modify working hours (no overlapping slots)
- Set consultation prices
- Record absences
- Keep each doctor's average rating up to date

## Data

- Doctor DB: doctors, availabilities, absences

## Events

- Publishes: DoctorAbsenceRecorded
- Consumes: DoctorRated

## Requirements

- FR2, FR13–FR15, FR24
