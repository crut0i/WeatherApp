#!/bin/bash

# Function to clear cache
clear_cache() {
    echo -e "\033[33mClearing cache...\033[0m"
    
    # Removing .pyc & .pyo files
    find . -type f -name "*.pyc" -o -name "*.pyo" | grep -v ".venv" | xargs rm -f

    # Removing __pycache__ dirs
    find . -type d -name "__pycache__" | grep -v ".venv" | xargs rm -rf

    # Removing .pytest_cache dirs
    find . -type d -name ".pytest_cache" | grep -v ".venv" | xargs rm -rf

    # Removing .ruff_cache dirs
    find . -type d -name ".ruff_cache" | grep -v ".venv" | xargs rm -rf

    # Removing .mypy_cache dirs
    find . -type d -name ".mypy_cache" | grep -v ".venv" | xargs rm -rf

    echo -e "\033[32mCache cleared successfully!\033[0m"
}

# Check for -r flag
if [[ "$1" == "-r" ]]; then
    echo -e "\033[36mStarting continuous cache clearing (every 5 seconds). Press Ctrl+C to stop.\033[0m"
    trap 'echo -e "\n\033[33mStopping cache clearing...\033[0m"; exit' INT
    while true; do
        clear_cache
        sleep 5
    done
else
    clear_cache
fi
