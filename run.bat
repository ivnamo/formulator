@echo off
cd /d "%~dp0"
if not exist "venv\Scripts\python.exe" (
    echo Creando entorno virtual...
    python -m venv venv
)
echo Instalando dependencias...
venv\Scripts\pip.exe install -r requirements.txt -q
if errorlevel 1 (
    echo Error al instalar. Cierra otras ventanas que usen esta carpeta y vuelve a ejecutar run.bat
    pause
    exit /b 1
)
echo Iniciando Streamlit...
venv\Scripts\python.exe -m streamlit run app.py
pause
