#!/bin/sh

set -e

#REACT_APP_API_URL="http://35.237.221.78/api"
# Default PORT to 8080 if not set
PORT=${PORT:-3000}

# Substitute the PORT in the Nginx configuration template
envsubst '$PORT' < /etc/nginx/conf.d/default.conf.template > /etc/nginx/conf.d/default.conf

# Execute the CMD from the Dockerfile
exec "$@"
