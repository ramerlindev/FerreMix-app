@echo off
setlocal

:: Check if py launcher is available
py --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] No se encontro el lanzador 'py'.
    echo Por favor instala Python desde https://www.python.org/downloads/
    echo Asegurate de instalar el "Python Launcher" (marcado por defecto).
    pause
    exit /b 1
)

:: Create virtual environment if it doesn't exist
if not exist "venv" (
    echo [INFO] Creando entorno virtual con py...
    py -m venv venv
)

:: Activate virtual environment
call venv\Scripts\activate.bat

:: Upgrade pip using the python within venv (which is aliased to python after activation, but we can be safe)
python -m pip install --upgrade pip

:: Install dependencies
if exist "requirements.txt" (
    echo [INFO] Instalando dependencias...
    pip install -r requirements.txt
) else (
    echo [WARNING] No se encontro requirements.txt.
)

echo.
echo [SUCCESS] Entorno configurado correctamente.
echo.
echo Para iniciar el servidor, usa:
echo 1. venv\Scripts\activate
echo 2. flask run
echo.
echo O simplemente ejecuta: start_server.bat (si lo creas)
echo.
pause
