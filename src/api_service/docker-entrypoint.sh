#!/bin/bash

# Default to port 8000 if not set
PORT=${PORT:-8080}

echo "Container is running!!!"

# Function to run the Uvicorn server in development mode
uvicorn_server() {
    uvicorn service:app --host 0.0.0.0 --port "$PORT" --log-level debug --reload --reload-dir ./ "$@"
}

# Function to run the Uvicorn server in production mode
uvicorn_server_production() {
    pipenv run uvicorn service:app --host 0.0.0.0 --port "$PORT" --lifespan on "$@"
}

# Export functions for use in interactive shell (optional)
export -f uvicorn_server
export -f uvicorn_server_production

export PATH="$PATH:/usr/local/bin"

echo -e "\033[92m
The following commands are available:
    uvicorn_server
        Run the Uvicorn Server (development mode)
    uvicorn_server_production
        Run the Uvicorn Server (production mode)
\033[0m
"

# Determine whether to run in development or production mode
if [ "${DEV}" = "1" ]; then
    echo "Starting in development mode..."
    pipenv run uvicorn service:app --host 0.0.0.0 --port "$PORT" --log-level debug --reload
else
    echo "Starting in production mode..."
    pipenv run uvicorn service:app --host 0.0.0.0 --port "$PORT" --lifespan on
fi