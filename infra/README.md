# Infrastructure

Everything needed to run the platform.

- `docker-compose.yml`: local development. Today: RabbitMQ, Redis, and queue-resource-service with its PostgreSQL. Other services, their databases and Keycloak to be added
- `rabbitmq/`: message broker config and topology (durable queues, dead-letter queues). See [rabbitmq/README.md](rabbitmq/README.md)
- Keycloak (authentication)
- Kubernetes manifests, one per service, plus the nightly database backup job
