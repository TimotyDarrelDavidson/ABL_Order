#!/bin/bash

# Ensure RABBIT_HOST and RABBIT_PORT are set, providing defaults if not
RABBIT_HOST=${RABBIT_HOST:-rabbit}
RABBIT_PORT=${RABBIT_PORT:-5672}

# Ensure DB_HOST and DB_PORT are set, providing defaults if not
DB_HOST=${DB_HOST:-mysql}
DB_PORT=${DB_PORT:-3306} # Default MySQL port

# Wait for RabbitMQ to be available
echo "Waiting for RabbitMQ at ${RABBIT_HOST}:${RABBIT_PORT}..."
until nc -z "${RABBIT_HOST}" "${RABBIT_PORT}"; do
    echo "$(date) - still waiting for rabbitmq..."
    sleep 2
done
echo "RabbitMQ started."

# Wait for MySQL to be available
echo "Waiting for MySQL at ${DB_HOST}:${DB_PORT}..."
until nc -z "${DB_HOST}" "${DB_PORT}"; do
    echo "$(date) - still waiting for mysql..."
    sleep 2
done
echo "MySQL started."

# Run all Order-related services.
# The paths are relative to the WORKDIR in the Dockerfile (/var/nameko).
# Since your services are inside a nested 'orders' package,
# you reference them by their module path: 'orders.orderService', etc.
nameko run --config config.yml \
    orders.orderService \
    orders.orderDetailService \
    orders.orderPackageService