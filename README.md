## Entorno virtual y ejecución local

El proyecto incluye un entorno virtual en la carpeta `venv`. Para usarlo:

1. **Crear el entorno** (si aún no existe):
   ```bash
   python -m venv venv
   ```

2. **Activar el entorno**:
   - Windows (PowerShell): `.\venv\Scripts\Activate.ps1`
   - Windows (CMD): `venv\Scripts\activate.bat`

3. **Instalar dependencias** (cierra antes cualquier terminal donde esté corriendo la app para evitar bloqueos):
   ```bash
   pip install -r requirements.txt
   ```

4. **Ejecutar la app**:
   ```bash
   streamlit run app.py
   ```

También puedes usar el script `run.bat` (Windows): hace todo lo anterior usando el Python del venv.

## Licencia

Este software está protegido por una licencia propietaria de uso exclusivo.  
Todos los derechos reservados © Iván Navarro.  
No se permite el uso, copia ni redistribución sin autorización expresa.  
Consulta el archivo [LICENSE](LICENSE) para más información.
