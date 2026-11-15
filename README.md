<div align="center">
  <img width="100%" alt="" src="https://capsule-render.vercel.app/api?type=waving&amp;height=105&amp;color=0:211F34,100:6849BD&amp;section=header">
  <h1>Librería Bazar Humbertito</h1>
  <p>Sistema de gestión de inventario, compras y ventas con una interfaz oscura en Next.js, inventario en Angular y operaciones en Python.</p>

![Angular](https://img.shields.io/badge/Angular-DD0031?style=for-the-badge&logo=angular&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-151515?style=for-the-badge&logo=nextdotjs&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-175B7D?style=for-the-badge&logo=sqlite&logoColor=white)

</div>

<p align="center"><a href="#funcionalidades">Funcionalidades</a> · <a href="#cómo-se-usa">Cómo se usa</a> · <a href="#estructura-del-código">Estructura</a> · <a href="#ejecución-local">Ejecución local</a></p>

**Frontend · Next.js (React) y Angular (inventario)**

**Backend · Python (Starlette)**

## Versión actual

- **Inicio de sesión** con el diseño de dos paneles y opción de mostrar u ocultar la contraseña.
- **Entorno de gestión** con tema oscuro en el panel general, menú, formularios, tablas y gráficos.
- **Inventario en Angular**, integrado con la sesión y la API del resto de la aplicación.

[Ver el cambio de interfaz](https://github.com/luiangelsb26/librer-a-bazar-humbertito/commit/69120d3) · [Ver cómo iniciar el sistema](#ejecución-local)

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

| Carpeta | Contenido |
| --- | --- |
| [`web/`](web/) | Interfaz Next.js y módulo de inventario en Angular. |
| [`backend/`](backend/) | API Starlette, autenticación, acceso a datos, operaciones y pronóstico. |
| [`database/migrations/`](database/migrations/) | Migraciones SQL para Supabase. |
| [`scripts/`](scripts/) | Utilidades de migración y pruebas manuales. |

El punto de entrada de la API está en `api.py`. La base SQLite y los modelos guardados se mantienen en `data/`.

## Ejecución local

Estos pasos son para **Windows con PowerShell**. Necesitas **Git**, **Python 3.14** y **Node.js 20.19+, 22.12+ o 24.x**. Ejecuta los comandos desde la raíz del proyecto.

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
npm.cmd --prefix web ci
```

### 2. Configura la base de datos y el acceso

La API usa **SQLite** por defecto y guarda los datos en `data/humbertito.db`. Si tu instalación usa **Supabase**, configura `SUPABASE_DB_URL` o `DATABASE_URL` en esta terminal antes de crear una cuenta o iniciar la API. Usa la URL de conexión de PostgreSQL que ya utiliza el proyecto. La API lee la variable del entorno. Si migras de la interfaz anterior y guardabas la conexión en los secretos de Streamlit, usa esa misma URL como variable de entorno de la API.

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
npm.cmd --prefix web run dev -- --hostname 127.0.0.1 --port 3000
```

El arranque compila el módulo Angular antes de iniciar Next.js. Abre [Humbertito en el navegador](http://127.0.0.1:3000) e inicia sesión. Next.js envía las solicitudes de `/api` al puerto `8000`. En el menú **Inventario**, Angular usa la misma sesión y la misma API que los demás módulos. Si la pantalla muestra un error de conexión, comprueba que la primera terminal siga ejecutando la API. Para detener el sistema, pulsa **Ctrl+C** en ambas terminales.

### Compilación de producción

Para generar el módulo Angular y la compilación de Next.js, mantén la API activa y ejecuta `npm.cmd --prefix web run build` seguido de `npm.cmd --prefix web start -- --hostname 127.0.0.1 --port 3000`. Si la API usa otra dirección, establece `HUMBERTITO_API_URL` antes de iniciar el servidor de desarrollo o compilar. En un despliegue con HTTPS, usa un secreto de sesión estable, activa `HUMBERTITO_SECURE_COOKIES=1` en la API y ejecuta un solo proceso de la API.

Consulta la [guía de desarrollo](CONTRIBUTING.md) para el análisis de tipos.

## Alojamiento en la nube

El `Dockerfile` arranca Next.js y Angular en el puerto público asignado por el proveedor. La API de Python escucha dentro del mismo contenedor. Por ejemplo, en Railway puedes conectar este repositorio y desplegar la rama `main` desde la raíz.

Configura estas variables en el servicio:

- `SUPABASE_DB_URL` con la conexión PostgreSQL de la base que usa Humbertito. Si tienes datos en SQLite que necesitas conservar, migra esos datos antes de cambiar de base.
- `HUMBERTITO_SESSION_SECRET` con un secreto aleatorio, estable y de al menos 32 caracteres. Puedes generarlo con `python -c "import secrets; print(secrets.token_hex(32))"`.

Mantén una sola instancia. El contenedor exige PostgreSQL y activa las cookies HTTPS. Después de obtener el dominio HTTPS, verifica que cargue el inicio de sesión y que `/api/sesion` devuelva un mensaje para iniciar sesión. Configura `HUMBERTITO_WEB_URL` con ese dominio en los secretos de tu ficha de Streamlit; el botón de acceso abrirá el sistema alojado.

## Autor

[Luis Angel Salinas Bardales](https://github.com/luiangelsb26)
