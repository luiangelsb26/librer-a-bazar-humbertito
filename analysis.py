import sqlite3
from pathlib import Path

import pandas as pd
import numpy as np


# ==========================================================
# CONFIGURACIÓN
# ==========================================================

DB_PATH = Path("data") / "humbertito.db"


# ==========================================================
# CONEXIÓN A LA BASE DE DATOS
# ==========================================================

def conectar():
    return sqlite3.connect(DB_PATH)


# ==========================================================
# OBTENER INFORMACIÓN DE VENTAS
# ==========================================================

def obtener_datos_ventas():

    conexion = conectar()

    consulta = """
        SELECT
            v.fecha,
            p.id AS producto_id,
            p.codigo,
            p.nombre,
            p.categoria,
            dv.cantidad,
            dv.precio_unitario,
            dv.subtotal
        FROM ventas v
        JOIN detalle_ventas dv
            ON v.id = dv.venta_id
        JOIN productos p
            ON dv.producto_id = p.id
        ORDER BY v.fecha
    """

    df = pd.read_sql_query(
        consulta,
        conexion
    )

    conexion.close()

    if not df.empty:
        df["fecha"] = pd.to_datetime(df["fecha"])

    return df


# ==========================================================
# PRODUCTOS MÁS VENDIDOS
# ==========================================================

def productos_mas_vendidos():

    df = obtener_datos_ventas()

    if df.empty:
        return pd.DataFrame()

    resultado = (
        df.groupby(
            ["producto_id", "codigo", "nombre", "categoria"],
            as_index=False
        )["cantidad"]
        .sum()
        .sort_values(
            "cantidad",
            ascending=False
        )
    )

    resultado.rename(
        columns={
            "cantidad": "unidades_vendidas"
        },
        inplace=True
    )

    return resultado


# ==========================================================
# PRODUCTOS CON STOCK BAJO
# ==========================================================

def productos_stock_bajo():

    conexion = conectar()

    consulta = """
        SELECT
            codigo,
            nombre,
            categoria,
            stock,
            stock_minimo
        FROM productos
        WHERE stock <= stock_minimo
        ORDER BY stock ASC
    """

    df = pd.read_sql_query(
        consulta,
        conexion
    )

    conexion.close()

    return df


# ==========================================================
# RESUMEN DE VENTAS
# ==========================================================

def resumen_ventas():

    df = obtener_datos_ventas()

    if df.empty:
        return {
            "total_ventas": 0,
            "unidades_vendidas": 0,
            "promedio_diario": 0,
            "dias_con_ventas": 0
        }

    total_ventas = df["subtotal"].sum()

    unidades_vendidas = df["cantidad"].sum()

    dias_con_ventas = df["fecha"].dt.date.nunique()

    promedio_diario = (
        total_ventas / dias_con_ventas
        if dias_con_ventas > 0
        else 0
    )

    return {
        "total_ventas": total_ventas,
        "unidades_vendidas": unidades_vendidas,
        "promedio_diario": promedio_diario,
        "dias_con_ventas": dias_con_ventas
    }


# ==========================================================
# TENDENCIA DE VENTAS
# ==========================================================

def tendencia_ventas():

    df = obtener_datos_ventas()

    if df.empty:
        return {
            "tipo": "Sin datos",
            "valor": 0
        }

    diario = (
        df.groupby(
            df["fecha"].dt.date
        )["subtotal"]
        .sum()
        .reset_index()
    )

    if len(diario) < 2:
        return {
            "tipo": "Sin datos suficientes",
            "valor": 0
        }

    x = np.arange(len(diario))

    y = diario["subtotal"].values

    pendiente = np.polyfit(
        x,
        y,
        1
    )[0]

    if pendiente > 0.01:
        tipo = "Creciente"

    elif pendiente < -0.01:
        tipo = "Decreciente"

    else:
        tipo = "Estable"

    return {
        "tipo": tipo,
        "valor": pendiente
    }


# ==========================================================
# ANÁLISIS DE PRODUCTOS
# ==========================================================

def clasificar_producto(
    unidades_vendidas,
    stock,
    stock_minimo
):

    if unidades_vendidas == 0:

        if stock <= stock_minimo:
            return "Sin ventas y stock bajo"

        return "Sin movimiento"

    if stock <= stock_minimo:
        return "Alta rotación / requiere reposición"

    if unidades_vendidas >= 10:
        return "Alta rotación"

    if unidades_vendidas >= 5:
        return "Movimiento medio"

    return "Movimiento bajo"


def analisis_productos():

    conexion = conectar()

    consulta = """
        SELECT
            p.id,
            p.codigo,
            p.nombre,
            p.categoria,
            p.stock,
            p.stock_minimo,
            COALESCE(
                SUM(dv.cantidad),
                0
            ) AS unidades_vendidas
        FROM productos p
        LEFT JOIN detalle_ventas dv
            ON p.id = dv.producto_id
        GROUP BY
            p.id,
            p.codigo,
            p.nombre,
            p.categoria,
            p.stock,
            p.stock_minimo
    """

    df = pd.read_sql_query(
        consulta,
        conexion
    )

    conexion.close()

    if df.empty:
        return df

    df["analisis"] = df.apply(
        lambda fila: clasificar_producto(
            fila["unidades_vendidas"],
            fila["stock"],
            fila["stock_minimo"]
        ),
        axis=1
    )

    return df


# ==========================================================
# PRUEBA
# ==========================================================

if __name__ == "__main__":

    print("===================================")
    print("     ANÁLISIS DE HUMBERTO IA")
    print("===================================")

    resumen = resumen_ventas()

    print(
        f"Ventas acumuladas: "
        f"S/ {resumen['total_ventas']:.2f}"
    )

    print(
        f"Unidades vendidas: "
        f"{resumen['unidades_vendidas']}"
    )

    print(
        f"Promedio diario: "
        f"S/ {resumen['promedio_diario']:.2f}"
    )

    print(
        f"Días con ventas: "
        f"{resumen['dias_con_ventas']}"
    )

    tendencia = tendencia_ventas()

    print(
        f"Tendencia de ventas: "
        f"{tendencia['tipo']}"
    )

    print("\nANÁLISIS DE PRODUCTOS:")

    print(
        analisis_productos()
    )