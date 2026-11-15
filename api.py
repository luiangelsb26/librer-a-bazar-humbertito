"""API de la interfaz Next.js. Ejecutar un proceso con uvicorn."""
import hashlib
import hmac
import io
import json
import logging
import math
import os
import time
from contextlib import asynccontextmanager
from datetime import date, datetime
from decimal import Decimal
from threading import Lock
from zipfile import BadZipFile, ZipFile

import pandas as pd
from starlette.applications import Starlette
from starlette.concurrency import run_in_threadpool
from starlette.exceptions import HTTPException
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import JSONResponse, Response
from starlette.routing import Route

import auth
import database
import operaciones as ops

LOG = logging.getLogger(__name__)
WRITE_LOCK = Lock()
LOGIN_LOCK = Lock()
LOGIN_ATTEMPTS = {}
PRODUCT = "id codigo nombre categoria precio_compra precio_venta stock stock_minimo dias_entrega"
SALE = "id fecha total producto cantidad precio subtotal stock_descontado referencia linea"
PURCHASE = "id fecha total referencia producto cantidad precio subtotal"
USER = "id username nombre rol activo creado"
XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def normalize(value):
    if isinstance(value, pd.DataFrame):
        return json.loads(value.to_json(orient="records", date_format="iso"))
    if isinstance(value, dict):
        return {k: normalize(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [normalize(item) for item in value]
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, Decimal):
        value = float(value)
    if hasattr(value, "item"):
        return normalize(value.item())
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


def table(columns, rows):
    names = columns.split()
    return [dict(zip(names, row)) for row in rows]


def json_response(data, status=200):
    return JSONResponse(normalize(data), status_code=status, headers={"Cache-Control": "no-store"})


def file_response(data, name, media_type=XLSX):
    return Response(data, media_type=media_type, headers={
        "Content-Disposition": f'attachment; filename="{name}"',
        "Cache-Control": "no-store",
    })


def current_user(request):
    uid = request.session.get("uid")
    if uid is None:
        raise HTTPException(401, "Inicia sesión para continuar.")
    con = database.conectar()
    try:
        row = con.execute(
            "SELECT id, username, nombre, rol, activo, password FROM usuarios WHERE id = ? AND activo = 1",
            (uid,),
        ).fetchone()
    finally:
        con.close()
    fingerprint = hashlib.sha256(str(row[5]).encode()).hexdigest() if row else ""
    if not row or not hmac.compare_digest(fingerprint, request.session.get("fingerprint", "")):
        request.session.clear()
        raise HTTPException(401, "La sesión ya no está disponible.")
    return dict(zip(USER.split()[:5], row[:5]))


def login(request, data):
    username = word(data, "username")
    password = word(data, "password")
    ip = request.client.host if request.client else "local"
    key = (ip, username.casefold())
    now = time.monotonic()
    with LOGIN_LOCK:
        for expired in [k for k, entries in LOGIN_ATTEMPTS.items() if now - entries[-1] >= 300]:
            del LOGIN_ATTEMPTS[expired]
        attempts = LOGIN_ATTEMPTS.get(key, [])
        attempts = [stamp for stamp in attempts if now - stamp < 300]
        if len(attempts) >= 8 or len(LOGIN_ATTEMPTS) >= 4000:
            raise HTTPException(429, "Demasiados intentos. Inténtalo en unos minutos.")
        LOGIN_ATTEMPTS[key] = attempts + [now]
    account = auth.verificar_usuario(username, password)
    if not account:
        raise HTTPException(401, "Usuario o contraseña incorrectos.")
    with LOGIN_LOCK:
        LOGIN_ATTEMPTS.pop(key, None)
    con = database.conectar()
    try:
        stored = con.execute("SELECT password FROM usuarios WHERE id = ?", (account["id"],)).fetchone()
    finally:
        con.close()
    if not stored:
        raise HTTPException(401, "La cuenta ya no está disponible.")
    request.session.clear()
    request.session.update(uid=account["id"], fingerprint=hashlib.sha256(str(stored[0]).encode()).hexdigest())
    return json_response(account)


def word(data, field, optional=False):
    value = data.get(field, "")
    if not isinstance(value, str) or len(value) > 500 or (not optional and not value.strip()):
        raise HTTPException(422, f"Revisa el campo {field}.")
    return value if field == "password" else value.strip()


def number(data, field, *, integer=False, minimum=0, maximum=1_000_000_000):
    try:
        value = float(data.get(field, ""))
        if not math.isfinite(value) or not minimum <= value <= maximum or (integer and not value.is_integer()):
            raise ValueError()
    except (ValueError, TypeError):
        raise HTTPException(422, f"Revisa el valor de {field}.") from None
    return int(value) if integer else value


def required_admin(user):
    if user["rol"] != "admin":
        raise HTTPException(403, "Esta operación requiere permisos de administración.")


def outcome(result):
    ok, message = result
    return json_response({"message": message}, 200 if ok else 422)


def forecast(data):
    import prediction

    pid = number(data, "producto_id", integer=True, minimum=1)
    days = number(data, "dias", integer=True, minimum=1, maximum=30)
    result = prediction.predecir_demanda(pid, days)
    if result["estado"] != "ok":
        raise HTTPException(422, result.get("mensaje", "No hay un pronóstico disponible para este producto."))
    product = next((row for row in ops.obtener_productos() if row[0] == pid), None)
    if product is None:
        raise HTTPException(404, "Producto no encontrado.")
    suggested = max(0, math.ceil(result["demanda_predicha"] + product[7] - product[6]))
    return product, result, suggested


def forecast_pdf(data):
    import pdf_report

    product, result, suggested = forecast(data)
    days = [date.fromisoformat(day).strftime("%d/%m/%Y") for day in result["fechas_prediccion"]]
    report = {
        "nombre_producto": product[2], "codigo_producto": product[1],
        "periodo": f"{days[0]} al {days[-1]}", "dias_historicos": result["dias_historicos"],
        "fecha_ultima_venta": result["fecha_ultima_venta_producto"], "fecha_base": result["fecha_base_prediccion"],
        "demanda_predicha": result["demanda_predicha"], "promedio_diario": result["promedio_diario_predicho"],
        "dias_entrega": result["dias_entrega"], "dias_cobertura": result["dias_cobertura"],
        "stock_actual": product[6], "stock_minimo": product[7], "cantidad_sugerida": suggested,
        "filas_prediccion": [[day, f"{qty:.2f}"] for day, qty in zip(days, result["predicciones"])],
        "evaluacion": result["evaluacion"],
    }
    return file_response(pdf_report.construir_informe_prediccion(report), "pronostico.pdf", "application/pdf")


def spreadsheet(kind, action, data):
    sources = {
        "productos": (ops.crear_plantilla_productos_excel, ops.validar_productos_excel, ops.importar_productos_excel),
        "ventas": (ops.crear_plantilla_ventas_excel, ops.validar_ventas_excel, ops.importar_ventas_excel),
        "compras": (ops.crear_plantilla_compras_excel, ops.validar_compras_excel, ops.importar_compras_excel),
    }
    if kind not in sources:
        raise HTTPException(404)
    template, validate, save = sources[kind]
    if action == "plantilla":
        return file_response(template(), f"plantilla-{kind}.xlsx")
    if action == "exportar":
        if kind == "productos":
            contents = ops.generar_excel_productos(ops.obtener_productos())
        else:
            sales = kind == "ventas"
            schema = SALE if sales else PURCHASE
            records = ops.obtener_ventas() if sales else ops.obtener_compras()
            rows = pd.DataFrame.from_records(records, columns=schema.split()).rename(columns={
                "id": "ID", "fecha": "Fecha", "referencia": "Comprobante", "producto": "Producto",
                "cantidad": "Cantidad", "precio": "Precio unitario", "subtotal": "Subtotal", "total": "Total",
            })
            rows = rows[["ID", "Fecha", "Comprobante", "Producto", "Cantidad", "Precio unitario", "Subtotal", "Total"]]
            contents = ops.generar_excel_historial(rows, kind.title(), ("Total", "Precio unitario", "Subtotal"))
        return file_response(contents, f"{kind}.xlsx")
    content = data.get("contents")
    if content is None:
        raise HTTPException(422, "Selecciona un archivo .xlsx.")
    try:
        with ZipFile(io.BytesIO(content)) as archive:
            if sum(entry.file_size for entry in archive.infolist()) > 80_000_000:
                raise HTTPException(413, "El contenido del archivo Excel es demasiado grande.")
    except BadZipFile:
        raise HTTPException(422, "El archivo no es un libro Excel válido.") from None
    digest = hashlib.sha256(content).hexdigest()
    validated = validate(content) if kind == "productos" else validate(content, digest)
    rows, errors = validated[:2]
    if action == "validar":
        return json_response({"rows": rows[:20], "count": len(rows), "errors": errors})
    if errors or not rows:
        return json_response({"message": "Revisa el archivo antes de importar.", "errors": errors}, 422)
    if kind == "productos":
        return outcome(save(rows))
    return outcome(save(rows, digest, data["filename"], data["stock"]))


def read_action(path, request, user):
    if path == "sesion":
        return json_response(user)
    if path == "resumen":
        return json_response({
            **ops.resumen_operativo(), "productos": ops.contar_productos(),
            "unidades": ops.obtener_stock(), "alertas": table("codigo nombre stock stock_minimo", ops.obtener_alertas_stock(10)),
        })
    if path == "productos":
        return json_response(table(PRODUCT, ops.obtener_productos()))
    if path == "ventas":
        return json_response(table(SALE, reversed(ops.obtener_ventas())))
    if path == "compras":
        return json_response(table(PURCHASE, ops.obtener_compras()))
    if path == "compras/auditoria":
        return json_response({"resumen": ops.obtener_auditoria_compras(), "archivos": ops.obtener_historial_importaciones_compras()})
    if path == "usuarios":
        required_admin(user)
        return json_response(table(USER, auth.listar_usuarios()))
    if path == "analisis":
        import analysis

        movements = analysis.obtener_datos_ventas()
        alerts, days = analysis.alertas_importes_diarios(movements)
        return json_response({
            "resumen": analysis.resumen_ventas(movements),
            "tendencia": analysis.tendencia_ventas(movements),
            "productos": analysis.analisis_productos(), "destacados": analysis.productos_mas_vendidos(movements),
            "alertas": alerts, "dias_evaluados": days,
        })
    if path == "modelo":
        import prediction

        return json_response(prediction.estado_modelo())
    if path == "pronostico/pdf":
        return forecast_pdf(request.query_params)
    if path.startswith(("plantilla/", "exportar/")):
        action, kind = path.split("/", 1)
        return spreadsheet(kind, action, None)
    raise HTTPException(404, "Operación no disponible.")


def write_action(path, request, user, data):
    if path == "salir":
        request.session.clear()
        return json_response({"message": "Sesión cerrada."})
    if path in ("productos/crear", "productos/editar"):
        args = [word(data, k, optional=k == "categoria") for k in ("codigo", "nombre", "categoria")]
        args += [number(data, "precio_compra"), number(data, "precio_venta", minimum=0.01)]
        args += [number(data, k, integer=True) for k in ("stock", "stock_minimo")]
        args += [number(data, "dias_entrega", integer=True, maximum=30)]
        if path.endswith("/editar"):
            return outcome(ops.actualizar_producto(number(data, "id", integer=True, minimum=1), *args))
        return outcome(ops.registrar_producto(*args))
    if path in ("ventas/crear", "compras/crear"):
        pid = number(data, "producto_id", integer=True, minimum=1)
        qty = number(data, "cantidad", integer=True, minimum=1)
        price = None
        if data.get("precio") not in ("", None) or path.startswith("compras"):
            price = number(data, "precio", minimum=0.01)
        if path.startswith("ventas"):
            try:
                day = date.fromisoformat(data["fecha"]) if data.get("fecha") else None
            except (TypeError, ValueError):
                raise HTTPException(422, "Revisa la fecha de la venta.") from None
            return outcome(ops.registrar_venta(pid, qty, day, price, data.get("stock") is not False))
        return outcome(ops.registrar_compra(pid, qty, price))
    if path in ("productos/eliminar", "ventas/eliminar"):
        uid = number(data, "id", integer=True, minimum=1)
        if path.startswith("productos"):
            return outcome(ops.eliminar_producto(uid))
        return outcome(ops.eliminar_venta(uid, data.get("restaurar") is True))
    if path.startswith(("validar/", "importar/")):
        action, kind = path.split("/", 1)
        return spreadsheet(kind, action, data)
    if path == "pronostico":
        _, result, suggested = forecast(data)
        return json_response({**result, "reposicion": suggested})
    required_admin(user)
    if path in ("productos/vaciar", "ventas/vaciar", "reiniciar"):
        if data.get("confirmacion") != "CONFIRMAR":
            raise HTTPException(422, "Escribe CONFIRMAR para continuar.")
        if path == "productos/vaciar":
            return outcome(ops.eliminar_todos_productos())
        if path == "ventas/vaciar":
            return outcome(ops.eliminar_todas_ventas())
        database.reiniciar_datos()
        ops.invalidar_cache_operativa()
        return json_response({"message": "Datos operativos reiniciados."})
    if path == "usuarios/crear":
        password = word(data, "password")
        if len(password) < 8:
            raise HTTPException(422, "Usa al menos ocho caracteres en la contraseña.")
        auth.crear_usuario(word(data, "username"), word(data, "nombre"), password, word(data, "rol"))
        return json_response({"message": "Usuario creado."})
    if path in ("usuarios/eliminar", "usuarios/transferir"):
        uid = number(data, "id", integer=True, minimum=1)
        if path.endswith("/transferir"):
            auth.transferir_administracion_y_eliminar_usuario(user["id"], uid)
            request.session.clear()
        else:
            auth.eliminar_usuario(uid, user["id"])
        return json_response({"message": "Cuenta actualizada."})
    if path == "modelo/entrenar":
        import prediction

        return json_response(prediction.entrenar_modelo())
    raise HTTPException(404, "Operación no disponible.")


def dispatch(request, data):
    path = request.path_params["path"].strip("/")
    if path == "entrar" and request.method == "POST":
        return login(request, data)
    user = current_user(request)
    if request.method == "GET":
        return read_action(path, request, user)
    if path in ("pronostico", "salir") or path.startswith("validar/"):
        return write_action(path, request, user, data)
    with WRITE_LOCK:
        return write_action(path, request, current_user(request), data)


async def api(request):
    try:
        data = {}
        if request.method == "POST":
            if request.headers.get("x-humbertito-request") != "1":
                raise HTTPException(403, "Solicitud rechazada.")
            if int(request.headers.get("content-length", "0")) > 12_000_000:
                raise HTTPException(413, "El archivo supera el tamaño permitido.")
            if request.headers.get("content-type", "").startswith("multipart/form-data"):
                current_path = request.path_params["path"].strip("/")
                if not current_path.startswith(("validar/", "importar/")):
                    raise HTTPException(415, "Formato de solicitud no admitido.")
                await run_in_threadpool(current_user, request)
                async with request.form(max_files=1, max_fields=2) as form:
                    upload = form.get("archivo")
                    if not getattr(upload, "filename", "").lower().endswith(".xlsx"):
                        raise HTTPException(422, "Selecciona un archivo .xlsx.")
                    contents = await upload.read(10_000_001)
                    if len(contents) > 10_000_000:
                        raise HTTPException(413, "El archivo supera los 10 MB.")
                    data = {"contents": contents, "filename": upload.filename, "stock": form.get("stock") == "true"}
            else:
                if not request.headers.get("content-type", "").startswith("application/json"):
                    raise HTTPException(415, "Se esperaba una solicitud JSON.")
                data = await request.json()
                if not isinstance(data, dict):
                    raise HTTPException(422, "Revisa el formato de la solicitud.")
        return await run_in_threadpool(dispatch, request, data)
    except HTTPException as error:
        return json_response({"message": error.detail}, error.status_code)
    except ValueError as error:
        return json_response({"message": str(error)}, 422)
    except Exception:
        LOG.exception("Error en la API de Humbertito")
        return json_response({"message": "No se pudo completar la operación. Inténtalo nuevamente."}, 500)


@asynccontextmanager
async def lifespan(_app):
    await run_in_threadpool(initialize_database)
    yield


def initialize_database():
    if not database.usar_supabase():
        database.crear_base_datos()
    return auth.inicializar()


def bootstrap_admin():
    from getpass import getpass

    initialize_database()
    if auth.cantidad_usuarios():
        raise SystemExit("Ya existe una cuenta administradora.")
    username = input("Usuario: ").strip()
    name = input("Nombre completo: ").strip()
    password = getpass("Contraseña: ")
    if len(password) < 8 or password != getpass("Confirma la contraseña: "):
        raise SystemExit("La contraseña debe coincidir y tener al menos ocho caracteres.")
    auth.crear_usuario(username, name, password, "admin")
    print("Cuenta administradora creada.")


def create_app():
    secret = os.environ.get("HUMBERTITO_SESSION_SECRET", "")
    if len(secret) < 32:
        raise RuntimeError("Configura HUMBERTITO_SESSION_SECRET con al menos 32 caracteres aleatorios.")
    app = Starlette(routes=[Route("/api/{path:path}", api, methods=["GET", "POST"])], lifespan=lifespan)
    app.add_middleware(
        SessionMiddleware, secret_key=secret, session_cookie="humbertito",
        same_site="lax", https_only=os.environ.get("HUMBERTITO_SECURE_COOKIES") == "1", max_age=28800,
    )
    return app



if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Administración de Humbertito")
    parser.add_argument("command", choices=["crear-admin"])
    parser.parse_args()
    bootstrap_admin()
