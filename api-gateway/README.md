# API Gateway

Single public entry point. Clients reach the services only through the gateway.

- Routes requests to the microservices
- Validates JWT tokens (issued by Keycloak)
- Rate limiting
- Proxies WebSocket connections (live queues)
