"""Entrenamiento y prediccion de demanda con seleccion temporal de modelos."""

from datetime import date, datetime, timedelta
import hashlib
import io
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

import database


MODEL_PATH = Path(__file__).resolve().parent / "data" / "demanda_random_forest.joblib"
MIN_LAG_DAYS = 28
MIN_FEATURE_DAYS = 60
RANDOM_STATE = 42


def conectar():
    return database.conectar()


@st.cache_resource(ttl=60, show_spinner=False)
def _cargar_artefacto():
    """Busca primero el modelo persistido en la base y luego el archivo local."""
    import joblib
    con = conectar()
    try:
        fila = con.execute(
            "SELECT artefacto FROM modelo_demanda WHERE id = 1"
        ).fetchone()
        if fila and fila[0]:
            return joblib.load(io.BytesIO(bytes(fila[0]))), "base de datos"
    except Exception:
        # Permite usar un modelo local mientras se aplica la migración remota.
        pass
    finally:
        con.close()

    if MODEL_PATH.is_file():
        try:
            return joblib.load(MODEL_PATH), "archivo local"
        except Exception:
            return None, None
    return None, None


def _guardar_artefacto(artefacto, joblib):
    """Prepara la tabla si hace falta, guarda en la base y conserva respaldo local."""
    try:
        buffer = io.BytesIO()
        joblib.dump(artefacto, buffer, compress=3)
        contenido = buffer.getvalue()
    except Exception as error:
        return None, error
    error_base = None
    con = conectar()
    try:
        if database.usar_supabase():
            con.execute("""
                CREATE TABLE IF NOT EXISTS public.modelo_demanda (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    artefacto BYTEA NOT NULL,
                    actualizado_en TEXT NOT NULL
                )
            """)
        else:
            con.execute("""
                CREATE TABLE IF NOT EXISTS modelo_demanda (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    artefacto BLOB NOT NULL,
                    actualizado_en TEXT NOT NULL
                )
            """)
        con.execute(
            """
            INSERT INTO modelo_demanda (id, artefacto, actualizado_en)
            VALUES (1, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                artefacto = excluded.artefacto,
                actualizado_en = excluded.actualizado_en
            """,
            (contenido, datetime.now().isoformat(timespec="seconds")),
        )
        con.commit()
        guardado_en_base = True
    except Exception as error:
        con.rollback()
        error_base = error
        guardado_en_base = False
    finally:
        con.close()

    error_local = None
    ruta_temporal = MODEL_PATH.with_name(
        f".{MODEL_PATH.stem}.tmp{MODEL_PATH.suffix}"
    )
    try:
        MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(artefacto, ruta_temporal, compress=3)
        ruta_temporal.replace(MODEL_PATH)
    except Exception as error:
        error_local = error
        try:
            ruta_temporal.unlink(missing_ok=True)
        except OSError:
            pass

    if guardado_en_base:
        return "base de datos", None
    if error_local is None:
        return "archivo local", error_base
    return None, error_base or error_local


@st.cache_data(ttl=60, show_spinner=False, max_entries=1)
def obtener_productos():
    con = conectar()
    try:
        return pd.read_sql_query(
            """
            SELECT id, codigo, nombre, categoria, stock, stock_minimo
            FROM productos
            ORDER BY nombre
            """,
            con,
        )
    finally:
        con.close()


@st.cache_data(ttl=120, show_spinner=False, max_entries=1)
def _obtener_ventas_diarias():
    """Reutiliza el historial agregado compartido con el módulo de análisis."""
    import analysis

    datos = analysis.obtener_datos_ventas()
    if datos.empty:
        return pd.DataFrame(
            columns=["producto_id", "codigo_producto", "fecha", "unidades"]
        )

    return datos[
        ["producto_id", "codigo", "fecha", "cantidad"]
    ].rename(
        columns={"codigo": "codigo_producto", "cantidad": "unidades"}
    )


def _series_diarias(df_ventas):
    """Rellena con cero los dias sin ventas dentro del historial registrado."""
    if df_ventas.empty:
        return {}, None

    datos = df_ventas.copy()
    datos["fecha"] = pd.to_datetime(datos["fecha"]).dt.normalize()
    ultima_fecha = datos["fecha"].max().date()
    series = {}

    for codigo_producto, grupo in datos.groupby("codigo_producto"):
        diario = grupo.groupby("fecha")["unidades"].sum().sort_index()
        fechas = pd.date_range(diario.index.min(), pd.Timestamp(ultima_fecha), freq="D")
        completo = diario.reindex(fechas, fill_value=0).astype(float)
        series[str(codigo_producto)] = {
            "inicio": completo.index[0].date(),
            "valores": completo.to_list(),
        }

    return series, ultima_fecha


def _nombres_caracteristicas(product_codes):
    base = [
        "ventas_dia_anterior",
        "ventas_hace_7_dias",
        "ventas_hace_14_dias",
        "promedio_7_dias_anteriores",
        "promedio_28_dias_anteriores",
        "dia_semana_seno",
        "dia_semana_coseno",
        "mes_seno",
        "mes_coseno",
    ]
    return base + [f"producto_{codigo}" for codigo in product_codes]


def _crear_vector(historial, fecha_objetivo, codigo_producto, product_codes):
    if len(historial) < MIN_LAG_DAYS:
        return None

    dia_semana = fecha_objetivo.weekday()
    mes = fecha_objetivo.month - 1
    vector = [
        float(historial[-1]),
        float(historial[-7]),
        float(historial[-14]),
        float(np.mean(historial[-7:])),
        float(np.mean(historial[-28:])),
        float(np.sin(2 * np.pi * dia_semana / 7)),
        float(np.cos(2 * np.pi * dia_semana / 7)),
        float(np.sin(2 * np.pi * mes / 12)),
        float(np.cos(2 * np.pi * mes / 12)),
    ]
    vector.extend(1.0 if current_code == codigo_producto else 0.0 for current_code in product_codes)
    return vector


def _crear_dataset(series):
    product_codes = sorted(series)
    filas = []
    fechas = []
    objetivos = []

    for codigo_producto in product_codes:
        inicio = series[codigo_producto]["inicio"]
        valores = series[codigo_producto]["valores"]
        for indice in range(MIN_LAG_DAYS, len(valores)):
            fecha_objetivo = inicio + timedelta(days=indice)
            vector = _crear_vector(
                valores[:indice], fecha_objetivo, codigo_producto, product_codes
            )
            if vector is not None:
                filas.append(vector)
                fechas.append(fecha_objetivo)
                objetivos.append(float(valores[indice]))

    return product_codes, np.asarray(filas, dtype=float), np.asarray(objetivos, dtype=float), fechas


def _mae(real, estimado):
    return float(np.mean(np.abs(np.asarray(real) - np.asarray(estimado))))


def _evaluar_horizonte(modelo, series, product_codes, corte, horizonte=7):
    """Evalua ventanas futuras de varios dias sin alimentar valores reales del futuro."""
    reales = []
    predichos = []
    referencias = []
    fechas_evaluadas = []
    ventanas = 0

    for codigo_producto in product_codes:
        inicio = series[codigo_producto]["inicio"]
        valores = series[codigo_producto]["valores"]
        primer_indice_prueba = (corte - inicio).days
        if primer_indice_prueba < MIN_LAG_DAYS:
            continue

        for origen in range(
            primer_indice_prueba,
            len(valores) - horizonte + 1,
            horizonte,
        ):
            historial = list(valores[:origen])
            baseline = valores[origen - horizonte:origen]
            prediccion_ventana = []
            for paso in range(horizonte):
                fecha_objetivo = inicio + timedelta(days=origen + paso)
                vector = _crear_vector(
                    historial, fecha_objetivo, codigo_producto, product_codes
                )
                estimacion = max(0.0, float(modelo.predict([vector])[0]))
                prediccion_ventana.append(estimacion)
                historial.append(estimacion)

            reales.extend(float(v) for v in valores[origen:origen + horizonte])
            predichos.extend(prediccion_ventana)
            referencias.extend(float(v) for v in baseline)
            fechas_evaluadas.extend(
                inicio + timedelta(days=origen + paso)
                for paso in range(horizonte)
            )
            ventanas += 1

    return reales, predichos, referencias, fechas_evaluadas, ventanas


def _firma_historial(df_ventas, fecha_fin_exclusiva):
    """Identifica el historial usado, sin invalidar el modelo por ventas nuevas."""
    if df_ventas.empty:
        return hashlib.sha256(b"").hexdigest()
    datos = df_ventas.copy()
    datos["fecha"] = pd.to_datetime(datos["fecha"]).dt.strftime("%Y-%m-%d")
    datos = datos[datos["fecha"] < fecha_fin_exclusiva]
    datos = datos.sort_values(["codigo_producto", "fecha"])
    contenido = datos[["codigo_producto", "fecha", "unidades"]].to_csv(index=False)
    return hashlib.sha256(contenido.encode("utf-8")).hexdigest()


def entrenar_modelo():
    """Entrena y valida cronologicamente; activa el modelo si supera el baseline."""
    try:
        from sklearn.ensemble import ExtraTreesRegressor, RandomForestRegressor
        import joblib
    except ImportError:
        return {
            "estado": "dependencia_faltante",
            "mensaje": "Instale las dependencias del proyecto con pip install -r requirements.txt.",
        }

    df_ventas = _obtener_ventas_diarias()
    if df_ventas.empty:
        return {
            "estado": "sin_datos",
            "mensaje": "No hay ventas registradas para entrenar el modelo.",
        }

    series, _ = _series_diarias(df_ventas)
    product_codes, X, y, fechas = _crear_dataset(series)
    fechas_unicas = sorted(set(fechas))

    if len(fechas_unicas) < MIN_FEATURE_DAYS or len(y) < 40:
        return {
            "estado": "datos_insuficientes",
            "mensaje": (
                f"Se necesitan al menos {MIN_FEATURE_DAYS} fechas con datos utilizables "
                f"despues de preparar los rezagos de {MIN_LAG_DAYS} dias, "
                "y suficientes observaciones para entrenar y evaluar."
            ),
            "dias_disponibles": len(fechas_unicas),
            "observaciones": int(len(y)),
        }

    corte = fechas_unicas[int(len(fechas_unicas) * 0.8)]
    mascara_entrenamiento = np.asarray([fecha < corte for fecha in fechas])
    if mascara_entrenamiento.sum() < 30:
        return {
            "estado": "datos_insuficientes",
            "mensaje": "No hay suficientes observaciones para separar entrenamiento y evaluacion temporal.",
        }

    modelos = {
        "RandomForestRegressor": RandomForestRegressor(
            n_estimators=300,
            max_depth=12,
            min_samples_leaf=2,
            max_features=0.8,
            random_state=RANDOM_STATE,
            n_jobs=-1,
        ),
        "ExtraTreesRegressor": ExtraTreesRegressor(
            n_estimators=300,
            max_depth=12,
            min_samples_leaf=2,
            max_features=0.8,
            random_state=RANDOM_STATE,
            n_jobs=-1,
        ),
    }
    resultados_modelos = {}
    for nombre, candidato in modelos.items():
        candidato.fit(X[mascara_entrenamiento], y[mascara_entrenamiento])
        reales, predicciones, baseline, fechas_prueba, ventanas = _evaluar_horizonte(
            candidato, series, product_codes, corte, horizonte=7
        )
        if len(reales) >= 7:
            resultados_modelos[nombre] = {
                "modelo": candidato,
                "reales": reales,
                "predicciones": predicciones,
                "baseline": baseline,
                "fechas_prueba": fechas_prueba,
                "ventanas": ventanas,
                "mae": _mae(reales, predicciones),
            }

    if not resultados_modelos:
        return {
            "estado": "datos_insuficientes",
            "mensaje": "No hay un periodo futuro suficiente para evaluar una prediccion de 7 dias.",
        }

    # Ambos algoritmos comparten el mismo corte cronologico y la misma referencia.
    # Se selecciona por MAE fuera de muestra, antes de reajustar con todo el historial.
    algoritmo, mejor = min(
        resultados_modelos.items(), key=lambda elemento: elemento[1]["mae"]
    )
    modelo = mejor["modelo"]
    reales = mejor["reales"]
    predicciones = mejor["predicciones"]
    baseline = mejor["baseline"]
    fechas_prueba = mejor["fechas_prueba"]
    ventanas = mejor["ventanas"]

    y_prueba = np.asarray(reales, dtype=float)
    predicciones = np.asarray(predicciones, dtype=float)
    baseline = np.asarray(baseline, dtype=float)
    mae_modelo = _mae(y_prueba, predicciones)
    mae_baseline = _mae(y_prueba, baseline)
    rmse_modelo = float(np.sqrt(np.mean((y_prueba - predicciones) ** 2)))
    suma_real = float(np.sum(np.abs(y_prueba)))
    wape = (
        float(np.sum(np.abs(y_prueba - predicciones)) / suma_real * 100)
        if suma_real
        else 0.0
    )

    evaluacion = {
        "mae": mae_modelo,
        "rmse": rmse_modelo,
        "wape_porcentaje": wape,
        "mae_baseline_7_dias": mae_baseline,
        "supera_baseline": mae_modelo < mae_baseline,
        "fecha_inicio_prueba": min(fechas_prueba).isoformat(),
        "fecha_fin_prueba": max(fechas_prueba).isoformat(),
        "ventanas_prueba_7_dias": ventanas,
        "observaciones_entrenamiento": int(mascara_entrenamiento.sum()),
        "observaciones_prueba": int(len(y_prueba)),
        "modelos_comparados": {
            nombre: round(resultado["mae"], 4)
            for nombre, resultado in resultados_modelos.items()
        },
    }

    if not evaluacion["supera_baseline"]:
        return {
            "estado": "no_supera_baseline",
            "mensaje": (
                "El mejor modelo evaluado no mejoro el error de la referencia "
                "de ventas de hace 7 dias. No se activo el modelo; acumule mas historial "
                "y vuelva a evaluar."
            ),
            "evaluacion": evaluacion,
        }

    # La validacion se calcula con el tramo reservado. Una vez aceptado el
    # algoritmo, se reajusta con todo el historial disponible para produccion.
    modelo.fit(X, y)
    fecha_fin_historial = pd.to_datetime(df_ventas["fecha"]).max().date()
    fecha_firma_exclusiva = (fecha_fin_historial + timedelta(days=1)).isoformat()
    artefacto = {
        "modelo": modelo,
        "producto_codigos": product_codes,
        "fecha_entrenamiento": date.today().isoformat(),
        "fecha_fin_historial": fecha_fin_historial.isoformat(),
        "fecha_firma_exclusiva": fecha_firma_exclusiva,
        "firma_historial": _firma_historial(
            df_ventas, fecha_firma_exclusiva
        ),
        "dias_minimos_rezago": MIN_LAG_DAYS,
        "nombres_caracteristicas": _nombres_caracteristicas(product_codes),
        "evaluacion": evaluacion,
        "algoritmo": algoritmo,
    }
    almacenamiento, error_guardado = _guardar_artefacto(artefacto, joblib)
    if almacenamiento is not None:
        _cargar_artefacto.clear()
        estado_modelo.clear()
        _obtener_ventas_diarias.clear()
    if almacenamiento is None:
        return {
            "estado": "error_guardar_modelo",
            "mensaje": (
                "El modelo se entrenó, pero no se pudo guardar en la base ni "
                f"en el servidor local. Detalle: {error_guardado}"
            ),
            "evaluacion": evaluacion,
        }

    if almacenamiento == "archivo local" and database.usar_supabase():
        return {
            "estado": "ok_local",
            "mensaje": (
                "El modelo se entrenó y quedó disponible en este servidor, pero "
                "no se guardó de forma persistente en Supabase. La aplicación intentó "
                "crear la tabla automáticamente; si la conexión no tiene permiso para "
                "crear tablas, ejecute migracion_modelo_demanda.sql en Supabase y vuelva "
                "a entrenarlo."
            ),
            "evaluacion": evaluacion,
            "almacenamiento": almacenamiento,
        }

    return {
        "estado": "ok",
        "mensaje": "Modelo entrenado, evaluado y guardado de forma persistente.",
        "evaluacion": evaluacion,
        "ruta_modelo": str(MODEL_PATH),
        "almacenamiento": almacenamiento,
    }


@st.cache_data(ttl=120, show_spinner=False, max_entries=1)
def estado_modelo():
    try:
        import joblib
        artefacto, almacenamiento = _cargar_artefacto()
        if artefacto is None:
            return {
                "estado": "modelo_no_entrenado",
                "mensaje": "Todavia no hay un modelo entrenado y validado.",
            }
        df_ventas = _obtener_ventas_diarias()
        firma_actual = _firma_historial(
            df_ventas, artefacto.get("fecha_firma_exclusiva", "0001-01-01")
        )
        if firma_actual != artefacto.get("firma_historial"):
            return {
                "estado": "modelo_desactualizado",
                "mensaje": "El historial usado para entrenar cambio. Vuelva a entrenar el modelo.",
            }
        return {
            "estado": "ok",
            "algoritmo": artefacto.get("algoritmo", "RandomForestRegressor"),
            "fecha_entrenamiento": artefacto.get("fecha_entrenamiento"),
            "fecha_fin_historial": artefacto.get("fecha_fin_historial"),
            "almacenamiento": almacenamiento,
            "evaluacion": artefacto.get("evaluacion", {}),
        }
    except Exception:
        return {
            "estado": "modelo_invalido",
            "mensaje": "No se pudo leer el modelo guardado. Vuelva a entrenarlo.",
        }


def obtener_ventas_producto(producto_id):
    df = _obtener_ventas_diarias()
    if df.empty:
        return pd.DataFrame(columns=["fecha", "unidades"])
    producto = df[df["producto_id"] == producto_id][["fecha", "unidades"]].copy()
    if producto.empty:
        return pd.DataFrame(columns=["fecha", "unidades"])
    producto["fecha"] = pd.to_datetime(producto["fecha"])
    return producto.sort_values("fecha").reset_index(drop=True)


def predecir_demanda(producto_id, dias_futuro=7):
    try:
        dias_futuro = int(dias_futuro)
    except (TypeError, ValueError):
        return {
            "estado": "horizonte_invalido",
            "mensaje": "Indique un horizonte de predicción entre 1 y 30 días.",
        }
    if not 1 <= dias_futuro <= 30:
        return {
            "estado": "horizonte_invalido",
            "mensaje": "Indique un horizonte de predicción entre 1 y 30 días.",
        }

    try:
        import joblib
    except ImportError:
        return {
            "estado": "dependencia_faltante",
            "mensaje": "Instale las dependencias del proyecto con pip install -r requirements.txt.",
        }

    try:
        artefacto, _ = _cargar_artefacto()
    except Exception:
        return {
            "estado": "modelo_invalido",
            "mensaje": "No se pudo leer el modelo. Vuelva a entrenarlo.",
        }
    if artefacto is None:
        return {
            "estado": "modelo_no_entrenado",
            "mensaje": "Primero entrene y valide el modelo con el historial disponible.",
        }

    df_ventas = _obtener_ventas_diarias()
    firma_actual = _firma_historial(
        df_ventas, artefacto.get("fecha_firma_exclusiva", "0001-01-01")
    )
    if firma_actual != artefacto.get("firma_historial"):
        return {
            "estado": "modelo_desactualizado",
            "mensaje": "El historial usado para entrenar cambio. Vuelva a entrenar el modelo.",
        }

    producto_id = int(producto_id)
    productos = obtener_productos()
    producto = productos[productos["id"] == producto_id]
    if producto.empty:
        return {
            "estado": "producto_no_encontrado",
            "mensaje": "El producto seleccionado ya no existe en la base de datos.",
        }
    codigo_producto = str(producto.iloc[0]["codigo"])
    product_codes = artefacto["producto_codigos"]
    if codigo_producto not in product_codes:
        return {
            "estado": "producto_sin_entrenar",
            "mensaje": "Este producto no estaba en el entrenamiento. Reentrene el modelo con su historial.",
        }

    series, ultima_fecha = _series_diarias(df_ventas)
    serie = series.get(codigo_producto)
    if serie is None:
        return {
            "estado": "sin_datos",
            "mensaje": "No existen ventas registradas para este producto.",
        }

    ventas_producto = df_ventas[df_ventas["producto_id"] == producto_id]
    fecha_ultima_venta_producto = pd.to_datetime(
        ventas_producto["fecha"]
    ).max().date()

    historial = list(serie["valores"])
    dias_historicos_observados = len(historial)
    if dias_historicos_observados < MIN_LAG_DAYS:
        return {
            "estado": "datos_insuficientes",
            "mensaje": f"Se requieren al menos {MIN_LAG_DAYS} dias calendario de historial para este producto.",
            "dias_disponibles": dias_historicos_observados,
        }

    # Proyecta desde hoy (o desde la última fecha futura registrada), no desde
    # una fecha antigua si el registro se quedó varios días sin actualizar.
    fecha_base = max(ultima_fecha, date.today())
    dias_sin_registro = (fecha_base - ultima_fecha).days
    if dias_sin_registro > 0:
        historial.extend([0.0] * dias_sin_registro)

    pronosticos = []
    fechas_prediccion = []
    for paso in range(1, int(dias_futuro) + 1):
        fecha_objetivo = fecha_base + timedelta(days=paso)
        vector = _crear_vector(historial, fecha_objetivo, codigo_producto, product_codes)
        estimacion = max(0.0, float(artefacto["modelo"].predict([vector])[0]))
        pronosticos.append(estimacion)
        fechas_prediccion.append(fecha_objetivo.isoformat())
        historial.append(estimacion)

    return {
        "estado": "ok",
        "algoritmo": artefacto.get("algoritmo", "RandomForestRegressor"),
        "dias_historicos": dias_historicos_observados,
        "fecha_base_prediccion": fecha_base.isoformat(),
        "fecha_ultima_venta_producto": fecha_ultima_venta_producto.isoformat(),
        "fechas_prediccion": fechas_prediccion,
        "demanda_predicha": float(sum(pronosticos)),
        "demanda_7_dias": (
            float(sum(pronosticos[:7])) if len(pronosticos) >= 7 else None
        ),
        "promedio_diario_predicho": float(np.mean(pronosticos)),
        "predicciones": pronosticos,
        "historial": obtener_ventas_producto(producto_id),
        "evaluacion": artefacto.get("evaluacion", {}),
    }


def analizar_productos():
    productos = obtener_productos()
    resultados = []
    for _, producto in productos.iterrows():
        resultado = predecir_demanda(int(producto["id"]))
        fila = {
            "codigo": producto["codigo"],
            "nombre": producto["nombre"],
            "stock_actual": int(producto["stock"]),
            "stock_minimo": int(producto["stock_minimo"]),
            "estado_prediccion": resultado["estado"],
        }
        if resultado["estado"] == "ok":
            faltante = max(
                0,
                resultado["demanda_predicha"]
                + producto["stock_minimo"]
                - producto["stock"],
            )
            fila.update(
                {
                    "demanda_7_dias": round(resultado["demanda_predicha"], 2),
                    "promedio_diario": round(resultado["promedio_diario_predicho"], 2),
                    "cantidad_sugerida": int(np.ceil(faltante)),
                    "recomendacion": (
                        f"Evaluar reposicion de aproximadamente {int(np.ceil(faltante))} unidad(es)."
                        if faltante > 0
                        else "El stock actual cubre la demanda estimada y el stock minimo."
                    ),
                }
            )
        else:
            fila.update(
                {
                    "demanda_7_dias": None,
                    "promedio_diario": None,
                    "cantidad_sugerida": None,
                    "recomendacion": resultado["mensaje"],
                }
            )
        resultados.append(fila)
    return pd.DataFrame(resultados)
