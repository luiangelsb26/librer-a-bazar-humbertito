# Humbertito IA

Sistema de gestión comercial para una librería bazar, desarrollado con Streamlit. Usa SQLite localmente y puede conectarse a PostgreSQL en Supabase.

## Ejecutar el proyecto

1. Crear y activar un entorno virtual.
2. Instalar las dependencias:

   ```powershell
   pip install -r requirements.txt
   ```

3. Crear la base de datos local (opcional, para trabajar sin Supabase):

   ```powershell
   python database.py
   ```

4. Iniciar la aplicación:

   ```powershell
   streamlit run app.py
   ```

La base de datos local se guarda en `data/humbertito.db` y no se sube al repositorio.

## Conectar Supabase

1. En tu organización de Supabase, crea un proyecto y espera a que termine de aprovisionarse.
2. En el proyecto, abre **Connect** y copia la URI de PostgreSQL del **Session pooler** para Streamlit Cloud. No publiques esa URI: contiene la contraseña de la base de datos.
3. Crea `.streamlit/secrets.toml` en este proyecto (ese archivo está excluido de Git) y agrega:

   ```toml
   SUPABASE_DB_URL = "postgresql://..."
   ```

4. Para cargar en el nuevo proyecto los datos de `data/humbertito.db`, ejecuta desde PowerShell, en la carpeta del proyecto:

   ```powershell
   .\venv\Scripts\python.exe .\migrate_to_supabase.py
   ```

   La migración conserva IDs, historial y usuarios, y solo escribe si las tablas remotas están vacías. No borra ni modifica el archivo SQLite local.
5. En Streamlit Community Cloud, abre la configuración de la app y añade la misma clave `SUPABASE_DB_URL` en **Secrets**. Al reiniciar la app, el login y las operaciones usarán Supabase. No configures la URI dentro de `app.py` ni la subas al repositorio.

Si no se configura `SUPABASE_DB_URL`, la app seguirá usando SQLite local.