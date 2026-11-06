# Infrastructure

Everything needed to run the platform.

- docker-compose for local development (all services, databases, RabbitMQ, Keycloak, Redis)
- RabbitMQ (message broker: durable queues, dead-letter queue)
- Keycloak (authentication)
- Kubernetes manifests, one per service, plus the nightly database backup job
