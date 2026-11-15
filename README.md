<div align="center">
  <img width="100%" alt="" src="https://capsule-render.vercel.app/api?type=waving&amp;height=105&amp;color=0:0C2944,100:087E8B&amp;section=header">
  <h1>Librería Bazar Humbertito</h1>
  <p>Sistema de gestión de inventario, compras y ventas para una librería y bazar.</p>

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
| [`app.py`](app.py) | Interfaz de Streamlit y flujos de operación. |
| [`database.py`](database.py) | Acceso a datos con SQLite local o PostgreSQL. |
| [`auth.py`](auth.py) | Autenticación y administración de usuarios. |
| [`analysis.py`](analysis.py) y [`prediction.py`](prediction.py) | Análisis del historial de ventas y pronóstico de demanda con scikit-learn. |
| [`pdf_report.py`](pdf_report.py) | Generación de reportes en PDF. |

## Ejecución local

Desde la raíz del repositorio, en un entorno virtual de Python:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

La base local usa SQLite. Para usar PostgreSQL, configura la conexión mediante la variable de entorno `SUPABASE_DB_URL` o `DATABASE_URL`. Consulta la [guía de desarrollo](CONTRIBUTING.md) para el análisis de tipos.

## Autor

[Luis Angel Salinas Bardales](https://github.com/luiangelsb26)
