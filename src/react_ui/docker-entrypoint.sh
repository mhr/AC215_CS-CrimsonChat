#!/bin/sh

set -e

# Default PORT to 8080 if not set
PORT=${PORT:-9000}

# Substitute the PORT in the Nginx configuration template
envsubst '$PORT' < /etc/nginx/conf.d/default.conf.template > /etc/nginx/conf.d/default.conf

# Execute the CMD from the Dockerfile
exec "$@"
