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

Desde la raíz del repositorio, con el entorno virtual de Python activo y **Node.js 20.9 o superior**:

```powershell
python -m pip install -r requirements.txt -r requirements-web.txt
npm ci
```

1. Si la base ya tiene usuarios, puedes iniciar sesión con esas cuentas. Para una base nueva, ejecuta `python -m api crear-admin`.
2. En una terminal inicia la API. El secreto aleatorio del siguiente ejemplo dura lo que dure esa sesión de PowerShell.

   ```powershell
   $env:HUMBERTITO_SESSION_SECRET = python -c "import secrets; print(secrets.token_hex(32))"
   python -m uvicorn api:create_app --factory --host 127.0.0.1 --port 8000
   ```

3. En otra terminal, ejecuta `npm run dev` y entra a [localhost:3000](http://localhost:3000).

SQLite usa el mismo archivo local del sistema existente. Si usas Supabase, configura `SUPABASE_DB_URL` (o `DATABASE_URL`) en el entorno de la API y de cualquier comando de inicialización. La API lee esas variables del entorno. Para producción, conserva un secreto estable, configura cookies seguras con `HUMBERTITO_SECURE_COOKIES=1` detrás de HTTPS, ejecuta un proceso de API y define `HUMBERTITO_API_URL` si la API está en otro host antes de compilar con `npm run build`. Sirve Next.js con `npm start`.

Para abrir la interfaz Streamlit, ejecuta `python -m streamlit run app.py`. Consulta la [guía de desarrollo](CONTRIBUTING.md) para el análisis de tipos.

## Autor

[Luis Angel Salinas Bardales](https://github.com/luiangelsb26)
