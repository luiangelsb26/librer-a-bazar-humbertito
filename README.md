<div align="center">
  <img width="100%" alt="" src="https://capsule-render.vercel.app/api?type=waving&amp;height=105&amp;color=0:0C2944,100:087E8B&amp;section=header">
  <h1>Librería Bazar Humbertito</h1>
  <p>Sistema de gestión de inventario, compras y ventas con una interfaz adaptable en Next.js y operaciones en Python.</p>

![Next.js](https://img.shields.io/badge/Next.js-151515?style=for-the-badge&logo=nextdotjs&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-C73044?style=for-the-badge&logo=streamlit&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-175B7D?style=for-the-badge&logo=sqlite&logoColor=white)

</div>

<p align="center"><a href="#funcionalidades">Funcionalidades</a> · <a href="#cómo-se-usa">Cómo se usa</a> · <a href="#estructura-del-código">Estructura</a> · <a href="#ejecución-local">Ejecución local</a></p>

## Funcionalidades

| Área | Funciones |
| --- | --- |
| Inventario | Registrar y actualizar productos, consultar existencias y revisar alertas de stock. |
| Compras y ventas | Registrar movimientos y consultar su historial. |
| Archivos Excel | Descargar plantillas, validar e importar productos, compras y ventas. |
| Análisis | Consultar indicadores y analizar la demanda para apoyar la reposición. |
| Reportes y acceso | Generar reportes en PDF y administrar usuarios del sistema. |

## Cómo se usa

1. Registra los productos o cárgalos desde una plantilla de Excel.
2. Registra las compras y ventas y consulta el historial de movimientos.
3. Revisa las existencias y las alertas de stock para identificar productos que requieren reposición.
4. Consulta los indicadores y el pronóstico de demanda cuando el sistema disponga de historial de ventas.

## Estructura del código

| Archivo | Responsabilidad |
| --- | --- |
| [`app/`](app/) | Interfaz Next.js con panel, inventario, compras, ventas, análisis, pronóstico y administración. |
| [`api.py`](api.py) | API de Python (Starlette), autenticación por sesión y autorización por rol. |
| [`operaciones.py`](operaciones.py) | Operaciones compartidas de inventario, ventas, compras y Excel. |
| [`app.py`](app.py) | Interfaz Streamlit. |
| [`database.py`](database.py) y [`auth.py`](auth.py) | Persistencia SQLite o PostgreSQL, usuarios y contraseñas. |
| [`analysis.py`](analysis.py), [`prediction.py`](prediction.py) y [`pdf_report.py`](pdf_report.py) | Análisis comercial, pronóstico de demanda e informe PDF. |

## Ejecución local

Estos pasos son para **Windows con PowerShell**. Necesitas **Git**, **Python 3.14** y **Node.js 20.9 o superior**. Ejecuta los comandos desde la raíz del proyecto.

### 1. Descarga e instala

Si aún no tienes el repositorio:

```powershell
git clone https://github.com/luiangelsb26/librer-a-bazar-humbertito.git
cd librer-a-bazar-humbertito
```

Si ya tienes una copia, abre su carpeta y ejecuta `git pull --ff-only origin main` para traer la última versión.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt -r requirements-web.txt
npm.cmd ci
```

### 2. Configura la base de datos y el acceso

La API usa **SQLite** por defecto y guarda los datos en `data/humbertito.db`. Si tu instalación usa **Supabase**, configura `SUPABASE_DB_URL` o `DATABASE_URL` en esta terminal antes de crear una cuenta o iniciar la API. Usa la URL de conexión de PostgreSQL que ya utiliza el proyecto. La API lee la variable del entorno. Si tienes la conexión guardada en los secretos de Streamlit, debes configurar también la variable para Next.js y su API.

Para una base de datos nueva, crea la primera cuenta administradora:

```powershell
.\.venv\Scripts\python.exe -m api crear-admin
```

Si la base ya tiene usuarios, inicia sesión con tu cuenta existente.

### 3. Inicia la API en la primera terminal

```powershell
$env:HUMBERTITO_SESSION_SECRET = .\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_hex(32))"
.\.venv\Scripts\python.exe -m uvicorn api:create_app --factory --host 127.0.0.1 --port 8000
```

Deja esta terminal abierta. El secreto se genera para esta sesión de PowerShell. Si generas uno nuevo, tendrás que volver a iniciar sesión.

### 4. Inicia Next.js en la segunda terminal

Abre otra terminal en la raíz del proyecto y ejecuta:

```powershell
npm.cmd run dev -- --hostname 127.0.0.1 --port 3000
```

Abre [Humbertito en el navegador](http://127.0.0.1:3000) e inicia sesión. Next.js envía las solicitudes de `/api` al puerto `8000`. Si la pantalla muestra un error de conexión, comprueba que la primera terminal siga ejecutando la API. Para detener el sistema, pulsa **Ctrl+C** en ambas terminales.

### Compilación e interfaz Streamlit

Para usar la compilación de Next.js, mantén la API activa y ejecuta `npm.cmd run build` seguido de `npm.cmd start -- --hostname 127.0.0.1 --port 3000`. Si la API usa otra dirección, establece `HUMBERTITO_API_URL` antes de iniciar el servidor de desarrollo o compilar. En un despliegue con HTTPS, usa un secreto de sesión estable, activa `HUMBERTITO_SECURE_COOKIES=1` en la API y ejecuta un solo proceso de la API.

Para abrir la interfaz Streamlit, ejecuta `.\.venv\Scripts\python.exe -m streamlit run app.py`. Consulta la [guía de desarrollo](CONTRIBUTING.md) para el análisis de tipos.

## Autor

[Luis Angel Salinas Bardales](https://github.com/luiangelsb26)
