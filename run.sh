#!/bin/bash

# Function to handle 'up' operation
up() {
    # Start docker-compose in detached mode
    docker-compose up --build -d

    # Wait for all containers to be up
    echo "Waiting for containers to be fully up..."
    while true; do
        if [ $(docker compose ps | grep "running" | wc -l) -eq $(docker compose config --services | wc -l) ]; then
            break
        fi
        sleep 1
    done

    echo "All containers are up. Storing and rotating audit logs into the reverse proxy..."
    while true; do
      # Store logs in bundle policy server to be behind the reverse proxy

      # Start docker logs in the background
      docker logs -f -t opa-llm-policy_agent-1 >& bundles/decision-log.txt &
      LOG_PID=$!

      # Rotate
      sleep 4
      kill $LOG_PID
    done
}

# Function to handle 'down' operation
down() {
    # Stop and remove containers, networks, images, and volumes
    docker compose down
}

# Function to handle 'clear' operation
clear() {
  rm -f bundles/decision-log.txt
}

# Check the first argument passed to the script
case "$1" in
    up)
        up # Call up function
        ;;
    down)
        down # Call down function
        ;;
    clear)
        clear # Call clear function
        ;;
    *)
        echo "Usage: $0 {up|down|clear}"
        exit 1
        ;;
esac
