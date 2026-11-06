# Infrastructure

Everything needed to run the platform.

- `docker-compose.yml`: local development (RabbitMQ for now; services, databases, Keycloak and Redis to be added)
- `rabbitmq/`: message broker config and topology (durable queues, dead-letter queues). See [rabbitmq/README.md](rabbitmq/README.md)
- Keycloak (authentication)
- Kubernetes manifests, one per service, plus the nightly database backup job
