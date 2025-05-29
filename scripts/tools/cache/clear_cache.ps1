param(
    [switch]$r
)

function Clear-Cache {
    Write-Host "Clearing cache..." -ForegroundColor Yellow
    
    # Removing .pyc & .pyo files
    Get-ChildItem -Path . -Recurse -Include *.pyc,*.pyo | 
        Where-Object { $_.FullName -notlike '*\.venv\*' } | 
        Remove-Item -Force

    # Removing __pycache__ dirs
    Get-ChildItem -Path . -Recurse -Directory -Filter "__pycache__" | 
        Where-Object { $_.FullName -notlike '*\.venv\*' } | 
        Remove-Item -Force -Recurse

    # Removing .pytest_cache dirs
    Get-ChildItem -Path . -Recurse -Directory -Filter ".pytest_cache" | 
        Where-Object { $_.FullName -notlike '*\.venv\*' } | 
        Remove-Item -Force -Recurse

    # Removing .ruff_cache dirs
    Get-ChildItem -Path . -Recurse -Directory -Filter ".ruff_cache" | 
        Where-Object { $_.FullName -notlike '*\.venv\*' } | 
        Remove-Item -Force -Recurse

    # Removing .mypy_cache dirs
    Get-ChildItem -Path . -Recurse -Directory -Filter ".mypy_cache" | 
        Where-Object { $_.FullName -notlike '*\.venv\*' } | 
        Remove-Item -Force -Recurse

    Write-Host "Cache cleared successfully!" -ForegroundColor Green
}

if ($r) {
    Write-Host "Starting continuous cache clearing (every 5 seconds). Press Ctrl+C to stop." -ForegroundColor Cyan
    try {
        while ($true) {
            Clear-Cache
            Start-Sleep -Seconds 5
        }
    }
    catch {
        Write-Host "`nStopping cache clearing..." -ForegroundColor Yellow
    }
}
else {
    Clear-Cache
}
