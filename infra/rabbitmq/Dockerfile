# CliniLink message broker: RabbitMQ with the CliniLink config and topology built in.
FROM rabbitmq:4.1-management

COPY --chown=rabbitmq:rabbitmq rabbitmq.conf /etc/rabbitmq/rabbitmq.conf
COPY --chown=rabbitmq:rabbitmq definitions.json /etc/rabbitmq/definitions.json

# 5672 = AMQP (services), 15672 = management UI and HTTP API
EXPOSE 5672 15672

HEALTHCHECK --interval=10s --timeout=5s --start-period=20s --retries=10 \
  CMD rabbitmq-diagnostics -q check_port_connectivity || exit 1
