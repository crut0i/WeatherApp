param(
    [Parameter(Mandatory=$true)]
    [string]$ComposeFilePath,
    
    [Parameter(Mandatory=$true)]
    [string]$EnvFilePath
)

if (-not (Test-Path $ComposeFilePath)) {
    Write-Error "Compose file not found at path: $ComposeFilePath"
    exit 1
}

if (-not (Test-Path $EnvFilePath)) {
    Write-Error "Environment file not found at path: $EnvFilePath"
    exit 1
}

docker-compose -f $ComposeFilePath --env-file $EnvFilePath -p "weather-app" up -d
