import sqlite3
from pathlib import Path
import pandas as pd
import numpy as np

DB_PATH = Path("data") / "humbertito.db"

def conectar():
    return sqlite3.connect(DB_PATH)

def obtener_ventas_producto(producto_id):
    con = conectar()
    q = """
        SELECT substr(v.fecha,1,10) AS fecha, SUM(dv.cantidad) AS unidades
        FROM ventas v
        JOIN detalle_ventas dv ON v.id = dv.venta_id
        WHERE dv.producto_id = ?
        GROUP BY substr(v.fecha,1,10)
        ORDER BY fecha
    """
    df = pd.read_sql_query(q, con, params=(producto_id,))
    con.close()
    if not df.empty:
        df["fecha"] = pd.to_datetime(df["fecha"])
    return df

def obtener_productos():
    con = conectar()
    df = pd.read_sql_query("""
        SELECT id,codigo,nombre,categoria,stock,stock_minimo
        FROM productos ORDER BY nombre
    """, con)
    con.close()
    return df

def predecir_demanda(producto_id, dias_futuro=7):
    df = obtener_ventas_producto(producto_id)
    if df.empty:
        return {"estado":"sin_datos","mensaje":"No existen ventas registradas para este producto."}
    if len(df) < 3:
        return {"estado":"datos_insuficientes",
                "mensaje":f"Se requieren ventas en al menos 3 días distintos. Actualmente existen {len(df)} día(s).",
                "dias_disponibles":len(df)}
    x = np.arange(len(df), dtype=float)
    y = df["unidades"].astype(float).to_numpy()
    pendiente, intercepto = np.polyfit(x, y, 1)
    futuros = np.arange(len(df), len(df)+dias_futuro, dtype=float)
    pred = np.maximum(pendiente*futuros + intercepto, 0)
    tendencia = "creciente" if pendiente > 0.01 else "decreciente" if pendiente < -0.01 else "estable"
    return {
        "estado":"ok",
        "dias_historicos":len(df),
        "pendiente":float(pendiente),
        "tendencia":tendencia,
        "demanda_7_dias":float(pred.sum()),
        "demanda_predicha":float(pred.sum()),
        "promedio_diario_predicho":float(pred.mean()),
        "predicciones":pred.tolist(),
        "historial":df
    }

def analizar_productos():
    productos = obtener_productos()
    resultados = []
    for _, p in productos.iterrows():
        r = predecir_demanda(int(p["id"]))
        fila = {
            "codigo":p["codigo"], "nombre":p["nombre"],
            "stock_actual":int(p["stock"]),
            "stock_minimo":int(p["stock_minimo"]),
            "estado_prediccion":r["estado"]
        }
        if r["estado"] == "ok":
            faltante = max(0, r["demanda_7_dias"] + p["stock_minimo"] - p["stock"])
            fila.update({
                "tendencia":r["tendencia"],
                "demanda_7_dias":round(r["demanda_7_dias"],2),
                "promedio_diario":round(r["promedio_diario_predicho"],2),
                "cantidad_sugerida":int(np.ceil(faltante)),
                "recomendacion":(
                    f"Evaluar reposición de aproximadamente {int(np.ceil(faltante))} unidad(es)."
                    if faltante > 0 else
                    "El stock actual cubre la demanda estimada y el stock mínimo."
                )
            })
        else:
            fila.update({
                "tendencia":"No disponible",
                "demanda_7_dias":None,
                "promedio_diario":None,
                "cantidad_sugerida":None,
                "recomendacion":r["mensaje"]
            })
        resultados.append(fila)
    return pd.DataFrame(resultados)

if __name__ == "__main__":
    print("="*60)
    print("PREDICCION DE DEMANDA - HUMBERTO IA")
    print("="*60)
    df = analizar_productos()
    print(df.to_string(index=False) if not df.empty else "No existen productos registrados.")
