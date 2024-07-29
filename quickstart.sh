#!/bin/bash

REQUIREMENTS_FILE="requirements.txt"
pids=()

start_server() {
    local app_name=$1
    local port=$2
    uvicorn --app-dir ${app_name} app:app --reload --port $port &
    local pid=$!
    pids+=($pid)
    echo "Started $app_name on port $port with PID $pid"
}

cleanup() {
    echo "Stopping servers..."
    for pid in "${pids[@]}"; do
        kill $pid
    done
    wait
}

trap cleanup SIGINT

if [ -f "$REQUIREMENTS_FILE" ]; then
    echo "Installing requirements from $REQUIREMENTS_FILE"
    pip install -r "$REQUIREMENTS_FILE"
else
    echo "Requirements file $REQUIREMENTS_FILE not found, skipping installation."
fi

# kubectl delete configmap fastapi-config-f
# kubectl create configmap fastapi-config-f --from-file=facilitator/app.py
# kubectl delete -f facilitator/pod.yaml
# kubectl apply -f facilitator/pod.yaml

# kubectl port-forward svc/my-memgpt 8083:8083


start_server "webapp/session" 8002
start_server "webapp/be" 8001
start_server "webapp/fe" 8000

sleep 5

# if command -v google-chrome > /dev/null; then
#     open -a "Google Chrome" http://localhost:8000
# elif command -v safari > /dev/null; then
#     open -a "Safari" http://localhost:8000
# else
#     echo "No supported browser found. Please open http://localhost:8000 manually."
# fi

wait