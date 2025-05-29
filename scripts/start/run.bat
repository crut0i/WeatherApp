@echo off

if "%~1"=="" (
    echo Error: Please provide compose file path as argument
    echo Usage: %~nx0 ^<path_to_compose.yml^> --env-file ^<path_to_env_file^>
    exit /b 1
)

if "%~2"=="--env-file" (
    if "%~3"=="" (
        echo Error: Please provide path to env file
        echo Usage: %~nx0 ^<path_to_compose.yml^> --env-file ^<path_to_env_file^>
        exit /b 1
    )
    set "env_file=%~3"
) else (
    echo Error: Missing --env-file flag
    echo Usage: %~nx0 ^<path_to_compose.yml^> --env-file ^<path_to_env_file^>
    exit /b 1
)

docker-compose -f %~1 --env-file %env_file% -p "weather-app" up -d
