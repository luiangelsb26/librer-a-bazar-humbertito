import pandas as pd
import streamlit as st
import database


# ==========================================================
# CONFIGURACIÓN
# ==========================================================

# ==========================================================
# CONEXIÓN A LA BASE DE DATOS
# ==========================================================

def conectar():
    return database.conectar()


# ==========================================================
# OBTENER INFORMACIÓN DE VENTAS
# ==========================================================

@st.cache_data(ttl=120, show_spinner=False, max_entries=1)
def obtener_datos_ventas():

    conexion = conectar()

    consulta = """
        SELECT
            substr(v.fecha, 1, 10) AS fecha,
            p.id AS producto_id,
            p.codigo,
            p.nombre,
            p.categoria,
            SUM(dv.cantidad) AS cantidad,
            SUM(dv.subtotal) AS subtotal
        FROM ventas v
        JOIN detalle_ventas dv
            ON v.id = dv.venta_id
        JOIN productos p
            ON dv.producto_id = p.id
        GROUP BY
            substr(v.fecha, 1, 10),
            p.id,
            p.codigo,
            p.nombre,
            p.categoria
        ORDER BY fecha, p.nombre
    """

    try:
        df = pd.read_sql_query(
            consulta,
            conexion
        )
    finally:
        conexion.close()

    if not df.empty:
        df["fecha"] = pd.to_datetime(df["fecha"])

    return df


# ==========================================================
# PRODUCTOS MÁS VENDIDOS
# ==========================================================

def productos_mas_vendidos(df=None):

    if df is None:
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

@st.cache_data(ttl=120, show_spinner=False, max_entries=1)
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

    try:
        df = pd.read_sql_query(
            consulta,
            conexion
        )
    finally:
        conexion.close()

    return df


# ==========================================================
# RESUMEN DE VENTAS
# ==========================================================

def resumen_ventas(df=None):

    if df is None:
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

def tendencia_ventas(df=None):

    if df is None:
        df = obtener_datos_ventas()

    if df.empty:
        return {
            "tipo": "Sin ventas recientes",
            "valor": None,
            "ventas_periodo_base": 0,
            "ventas_periodo_reciente": 0,
            "fecha_inicio": None,
            "fecha_fin": None,
            "dias_por_periodo": 45,
            "explicacion": "No hay ventas registradas para analizar."
        }

    # Se comparan dos tramos iguales dentro de los últimos 90 días.
    # Los días sin ventas se incluyen con valor cero para que no se omitan.
    fecha_fin = pd.Timestamp.now().normalize()
    fecha_inicio = fecha_fin - pd.Timedelta(days=89)
    fechas = pd.date_range(fecha_inicio, fecha_fin, freq="D")
    datos_recientes = df.loc[
        (df["fecha"] >= fecha_inicio)
        & (df["fecha"] < fecha_fin + pd.Timedelta(days=1))
    ]
    diario = (
        datos_recientes.assign(fecha=datos_recientes["fecha"].dt.normalize())
        .groupby("fecha")["subtotal"]
        .sum()
        .reindex(fechas, fill_value=0)
    )

    dias_por_periodo = 45
    ventas_periodo_base = float(diario.iloc[:dias_por_periodo].sum())
    ventas_periodo_reciente = float(diario.iloc[dias_por_periodo:].sum())

    if ventas_periodo_base == 0 and ventas_periodo_reciente == 0:
        return {
            "tipo": "Sin ventas recientes",
            "valor": None,
            "ventas_periodo_base": ventas_periodo_base,
            "ventas_periodo_reciente": ventas_periodo_reciente,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
            "dias_por_periodo": dias_por_periodo,
            "explicacion": "No se registraron ventas en los últimos 90 días."
        }

    if ventas_periodo_base == 0:
        tipo = "Creciente"
        variacion = None
        explicacion = (
            "No hubo ventas en los primeros 45 días y se registraron "
            "ventas en los últimos 45 días. "
            "No se calcula un porcentaje porque el periodo inicial no tiene "
            "una base de ventas."
        )
    elif ventas_periodo_reciente == 0:
        tipo = "Decreciente"
    else:
        variacion = (
            (ventas_periodo_reciente - ventas_periodo_base)
            / ventas_periodo_base
            * 100
        )
        if variacion > 5:
            tipo = "Creciente"
        elif variacion < -5:
            tipo = "Decreciente"
        else:
            tipo = "Estable"

        if tipo == "Creciente":
            explicacion = (
                f"El total del periodo reciente aumentó {variacion:.1f}% "
                "respecto al periodo base. Se clasifica como creciente cuando "
                "el aumento supera el umbral del 5%."
            )
        elif tipo == "Decreciente":
            explicacion = (
                f"El total del periodo reciente disminuyó {abs(variacion):.1f}% "
                "respecto al periodo base. Se clasifica como decreciente cuando "
                "la caída supera el umbral del 5%."
            )
        else:
            explicacion = (
                f"La variación entre periodos fue de {variacion:+.1f}%, "
                "dentro del margen de ±5%; por eso se clasifica como estable."
            )

    if ventas_periodo_base > 0 and ventas_periodo_reciente == 0:
        variacion = -100.0
        explicacion = (
            f"Las ventas pasaron de S/ {ventas_periodo_base:,.2f} en los "
            "primeros 45 días a S/ 0.00 en los últimos 45 días, una "
            "disminución del 100%."
        )

    return {
        "tipo": tipo,
        "valor": variacion,
        "ventas_periodo_base": ventas_periodo_base,
        "ventas_periodo_reciente": ventas_periodo_reciente,
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "dias_por_periodo": dias_por_periodo,
        "explicacion": explicacion
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


@st.cache_data(ttl=120, show_spinner=False, max_entries=1)
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

    try:
        df = pd.read_sql_query(
            consulta,
            conexion
        )
    finally:
        conexion.close()

    if df.empty:
        return df

    unidades = df["unidades_vendidas"]
    stock_bajo = df["stock"] <= df["stock_minimo"]
    df["analisis"] = "Sin movimiento"
    df.loc[unidades > 0, "analisis"] = "Movimiento bajo"
    df.loc[unidades >= 5, "analisis"] = "Movimiento medio"
    df.loc[unidades >= 10, "analisis"] = "Alta rotación"
    df.loc[(unidades > 0) & stock_bajo, "analisis"] = (
        "Alta rotación / requiere reposición"
    )
    df.loc[(unidades == 0) & stock_bajo, "analisis"] = (
        "Sin ventas y stock bajo"
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
