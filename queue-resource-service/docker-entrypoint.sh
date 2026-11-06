#!/bin/sh
set -e

# Apply database migrations before starting. With several replicas (Kubernetes), set
# RUN_MIGRATIONS=false and run "alembic upgrade head" once as a Job instead.
if [ "${RUN_MIGRATIONS:-true}" = "true" ]; then
  echo "Applying database migrations..."
  alembic upgrade head
fi

exec "$@"
