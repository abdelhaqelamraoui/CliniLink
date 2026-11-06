# User & Authentication Service

Manages user accounts, roles and permissions. Authentication is delegated to Keycloak.

## Responsibilities

- Register patients and doctors, create staff accounts
- Roles: PATIENT, DOCTOR, STAFF, ADMIN, SUPER_ADMIN
- Admin permissions (manage doctors, staff, resources), granted by the super administrator
- Role-based access control

## Data

- User DB: users, roles, permissions

## Events

- Publishes: user events (to be defined)
- Consumes: none

## Requirements

- FR1, FR25, FR26
