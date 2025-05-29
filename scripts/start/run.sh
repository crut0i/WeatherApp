#!/bin/bash

if [ $# -lt 3 ]; then
    echo "Error: Please provide compose file path and env file path as arguments"
    echo "Usage: $0 <path_to_compose.yml> --env-file <path_to_env_file>"
    exit 1
fi

compose_file=$1
env_file=""

if [ "$2" == "--env-file" ]; then
    if [ -z "$3" ]; then
        echo "Error: Please provide path to env file"
        echo "Usage: $0 <path_to_compose.yml> --env-file <path_to_env_file>"
        exit 1
    fi
    env_file=$3
else
    echo "Error: Missing --env-file flag"
    echo "Usage: $0 <path_to_compose.yml> --env-file <path_to_env_file>"
    exit 1
fi

docker-compose -f "$compose_file" --env-file "$env_file" -p "weather-app" up -d
