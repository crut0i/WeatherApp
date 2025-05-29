@echo off
setlocal enabledelayedexpansion

:: Function to clear cache
:clear_cache
echo [33mClearing cache...[0m

:: Removing .pyc & .pyo files
for /r %%f in (*.pyc *.pyo) do (
    echo %%f | findstr /i /v "\\.venv\\" >nul && del /f /q "%%f"
)

:: Removing __pycache__ dirs
for /r /d %%d in (__pycache__) do (
    echo %%d | findstr /i /v "\\.venv\\" >nul && rmdir /s /q "%%d"
)

:: Removing .pytest_cache dirs
for /r /d %%d in (.pytest_cache) do (
    echo %%d | findstr /i /v "\\.venv\\" >nul && rmdir /s /q "%%d"
)

:: Removing .ruff_cache dirs
for /r /d %%d in (.ruff_cache) do (
    echo %%d | findstr /i /v "\\.venv\\" >nul && rmdir /s /q "%%d"
)

:: Removing .mypy_cache dirs
for /r /d %%d in (.mypy_cache) do (
    echo %%d | findstr /i /v "\\.venv\\" >nul && rmdir /s /q "%%d"
)

echo [32mCache cleared successfully![0m
goto :eof

:: Check for -r flag
if "%1"=="-r" (
    echo [36mStarting continuous cache clearing (every 5 seconds). Press Ctrl+C to stop.[0m
    :loop
    call :clear_cache
    timeout /t 5 /nobreak >nul
    goto loop
) else (
    call :clear_cache
)
