@echo off
cd /d %~dp0

:: Activate virtual environment
if exist "venv\Scripts\activate" (
    call venv\Scripts\activate
)

:: Run database migrations
echo Applying database migrations...
python manage.py migrate
if %errorlevel% neq 0 (
    echo Error applying migrations!
    pause
    exit /b 1
)

:: Check if service exists
sc query NeoPharmService >nul 2>&1
if %errorlevel% equ 1060 (
    echo Installing NeoPharm service...
    python windows_service.py install
    if %errorlevel% neq 0 (
        echo Failed to install service
        pause
        exit /b 1
    )
)

:: Start service
echo Starting NeoPharm service...
net start NeoPharmService
if %errorlevel% neq 0 (
    echo Failed to start service
    pause
    exit /b 1
)

echo Service started successfully
pause