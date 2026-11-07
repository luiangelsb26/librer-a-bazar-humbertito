# Desarrollo

## Verificación de tipos

La aplicación usa Python y Streamlit; Pyright revisa tipos estáticos sin cambiar
el modo de ejecución ni requerir una compilación previa.

Instala las dependencias de desarrollo y ejecuta el análisis desde la raíz:

```powershell
python -m pip install -r requirements-dev.txt
python -m pyright
```

La configuración actual cubre autenticación, acceso a datos, informes y
migraciones; `auth.py` y `database.py` se revisan en modo estricto. La interfaz
Streamlit y los módulos de análisis con Pandas/NumPy quedan fuera inicialmente;
se incorporarán conforme sus límites dinámicos reciban contratos de tipos y el
analizador pueda verificarlos sin ocultar errores. Al ampliar anotaciones o
corregir avisos, agrega esos módulos a `pyrightconfig.json`.

Las anotaciones y Pyright ayudan a detectar incompatibilidades antes de ejecutar
el código, pero no sustituyen la validación de datos en tiempo de ejecución.
