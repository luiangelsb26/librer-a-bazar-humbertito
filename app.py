import io
import sys
import streamlit as st
import importlib
import math
import hashlib
import re
import unicodedata
from datetime import datetime
from html import escape
from pathlib import Path
from time import perf_counter
import database
import auth

if not hasattr(database, "reiniciar_datos"):
    database = importlib.reload(database)

# ==========================================================
# CONFIGURACIÓN
# ==========================================================

st.set_page_config(
    page_title="Librería Bazar Humbertito",
    page_icon=":material/menu_book:",
    layout="wide"
)


def notificar_exito(mensaje):
    notificaciones = st.session_state.setdefault(
        "_notificaciones_exito",
        [],
    )
    notificaciones.append(mensaje)


def mostrar_grafico_fijo(figura, clave):
    """Mantiene la navegación fija y deja que Streamlit coloree los ejes."""
    figura.update_xaxes(fixedrange=True)
    figura.update_yaxes(fixedrange=True)
    figura.update_layout(dragmode=False)
    st.plotly_chart(
        figura,
        config={
            "scrollZoom": False,
            "displayModeBar": False,
            "displaylogo": False,
            "responsive": True,
        },
        key=clave,
        theme="streamlit",
        width="stretch",
        height=430,
    )


def formatear_numero_es(valor, decimales=0):
    """Usa punto para miles y coma para decimales, como en formato local."""
    numero = f"{float(valor):,.{decimales}f}"
    return numero.replace(",", "\0").replace(".", ",").replace("\0", ".")


def formatear_soles(valor):
    return f"S/ {formatear_numero_es(valor, 2)}"


def mostrar_tabla(datos, *, height="content", **opciones):
    """Muestra tablas navegables sin reservar espacio para filas vacías."""
    import pandas as pd

    marco = datos if isinstance(datos, pd.DataFrame) else pd.DataFrame(datos)
    alto_fila = 36
    if height == "content":
        height = "auto"
    else:
        height = min(height, 42 + alto_fila * max(1, len(marco)))

    return st.dataframe(
        marco,
        height=height,
        row_height=alto_fila,
        lazy=len(marco) > 1000,
        **opciones,
    )


for mensaje_notificacion in st.session_state.pop(
    "_notificaciones_exito",
    [],
):
    st.toast(
        mensaje_notificacion,
        icon=":material/check_circle:",
    )


database.configurar_desde_streamlit()


def seleccionar_modulo(nombre):
    """Cambia el módulo antes del rerun natural del clic de navegación."""
    st.session_state.menu = nombre


def invalidar_cache_operativa():
    """Refresca solo lecturas del negocio, conservando cachés de plantillas."""
    funciones_app = (
        "contar_productos",
        "obtener_stock",
        "obtener_productos",
        "obtener_ventas",
        "obtener_compras",
        "obtener_auditoria_compras",
        "obtener_historial_importaciones_compras",
        "resumen_dashboard",
        "obtener_alertas_stock",
        "validar_ventas_excel",
        "validar_compras_excel",
    )
    for nombre in funciones_app:
        funcion = globals().get(nombre)
        if callable(funcion) and hasattr(funcion, "clear"):
            funcion.clear()

    # Estos módulos se importan solo en las secciones que los necesitan.
    invalidaciones_por_modulo = {
        "analysis": (
            "obtener_datos_ventas",
            "productos_stock_bajo",
            "analisis_productos",
        ),
        "prediction": (
            "obtener_productos",
            "_obtener_ventas_diarias",
            "estado_modelo",
        ),
    }
    for nombre_modulo, nombres_funciones in invalidaciones_por_modulo.items():
        modulo = sys.modules.get(nombre_modulo)
        if modulo is None:
            continue
        for nombre in nombres_funciones:
            funcion = getattr(modulo, nombre, None)
            if callable(funcion) and hasattr(funcion, "clear"):
                funcion.clear()


st.html(Path(__file__).with_name("interfaz.css"))

@st.cache_resource(ttl=300, show_spinner=False)
def preparar_tabla_usuarios():
    """Prepara la autenticación y refresca en segundo plano al vencer."""
    return auth.inicializar()

# La base no se consulta al cargar la página de acceso.
# Se conecta únicamente al iniciar sesión o crear el primer administrador.

# ==========================================================
# AUTENTICACIÓN Y CONTROL DE ACCESO
# ==========================================================

def contar_usuarios_acceso():
    """Usa el conteo obtenido al preparar la conexión de autenticación."""
    return preparar_tabla_usuarios()

@st.cache_data(ttl=15, show_spinner=False, max_entries=1)
def obtener_usuarios_administracion_cache():
    """Reutiliza la lista de usuarios entre reruns y se limpia al modificarla."""
    return auth.listar_usuarios()


def pantalla_acceso():
    try:
        administradores_activos = contar_usuarios_acceso()
    except Exception:
        administradores_activos = None


    with st.container(key="access_shell"):
        brand_column, access_column = st.columns(
            [1.03, 0.97],
            vertical_alignment="center",
            gap=None,
        )
        with brand_column:
            st.markdown(
                """
                <section class="login-brand">
                    <div class="login-brand-head">
                        <div class="login-brand-mark" aria-hidden="true">
                            <svg viewBox="0 0 32 32" focusable="false">
                                <path d="M16 8.2c-3.6-2.1-7.3-2.1-11-.8v16.8c3.7-1.3 7.4-1.3 11 .8m0-16.8c3.6-2.1 7.3-2.1 11-.8v16.8c-3.7-1.3-7.4-1.3-11 .8m0-16.8v16.8"/>
                                <path d="M8.5 12.1c1.7-.3 3.3 0 4.8.7m-4.8 3c1.7-.3 3.3 0 4.8.7m8.2-3.7c1.4-.7 3.1-1 4.8-.7m-4.8 3.7c1.4-.7 3.1-1 4.8-.7"/>
                            </svg>
                        </div>
                        <div class="login-brand-identity">
                            <div class="login-brand-kicker">Sistema de gestión</div>
                            <div class="login-brand-name">Librería Bazar</div>
                            <div class="login-brand-name-strong">Humbertito</div>
                        </div>
                    </div>
                    <div class="login-brand-title">Gestiona tu librería</div>
                    <p class="login-brand-subtitle">
                        Registra ventas, controla el stock y consulta tus compras
                        desde el mismo lugar.
                    </p>
                    <div class="login-brand-features">
                        <span class="login-brand-feature">Inventario</span>
                        <span class="login-brand-feature">Ventas</span>
                        <span class="login-brand-feature">Compras</span>
                    </div>
                </section>
                """,
                unsafe_allow_html=True,
            )

        with access_column:
            configurar_admin = administradores_activos == 0
            if configurar_admin:
                with st.form("crear_primer_admin", border=False):
                    st.caption("Configuración inicial")
                    st.title("Crear administrador")
                    st.write("Crea la cuenta principal para administrar Humbertito.")
                    nombre = st.text_input("Nombre completo", autocomplete="name")
                    username = st.text_input("Usuario", autocomplete="username")
                    password = st.text_input("Contraseña", type="password")
                    confirmar = st.text_input("Confirmar contraseña", type="password")
                    enviar = st.form_submit_button(
                        "Crear administrador",
                        type="primary",
                        width="stretch",
                    )

                if enviar:
                    if password != confirmar:
                        st.error("Las contraseñas no coinciden.")
                    else:
                        try:
                            preparar_tabla_usuarios.clear()
                            cantidad = contar_usuarios_acceso()
                            if cantidad != 0:
                                st.error("Ya existe una cuenta administradora activa. Inicia sesión.")
                            else:
                                auth.crear_usuario(username, nombre, password, "admin")
                                preparar_tabla_usuarios.clear()
                                notificar_exito("Administrador creado. Inicia sesión.")
                                st.rerun()
                        except ValueError as error:
                            st.error(str(error))
                        except Exception:
                            st.error(
                                "No se pudo conectar con la base de datos. "
                                "Vuelve a intentarlo en unos segundos."
                            )

            else:
                with st.form("form_login", border=False):
                    st.caption("Acceso al sistema")
                    st.title("Iniciar sesión")
                    st.write("Ingresa con la cuenta de tu librería.")
                    username = st.text_input("Usuario", autocomplete="username")
                    password = st.text_input(
                        "Contraseña", type="password", autocomplete="current-password"
                    )
                    entrar = st.form_submit_button(
                        "Iniciar sesión",
                        icon=":material/login:",
                        type="primary",
                        width="stretch",
                    )

                if entrar and (not username or not username.strip() or not password):
                    st.warning("Ingresa tu usuario y contraseña para continuar.")
                elif entrar:
                    try:
                        with st.spinner("Verificando tus datos de acceso..."):
                            usuario = auth.verificar_usuario(username, password)
                        if usuario:
                            st.session_state["usuario"] = usuario
                            st.session_state["menu"] = "Inicio"
                            st.rerun()
                        else:
                            st.error(
                                "Usuario o contraseña incorrectos. "
                                "Revisa tus datos e inténtalo de nuevo."
                            )
                    except Exception as error:
                        st.error(
                            "No se pudo conectar con la base de datos. "
                            "Revisa la conexión e inténtalo otra vez."
                        )
                        st.caption(
                            "Diagnóstico técnico: "
                            f"{type(error).__name__}."
                        )


if "usuario" not in st.session_state:
    pantalla_acceso()
    st.stop()


def normalizar_usuario(usuario):
    """Convierte el usuario de autenticación a un diccionario compatible."""
    if usuario is None:
        return None

    if isinstance(usuario, dict):
        return {
            "id": usuario.get("id"),
            "username": usuario.get("username", ""),
            "nombre": usuario.get("nombre", ""),
            "rol": usuario.get("rol", "empleado"),
            "activo": usuario.get("activo", 1),
        }

    if isinstance(usuario, (tuple, list)):
        datos = list(usuario)

        # Formato habitual: id, username, nombre, rol, activo
        if len(datos) >= 5 and str(datos[3]).lower() in ("admin", "empleado"):
            return {
                "id": datos[0],
                "username": datos[1],
                "nombre": datos[2],
                "rol": str(datos[3]).lower(),
                "activo": datos[4],
            }

        # Formato alternativo: id, username, nombre, password, rol, activo
        if len(datos) >= 6 and str(datos[4]).lower() in ("admin", "empleado"):
            return {
                "id": datos[0],
                "username": datos[1],
                "nombre": datos[2],
                "rol": str(datos[4]).lower(),
                "activo": datos[5],
            }

        # Último recurso: localizar el rol dentro de la fila.
        for indice, valor in enumerate(datos):
            if str(valor).lower() in ("admin", "empleado"):
                return {
                    "id": datos[0] if len(datos) > 0 else None,
                    "username": datos[1] if len(datos) > 1 else "",
                    "nombre": datos[2] if len(datos) > 2 else "",
                    "rol": str(valor).lower(),
                    "activo": 1,
                }

    return None


# Normalizar también sesiones antiguas que hayan guardado una tupla.
usuario_actual = normalizar_usuario(st.session_state.get("usuario"))

if usuario_actual is None:
    st.session_state.pop("usuario", None)
    st.session_state.pop("menu", None)
    pantalla_acceso()
    st.stop()

st.session_state["usuario"] = usuario_actual
es_admin = usuario_actual.get("rol", "empleado") == "admin"

if not database.usar_supabase():
    st.warning(
        "La app está usando SQLite local. Configura SUPABASE_DB_URL "
        "en los Secrets de Streamlit Cloud para usar la base persistente."
    )


# Las tablas operativas no bloquean la pantalla de acceso; se preparan al entrar.
@st.cache_resource(show_spinner=False)
def preparar_esquema_sistema():
    """Prepara el esquema operativo una sola vez por proceso."""
    if not database.usar_supabase():
        database.crear_base_datos()
    return True


preparar_esquema_sistema()

# pandas se usa en módulos operativos, no en la pantalla de inicio de sesión.


# ==========================================================
# CONEXIÓN A LA BASE DE DATOS
# ==========================================================

def conectar():
    return database.conectar()


# ==========================================================
# CONSULTAS GENERALES
# ==========================================================

@st.cache_data(ttl=120, show_spinner=False, max_entries=1)
def contar_productos():
    con = conectar()
    try:
        return con.execute("SELECT COUNT(*) FROM productos").fetchone()[0]
    finally:
        con.close()

@st.cache_data(ttl=120, show_spinner=False, max_entries=1)
def obtener_stock():
    con = conectar()
    try:
        return con.execute("SELECT COALESCE(SUM(stock), 0) FROM productos").fetchone()[0]
    finally:
        con.close()

@st.cache_data(ttl=60, show_spinner=False, max_entries=1)
def obtener_productos():
    con = conectar()
    try:
        cur = con.cursor()
        cur.execute("""
            SELECT id, codigo, nombre, categoria, precio_compra, precio_venta,
                   stock, stock_minimo, dias_entrega
            FROM productos
            ORDER BY id ASC
        """)
        return cur.fetchall()
    finally:
        con.close()

@st.cache_data(ttl=60, show_spinner=False, max_entries=3)
def generar_excel_productos(productos):
    columnas = [
        "ID",
        "Código",
        "Producto",
        "Categoría",
        "Precio compra (S/)",
        "Precio venta (S/)",
        "Stock",
        "Stock mínimo",
        "Días de entrega",
    ]
    filas = [
        {
            "ID": p[0],
            "Código": p[1],
            "Producto": p[2],
            "Categoría": p[3] or "",
            "Precio compra (S/)": p[4],
            "Precio venta (S/)": p[5],
            "Stock": p[6],
            "Stock mínimo": p[7],
            "Días de entrega": p[8],
        }
        for p in productos
    ]

    archivo = io.BytesIO()
    with pd.ExcelWriter(archivo, engine="openpyxl") as escritor:
        pd.DataFrame(filas, columns=columnas).to_excel(
            escritor,
            index=False,
            sheet_name="Productos",
        )
        hoja = escritor.sheets["Productos"]
        hoja.freeze_panes = "A2"
        hoja.auto_filter.ref = hoja.dimensions

        anchos = {
            "A": 10,
            "B": 18,
            "C": 34,
            "D": 24,
            "E": 20,
            "F": 20,
            "G": 12,
            "H": 16,
            "I": 18,
        }
        for columna, ancho in anchos.items():
            hoja.column_dimensions[columna].width = ancho

        if filas:
            from openpyxl.worksheet.table import Table, TableStyleInfo

            tabla = Table(
                displayName="TablaProductos",
                ref=hoja.dimensions,
            )
            tabla.tableStyleInfo = TableStyleInfo(
                name="TableStyleMedium2",
                showFirstColumn=False,
                showLastColumn=False,
                showRowStripes=True,
                showColumnStripes=False,
            )
            hoja.add_table(tabla)

    archivo.seek(0)
    return archivo.getvalue()


@st.cache_data(ttl=60, show_spinner=False, max_entries=3)
def crear_plantilla_productos_excel():
    """Genera una plantilla para registrar productos desde Excel."""
    columnas = [
        "ID",
        "Código",
        "Producto",
        "Categoría",
        "Precio compra (S/)",
        "Precio venta (S/)",
        "Stock",
        "Stock mínimo",
        "Días de entrega",
    ]
    archivo = io.BytesIO()
    with pd.ExcelWriter(archivo, engine="openpyxl") as escritor:
        pd.DataFrame(columns=columnas).to_excel(
            escritor,
            index=False,
            sheet_name="Productos",
        )
        hoja = escritor.sheets["Productos"]
        hoja.freeze_panes = "A2"
        hoja.auto_filter.ref = "A1:I1"
        for columna, ancho in {
            "A": 10,
            "B": 20,
            "C": 34,
            "D": 26,
            "E": 20,
            "F": 20,
            "G": 12,
            "H": 16,
            "I": 18,
        }.items():
            hoja.column_dimensions[columna].width = ancho

        pd.DataFrame({
            "Instrucciones": [
                "Una fila por producto; no cambies los encabezados.",
                "ID es opcional: conserva el ID exportado para actualizar el mismo producto; déjalo vacío para uno nuevo.",
                "Código y Producto son obligatorios y el código debe ser único.",
                "Precio compra y Precio venta deben ser números no negativos; la venta debe ser mayor que cero.",
                "Stock y Stock mínimo deben ser números enteros no negativos.",
                "Días de entrega es opcional; usa un entero entre 0 y 30 y, si queda vacío, conserva el valor actual o usa 0 para productos nuevos.",
                "Categoría puede quedar vacía. Si Stock mínimo queda vacío, se usará 5.",
                "No incluyas filas de totales ni resúmenes debajo de los productos.",
            ]
        }).to_excel(escritor, index=False, sheet_name="Instrucciones")
        escritor.sheets["Instrucciones"].column_dimensions["A"].width = 105

    archivo.seek(0)
    return archivo.getvalue()


def validar_productos_excel(contenido):
    """Valida el catálogo de productos de Excel sin modificar la base de datos."""
    try:
        original = pd.read_excel(io.BytesIO(contenido), sheet_name=0)
    except Exception as e:
        return [], [f"No se pudo leer el archivo Excel: {e}"]

    if original.empty:
        return [], ["La primera hoja no contiene productos."]

    alias = {
        "id": {"id", "id producto", "identificador"},
        "codigo": {"codigo", "codigo producto", "codigo del producto", "sku"},
        "nombre": {"producto", "nombre", "nombre producto", "nombre del producto"},
        "categoria": {"categoria", "category"},
        "precio_compra": {
            "precio compra", "precio compra s", "precio de compra", "costo",
            "costo unitario", "precio costo",
        },
        "precio_venta": {
            "precio venta", "precio venta s", "precio de venta",
            "precio de venta s", "precio",
        },
        "stock": {"stock", "stock inicial", "existencias"},
        "stock_minimo": {
            "stock minimo", "stock min", "minimo", "stock minimo recomendado",
        },
        "dias_entrega": {
            "dias entrega", "dias de entrega", "plazo entrega",
            "dias entrega proveedor", "plazo proveedor",
        },
    }
    columnas = {}
    for columna in original.columns:
        encabezado = _normalizar_encabezado_excel(columna)
        for campo, nombres in alias.items():
            if encabezado in nombres:
                columnas[campo] = columna

    requeridos = [
        "codigo", "nombre", "precio_compra", "precio_venta", "stock",
    ]
    faltantes = [campo for campo in requeridos if campo not in columnas]
    if faltantes:
        nombres = {
            "codigo": "Código",
            "nombre": "Producto",
            "precio_compra": "Precio compra",
            "precio_venta": "Precio venta",
            "stock": "Stock",
        }
        return [], [
            "Faltan columnas requeridas: "
            + ", ".join(nombres[campo] for campo in faltantes)
            + ". Descarga la plantilla para ver los encabezados aceptados."
        ]

    productos_existentes = obtener_productos()
    existentes_por_id = {producto[0]: producto for producto in productos_existentes}
    existentes_por_codigo = {
        str(producto[1]).strip().casefold(): producto
        for producto in productos_existentes
    }
    codigos_archivo = set()
    ids_archivo = set()
    filas_validas = []
    errores = []

    for numero_fila, (_, fila) in enumerate(original.iterrows(), start=2):
        if all(pd.isna(valor) or str(valor).strip() == "" for valor in fila):
            continue

        errores_fila = []

        id_producto = None
        if "id" in columnas:
            valor_id = fila[columnas["id"]]
            if not pd.isna(valor_id) and str(valor_id).strip():
                numero_id = _numero_excel(valor_id)
                if (
                    numero_id is None
                    or numero_id <= 0
                    or not numero_id.is_integer()
                ):
                    errores_fila.append("ID debe ser un entero positivo")
                else:
                    id_producto = int(numero_id)
                    if id_producto in ids_archivo:
                        errores_fila.append(
                            f"el ID {id_producto} está repetido en el Excel"
                        )
                    ids_archivo.add(id_producto)

        valor_codigo = fila[columnas["codigo"]]
        if pd.isna(valor_codigo) or not str(valor_codigo).strip():
            codigo = ""
            errores_fila.append("falta el código")
        elif isinstance(valor_codigo, float) and valor_codigo.is_integer():
            codigo = str(int(valor_codigo))
        else:
            codigo = str(valor_codigo).strip()

        clave_codigo = codigo.casefold()
        producto_actual = (
            existentes_por_id.get(id_producto)
            if id_producto is not None
            else existentes_por_codigo.get(clave_codigo)
        )
        if clave_codigo:
            if clave_codigo in codigos_archivo:
                errores_fila.append(f"el código {codigo} está repetido en el Excel")
            codigos_archivo.add(clave_codigo)

            producto_por_codigo = existentes_por_codigo.get(clave_codigo)
            producto_por_id = existentes_por_id.get(id_producto)
            if id_producto is None and producto_por_codigo:
                errores_fila.append(
                    f"el código {codigo} ya está registrado con ID "
                    f"{producto_por_codigo[0]}; conserva ese ID en el Excel para actualizarlo"
                )
            elif id_producto is not None and producto_por_id:
                if str(producto_por_id[1]).strip().casefold() != clave_codigo:
                    errores_fila.append(
                        f"el ID {id_producto} ya pertenece al código "
                        f"{producto_por_id[1]}"
                    )
            elif producto_por_codigo and producto_por_codigo[0] != id_producto:
                errores_fila.append(
                    f"el código {codigo} ya pertenece al ID "
                    f"{producto_por_codigo[0]}"
                )

        valor_nombre = fila[columnas["nombre"]]
        nombre = "" if pd.isna(valor_nombre) else str(valor_nombre).strip()
        if not nombre:
            errores_fila.append("falta el nombre del producto")

        def valor_numerico(campo, etiqueta, predicado, mensaje):
            numero = _numero_excel(fila[columnas[campo]])
            if numero is None or not predicado(numero):
                errores_fila.append(f"{etiqueta} {mensaje}")
                return None
            return numero

        precio_compra = valor_numerico(
            "precio_compra", "Precio compra", lambda n: n >= 0,
            "debe ser un número mayor o igual a cero",
        )
        precio_venta = valor_numerico(
            "precio_venta", "Precio venta", lambda n: n > 0,
            "debe ser mayor que cero",
        )
        stock = valor_numerico(
            "stock", "Stock", lambda n: n >= 0 and n.is_integer(),
            "debe ser un entero no negativo",
        )

        valor_stock_minimo = (
            fila[columnas["stock_minimo"]]
            if "stock_minimo" in columnas
            else None
        )
        stock_minimo = (
            5.0 if pd.isna(valor_stock_minimo) or str(valor_stock_minimo).strip() == ""
            else _numero_excel(valor_stock_minimo)
        )
        if (
            stock_minimo is None
            or stock_minimo < 0
            or not stock_minimo.is_integer()
        ):
            errores_fila.append("Stock mínimo debe ser un entero no negativo")
            stock_minimo = None

        valor_dias_entrega = (
            fila[columnas["dias_entrega"]]
            if "dias_entrega" in columnas
            else None
        )
        if (
            pd.isna(valor_dias_entrega)
            or str(valor_dias_entrega).strip() == ""
        ):
            dias_entrega = (
                int(producto_actual[8])
                if producto_actual is not None and len(producto_actual) > 8
                else 0
            )
        else:
            dias_entrega_numero = _numero_excel(valor_dias_entrega)
            if (
                dias_entrega_numero is None
                or not dias_entrega_numero.is_integer()
                or not 0 <= dias_entrega_numero <= 30
            ):
                errores_fila.append(
                    "Días de entrega debe ser un entero entre 0 y 30"
                )
                dias_entrega = None
            else:
                dias_entrega = int(dias_entrega_numero)

        valor_categoria = (
            fila[columnas["categoria"]]
            if "categoria" in columnas
            else ""
        )
        categoria = (
            "" if pd.isna(valor_categoria) else str(valor_categoria).strip()
        )

        if (
            errores_fila
            or precio_compra is None
            or precio_venta is None
            or stock is None
            or stock_minimo is None
            or dias_entrega is None
        ):
            if not errores_fila:
                errores_fila.append("hay valores de producto que no se pudieron validar")
            errores.extend(
                f"Fila {numero_fila}: {error}." for error in errores_fila
            )
            continue

        filas_validas.append({
            "id": id_producto,
            "codigo": codigo,
            "nombre": nombre,
            "categoria": categoria,
            "precio_compra": round(precio_compra, 2),
            "precio_venta": round(precio_venta, 2),
            "stock": int(stock),
            "stock_minimo": int(stock_minimo),
            "dias_entrega": dias_entrega,
            "fila_excel": numero_fila,
        })

    if not filas_validas and not errores:
        errores.append("No se encontraron filas de productos para importar.")
    return filas_validas, errores


# ==========================================================
# PRODUCTOS
# ==========================================================

def registrar_producto(
    codigo,
    nombre,
    categoria,
    precio_compra,
    precio_venta,
    stock,
    stock_minimo,
    dias_entrega=0,
):
    con = conectar()

    try:
        con.execute("""
            INSERT INTO productos (
                codigo,
                nombre,
                categoria,
                precio_compra,
                precio_venta,
                stock,
                stock_minimo,
                dias_entrega
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            codigo,
            nombre,
            categoria,
            precio_compra,
            precio_venta,
            stock,
            stock_minimo,
            dias_entrega,
        ))

        con.commit()
        invalidar_cache_operativa()
        return True, "Producto registrado correctamente."

    except Exception as e:
        if database.es_error_integridad(e):
            return False, "El código del producto ya existe."
        return False, f"Error: {e}"

    finally:
        con.close()


def actualizar_producto(
    producto_id,
    codigo,
    nombre,
    categoria,
    precio_compra,
    precio_venta,
    stock,
    stock_minimo,
    dias_entrega=0,
):
    con = conectar()

    try:
        cursor = con.execute("""
            UPDATE productos
            SET codigo = ?,
                nombre = ?,
                categoria = ?,
                precio_compra = ?,
                precio_venta = ?,
                stock = ?,
                stock_minimo = ?,
                dias_entrega = ?
            WHERE id = ?
        """, (
            codigo,
            nombre,
            categoria,
            precio_compra,
            precio_venta,
            stock,
            stock_minimo,
            dias_entrega,
            producto_id,
        ))
        con.commit()
        invalidar_cache_operativa()

        if cursor.rowcount == 0:
            return False, "No se encontró el producto seleccionado."

        return True, "Producto actualizado correctamente."

    except Exception as e:
        if database.es_error_integridad(e):
            return False, "Ese código ya está asignado a otro producto."
        return False, f"No se pudo actualizar el producto: {e}"

    finally:
        con.close()


def eliminar_producto(producto_id):
    con = conectar()

    try:
        ventas_asociadas = con.execute(
            "SELECT COUNT(*) FROM detalle_ventas WHERE producto_id = ?",
            (producto_id,),
        ).fetchone()[0]
        compras_asociadas = con.execute(
            "SELECT COUNT(*) FROM detalle_compras WHERE producto_id = ?",
            (producto_id,),
        ).fetchone()[0]

        if ventas_asociadas or compras_asociadas:
            return (
                False,
                "No se puede eliminar porque el producto tiene movimientos "
                "de venta o compra. Puedes editar sus datos y conservar el historial.",
            )

        cursor = con.execute(
            "DELETE FROM productos WHERE id = ?",
            (producto_id,),
        )
        con.commit()
        invalidar_cache_operativa()

        if cursor.rowcount == 0:
            return False, "No se encontró el producto seleccionado."

        return True, "Producto eliminado correctamente."

    except Exception as e:
        return False, f"No se pudo eliminar el producto: {e}"

    finally:
        con.close()


def importar_productos_excel(filas):
    """Importa o actualiza por ID todos los productos en una transacción."""
    con = conectar()
    try:
        for fila in filas:
            valores = (
                fila["codigo"],
                fila["nombre"],
                fila["categoria"],
                fila["precio_compra"],
                fila["precio_venta"],
                fila["stock"],
                fila["stock_minimo"],
                fila.get("dias_entrega", 0),
            )
            id_producto = fila.get("id")
            if id_producto is not None:
                existente = con.execute(
                    "SELECT codigo FROM productos WHERE id = ?",
                    (id_producto,),
                ).fetchone()
                if existente:
                    if str(existente[0]).strip().casefold() != fila["codigo"].casefold():
                        raise ValueError(
                            f"El ID {id_producto} ya pertenece a "
                            f"{existente[0]}; no se modificó ningún producto."
                        )
                    con.execute(
                        """
                        UPDATE productos SET
                            codigo = ?, nombre = ?, categoria = ?,
                            precio_compra = ?, precio_venta = ?, stock = ?,
                            stock_minimo = ?, dias_entrega = ?
                        WHERE id = ?
                        """,
                        (*valores, id_producto),
                    )
                else:
                    codigo_existente = con.execute(
                        "SELECT id FROM productos WHERE LOWER(codigo) = LOWER(?)",
                        (fila["codigo"],),
                    ).fetchone()
                    if codigo_existente:
                        raise ValueError(
                            f"El código {fila['codigo']} ya pertenece al ID "
                            f"{codigo_existente[0]}; no se modificó ningún producto."
                        )
                    con.execute(
                        """
                        INSERT INTO productos (
                            id, codigo, nombre, categoria, precio_compra,
                            precio_venta, stock, stock_minimo, dias_entrega
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (id_producto, *valores),
                    )
            else:
                codigo_existente = con.execute(
                    "SELECT id FROM productos WHERE LOWER(codigo) = LOWER(?)",
                    (fila["codigo"],),
                ).fetchone()
                if codigo_existente:
                    raise ValueError(
                        f"El código {fila['codigo']} ya existe con ID "
                        f"{codigo_existente[0]}; no se modificó ningún producto."
                    )
                con.execute(
                    """
                    INSERT INTO productos (
                        codigo, nombre, categoria, precio_compra, precio_venta,
                        stock, stock_minimo, dias_entrega
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    valores,
                )

        if database.usar_supabase():
            con.execute(
                """
                SELECT setval(
                    pg_get_serial_sequence('productos', 'id'),
                    COALESCE((SELECT MAX(id) FROM productos), 1),
                    EXISTS(SELECT 1 FROM productos)
                )
                """
            )
        con.commit()
        invalidar_cache_operativa()
        return True, (
            f"Se procesaron {len(filas)} productos. Los IDs incluidos en el "
            "Excel se conservaron; los vacíos se asignaron automáticamente."
        )
    except Exception as e:
        con.rollback()
        if database.es_error_integridad(e):
            return False, "No se importó ningún producto porque hay códigos repetidos."
        return False, f"No se pudieron importar los productos: {e}"
    finally:
        con.close()


def eliminar_todos_productos():
    """Elimina el catálogo solo si no tiene ventas ni compras asociadas."""
    con = conectar()
    try:
        cantidad_productos = con.execute(
            "SELECT COUNT(*) FROM productos"
        ).fetchone()[0]
        if not cantidad_productos:
            return False, "No hay productos registrados para eliminar."

        ventas_asociadas = con.execute(
            "SELECT COUNT(*) FROM detalle_ventas"
        ).fetchone()[0]
        compras_asociadas = con.execute(
            "SELECT COUNT(*) FROM detalle_compras"
        ).fetchone()[0]
        if ventas_asociadas or compras_asociadas:
            return False, (
                "No se eliminó ningún producto para proteger el historial. "
                f"Hay {ventas_asociadas} detalle(s) de venta y "
                f"{compras_asociadas} detalle(s) de compra asociados. "
                "Elimina o conserva esos movimientos antes de borrar el catálogo."
            )

        con.execute("DELETE FROM productos")
        if database.usar_supabase():
            con.execute(
                "SELECT setval(pg_get_serial_sequence('productos', 'id'), 1, false)"
            )
        else:
            con.execute(
                "DELETE FROM sqlite_sequence WHERE name = 'productos'"
            )
        con.commit()
        invalidar_cache_operativa()
        return True, f"Se eliminaron {cantidad_productos} productos."
    except Exception as e:
        con.rollback()
        return False, f"No se pudieron eliminar los productos: {e}"
    finally:
        con.close()


# ==========================================================
# VENTAS
# ==========================================================

@st.cache_data(ttl=60, show_spinner=False, max_entries=3)
def crear_plantilla_ventas_excel():
    """Genera una plantilla vacía para importar ventas históricas."""
    archivo = io.BytesIO()
    columnas = [
        "Fecha",
        "Código del producto",
        "Cantidad",
        "Precio unitario (S/)",
        "N° Boleta",
    ]

    with pd.ExcelWriter(archivo, engine="openpyxl") as escritor:
        pd.DataFrame(columns=columnas).to_excel(
            escritor,
            index=False,
            sheet_name="Ventas",
        )
        hoja = escritor.sheets["Ventas"]
        hoja.freeze_panes = "A2"
        hoja.auto_filter.ref = "A1:E1"
        for columna, ancho in {"A": 18, "B": 24, "C": 12, "D": 22, "E": 18}.items():
            hoja.column_dimensions[columna].width = ancho

        pd.DataFrame({
            "Instrucciones": [
                "Registra una fila por cada producto vendido.",
                "Usa la fecha impresa en la boleta; no se aceptan fechas futuras.",
                "El código debe coincidir con el catálogo de productos del sistema.",
                "Cantidad debe ser un entero mayor que cero.",
                "Usa el precio unitario que figura en la boleta.",
                "N° Boleta es opcional; repite el mismo número para agrupar sus productos.",
                "No agregues totales ni filas de resumen debajo de las ventas.",
            ]
        }).to_excel(escritor, index=False, sheet_name="Instrucciones")
        escritor.sheets["Instrucciones"].column_dimensions["A"].width = 100

    archivo.seek(0)
    return archivo.getvalue()


def _normalizar_encabezado_excel(valor):
    texto = unicodedata.normalize("NFKD", str(valor))
    texto = "".join(caracter for caracter in texto if not unicodedata.combining(caracter))
    return re.sub(r"[^a-z0-9]+", " ", texto.lower()).strip()


def _numero_excel(valor):
    if pd.isna(valor):
        return None
    if isinstance(valor, (int, float)):
        return float(valor)

    texto = re.sub(r"[^0-9,.-]", "", str(valor).strip())
    if not texto:
        return None
    if "," in texto and "." in texto:
        if texto.rfind(",") > texto.rfind("."):
            texto = texto.replace(".", "").replace(",", ".")
        else:
            texto = texto.replace(",", "")
    elif "," in texto:
        texto = texto.replace(",", ".")
    try:
        return float(texto)
    except ValueError:
        return None


@st.cache_data(ttl=180, show_spinner=False, max_entries=6)
def validar_ventas_excel(_contenido, hash_contenido):
    """Lee y valida el Excel sin modificar la base de datos."""
    try:
        original = pd.read_excel(io.BytesIO(_contenido), sheet_name=0)
    except Exception as e:
        return [], [f"No se pudo leer el archivo Excel: {e}"], pd.DataFrame()

    if original.empty:
        return [], ["La primera hoja no contiene filas de ventas."], original

    encabezados = {
        "fecha": {"fecha", "fecha de venta", "fecha boleta"},
        "codigo": {"codigo", "codigo producto", "codigo del producto", "sku"},
        "producto": {"producto", "nombre producto", "nombre del producto"},
        "cantidad": {"cantidad", "unidades"},
        "precio": {
            "precio unitario", "precio unitario s", "precio de venta", "precio venta", "precio"
        },
        "boleta": {
            "boleta", "numero boleta", "numero de boleta", "n boleta",
            "nro boleta", "ticket", "comprobante", "referencia"
        },
    }
    columnas = {}
    for columna in original.columns:
        normalizado = _normalizar_encabezado_excel(columna)
        for campo, alias in encabezados.items():
            if normalizado in alias:
                columnas[campo] = columna

    requeridos = ["fecha", "cantidad", "precio"]
    faltantes = [campo for campo in requeridos if campo not in columnas]
    if "codigo" not in columnas and "producto" not in columnas:
        faltantes.append("Código del producto o Producto")
    if faltantes:
        return [], [
            "Faltan columnas requeridas: " + ", ".join(faltantes) + ". "
            "Descarga la plantilla para ver los encabezados aceptados."
        ], original

    productos = obtener_productos()
    por_codigo = {str(producto[1]).strip().casefold(): producto for producto in productos}
    por_nombre = {}
    for producto in productos:
        por_nombre.setdefault(str(producto[2]).strip().casefold(), []).append(producto)

    filas_validas = []
    errores = []
    hoy = datetime.now().date()

    for numero_fila, (_, fila) in enumerate(original.iterrows(), start=2):
        valores = [fila[columna] for columna in original.columns]
        if all(pd.isna(valor) or str(valor).strip() == "" for valor in valores):
            continue

        errores_fila = []
        producto = None

        valor_codigo = fila[columnas["codigo"]] if "codigo" in columnas else None
        valor_nombre = fila[columnas["producto"]] if "producto" in columnas else None
        if not pd.isna(valor_codigo) and str(valor_codigo).strip():
            producto = por_codigo.get(str(valor_codigo).strip().casefold())
            if producto is None:
                errores_fila.append(f"código de producto no registrado: {valor_codigo}")
        elif not pd.isna(valor_nombre) and str(valor_nombre).strip():
            coincidencias = por_nombre.get(str(valor_nombre).strip().casefold(), [])
            if len(coincidencias) == 1:
                producto = coincidencias[0]
            elif len(coincidencias) > 1:
                errores_fila.append(f"nombre ambiguo; usa su código: {valor_nombre}")
            else:
                errores_fila.append(f"producto no registrado: {valor_nombre}")
        else:
            errores_fila.append("falta el código o nombre del producto")

        valor_fecha = fila[columnas["fecha"]]
        fecha_parseada = None
        if pd.isna(valor_fecha):
            errores_fila.append("falta la fecha")
        else:
            try:
                if isinstance(valor_fecha, (int, float)) and not isinstance(valor_fecha, bool):
                    fecha_parseada = (
                        pd.Timestamp("1899-12-30")
                        + pd.to_timedelta(float(valor_fecha), unit="D")
                    ).date()
                else:
                    fecha_convertida = pd.to_datetime(
                        valor_fecha,
                        dayfirst=True,
                        format="mixed",
                        errors="coerce",
                    )
                    if not pd.isna(fecha_convertida):
                        fecha_parseada = fecha_convertida.date()
            except (TypeError, ValueError, OverflowError):
                fecha_parseada = None
            if fecha_parseada is None:
                errores_fila.append("fecha inválida")
            elif fecha_parseada > hoy:
                errores_fila.append("la fecha no puede ser futura")

        cantidad_numero = _numero_excel(fila[columnas["cantidad"]])
        if cantidad_numero is None or cantidad_numero <= 0 or not cantidad_numero.is_integer():
            errores_fila.append("la cantidad debe ser un entero mayor que cero")

        precio = _numero_excel(fila[columnas["precio"]])
        if precio is None or precio <= 0:
            errores_fila.append("el precio unitario debe ser mayor que cero")

        referencia = ""
        if "boleta" in columnas:
            valor_referencia = fila[columnas["boleta"]]
            if not pd.isna(valor_referencia):
                referencia = str(valor_referencia).strip()
                if referencia.endswith(".0") and referencia[:-2].isdigit():
                    referencia = referencia[:-2]

        if (
            errores_fila
            or fecha_parseada is None
            or producto is None
            or cantidad_numero is None
            or precio is None
        ):
            if not errores_fila:
                errores_fila.append("hay valores de venta que no se pudieron validar")
            errores.extend([f"Fila {numero_fila}: {error}" for error in errores_fila])
            continue

        filas_validas.append({
            "fila_excel": numero_fila,
            "fecha": fecha_parseada.isoformat() + " 12:00:00",
            "producto_id": producto[0],
            "codigo": producto[1],
            "producto": producto[2],
            "cantidad": int(cantidad_numero),
            "precio_unitario": round(precio, 2),
            "subtotal": round(precio * cantidad_numero, 2),
            "referencia": referencia,
        })

    if not filas_validas and not errores:
        errores.append("No se encontraron filas de ventas para importar.")
    return filas_validas, errores, original


def hash_importacion_registrada(hash_archivo):
    con = conectar()
    try:
        return con.execute(
            "SELECT nombre_archivo, fecha_importacion FROM importaciones_ventas "
            "WHERE hash_archivo = ?",
            (hash_archivo,),
        ).fetchone()
    finally:
        con.close()


def importar_ventas_excel(filas, hash_archivo, nombre_archivo, descontar_stock=False):
    """Importa todo el archivo en una transacción o no importa ninguna fila."""
    con = conectar()
    try:
        existente = con.execute(
            "SELECT 1 FROM importaciones_ventas WHERE hash_archivo = ?",
            (hash_archivo,),
        ).fetchone()
        if existente:
            return False, "Este mismo archivo ya fue importado."

        cantidades = {}
        for fila in filas:
            cantidades[fila["producto_id"]] = (
                cantidades.get(fila["producto_id"], 0) + fila["cantidad"]
            )

        descontar_stock_aplicado = bool(descontar_stock)
        aviso_stock = ""
        if descontar_stock_aplicado:
            ids_productos = list(cantidades)
            marcadores = ", ".join("?" for _ in ids_productos)
            stocks = con.execute(
                f"SELECT id, stock FROM productos WHERE id IN ({marcadores})",
                tuple(ids_productos),
            ).fetchall()
            stock_por_producto = {producto_id: stock for producto_id, stock in stocks}
            nombres_producto = {
                fila["producto_id"]: fila["producto"] for fila in filas
            }
            productos_sin_stock = [
                f"{nombres_producto[producto_id]} (se necesitan {cantidad}, "
                f"hay {stock_por_producto.get(producto_id, 0)})"
                for producto_id, cantidad in cantidades.items()
                if producto_id not in stock_por_producto
                or cantidad > stock_por_producto[producto_id]
            ]
            if productos_sin_stock:
                # El historial debe poder cargarse aunque el inventario actual ya
                # refleje esas ventas o no alcance para volver a descontarlas.
                # No descontamos ningún producto para evitar una actualización parcial.
                descontar_stock_aplicado = False
                lista_productos = "; ".join(productos_sin_stock[:3])
                if len(productos_sin_stock) > 3:
                    lista_productos += f" y {len(productos_sin_stock) - 3} más"
                aviso_stock = (
                    " No se descontó stock porque no alcanza para: "
                    f"{lista_productos}."
                )

        grupos = {}
        for fila in filas:
            clave = (
                (fila["fecha"], fila["referencia"])
                if fila["referencia"]
                else (fila["fecha"], f"__fila_{fila['fila_excel']}")
            )
            grupos.setdefault(clave, []).append(fila)

        grupos_lista = list(grupos.items())
        detalles_para_insertar = []
        for inicio in range(0, len(grupos_lista), 250):
            lote_grupos = grupos_lista[inicio:inicio + 250]
            valores_ventas = []
            for (fecha, referencia), detalles in lote_grupos:
                total = round(sum(detalle["subtotal"] for detalle in detalles), 2)
                valores_ventas.append(
                    (fecha, total, int(descontar_stock_aplicado), referencia or None)
                )

            marcadores = ", ".join("(?, ?, ?, ?)" for _ in valores_ventas)
            ventas_insertadas = con.execute(
                "INSERT INTO ventas (fecha, total, stock_descontado, referencia) "
                f"VALUES {marcadores} RETURNING id, fecha, referencia",
                tuple(valor for venta in valores_ventas for valor in venta),
            ).fetchall()
            ids_por_clave = {
                (str(fecha), referencia): venta_id
                for venta_id, fecha, referencia in ventas_insertadas
            }

            for (fecha, referencia), detalles in lote_grupos:
                venta_id = ids_por_clave[(fecha, referencia or None)]
                detalles_para_insertar.extend(
                    (
                        venta_id,
                        detalle["producto_id"],
                        detalle["cantidad"],
                        detalle["precio_unitario"],
                        detalle["subtotal"],
                    )
                    for detalle in detalles
                )

        for inicio in range(0, len(detalles_para_insertar), 150):
            lote_detalles = detalles_para_insertar[inicio:inicio + 150]
            marcadores = ", ".join("(?, ?, ?, ?, ?)" for _ in lote_detalles)
            con.execute(
                "INSERT INTO detalle_ventas "
                "(venta_id, producto_id, cantidad, precio_unitario, subtotal) "
                f"VALUES {marcadores}",
                tuple(valor for detalle in lote_detalles for valor in detalle),
            )

        if descontar_stock_aplicado:
            productos_lote = list(cantidades.items())
            for inicio in range(0, len(productos_lote), 250):
                lote_productos = productos_lote[inicio:inicio + 250]
                casos = " ".join("WHEN ? THEN ?" for _ in lote_productos)
                ids_sql = ", ".join("?" for _ in lote_productos)
                parametros = tuple(
                    valor
                    for producto_id, cantidad in lote_productos
                    for valor in (producto_id, cantidad)
                ) + tuple(producto_id for producto_id, _ in lote_productos)
                con.execute(
                    "UPDATE productos SET stock = stock - CASE id "
                    f"{casos} ELSE 0 END WHERE id IN ({ids_sql})",
                    parametros,
                )

        con.execute(
            "INSERT INTO importaciones_ventas "
            "(hash_archivo, nombre_archivo, fecha_importacion, filas_importadas) "
            "VALUES (?, ?, ?, ?)",
            (
                hash_archivo,
                nombre_archivo,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                len(filas),
            ),
        )
        con.commit()
        invalidar_cache_operativa()
        return True, (
            f"Se importaron {len(filas)} filas de venta correctamente.{aviso_stock}"
        )
    except Exception as e:
        con.rollback()
        return False, f"No se pudo importar el archivo: {e}"
    finally:
        con.close()

@st.cache_data(ttl=120, show_spinner=False, max_entries=1)
def obtener_ventas():
    con = conectar()
    try:
        return con.execute("""
            SELECT v.id, v.fecha, v.total, p.nombre, dv.cantidad,
                   dv.precio_unitario, dv.subtotal, v.stock_descontado,
                   v.referencia, dv.id
            FROM ventas v
            JOIN detalle_ventas dv ON v.id = dv.venta_id
            JOIN productos p ON dv.producto_id = p.id
            ORDER BY dv.id ASC
        """).fetchall()
    finally:
        con.close()

def eliminar_venta(venta_id, restaurar_stock_venta_antigua=False):
    """Elimina una venta y restaura el stock si esa venta lo había descontado."""
    con = conectar()

    try:
        venta = con.execute(
            "SELECT stock_descontado FROM ventas WHERE id = ?",
            (venta_id,),
        ).fetchone()

        if venta is None:
            return False, "No se encontró la venta seleccionada."

        detalles = con.execute(
            "SELECT producto_id, cantidad FROM detalle_ventas WHERE venta_id = ?",
            (venta_id,),
        ).fetchall()

        stock_descontado = venta[0]
        reponer_stock = (
            stock_descontado == 1
            or (stock_descontado is None and restaurar_stock_venta_antigua)
        )

        if reponer_stock:
            for producto_id, cantidad in detalles:
                con.execute(
                    "UPDATE productos SET stock = stock + ? WHERE id = ?",
                    (cantidad, producto_id),
                )

        con.execute("DELETE FROM detalle_ventas WHERE venta_id = ?", (venta_id,))
        con.execute("DELETE FROM ventas WHERE id = ?", (venta_id,))
        con.commit()
        invalidar_cache_operativa()

        if reponer_stock:
            return True, "Venta eliminada y stock restaurado."
        return True, "Venta eliminada. El stock actual no se modificó."

    except Exception as e:
        con.rollback()
        return False, f"No se pudo eliminar la venta: {e}"

    finally:
        con.close()


def eliminar_todas_ventas():
    """Elimina todas las ventas y sus detalles, reponiendo el stock descontado."""
    con = conectar()

    try:
        cantidad_ventas = con.execute(
            "SELECT COUNT(*) FROM ventas"
        ).fetchone()[0]
        if not cantidad_ventas:
            return False, "No hay ventas registradas para eliminar."

        stock_a_reponer = con.execute("""
            SELECT dv.producto_id, SUM(dv.cantidad)
            FROM detalle_ventas dv
            JOIN ventas v ON v.id = dv.venta_id
            WHERE v.stock_descontado = 1
            GROUP BY dv.producto_id
        """).fetchall()

        for producto_id, cantidad in stock_a_reponer:
            con.execute(
                "UPDATE productos SET stock = stock + ? WHERE id = ?",
                (cantidad, producto_id),
            )

        con.execute("DELETE FROM detalle_ventas")
        con.execute("DELETE FROM ventas")
        # Permite volver a importar los mismos archivos después de vaciar ventas.
        con.execute("DELETE FROM importaciones_ventas")
        if database.usar_supabase():
            con.execute(
                "SELECT setval(pg_get_serial_sequence('ventas', 'id'), 1, false)"
            )
            con.execute(
                "SELECT setval(pg_get_serial_sequence('detalle_ventas', 'id'), 1, false)"
            )
        else:
            con.execute(
                "DELETE FROM sqlite_sequence "
                "WHERE name IN ('ventas', 'detalle_ventas')"
            )
        con.commit()
        invalidar_cache_operativa()
        return True, (
            f"Se eliminaron {cantidad_ventas} ventas. El stock se restauró "
            "para las ventas que estaban marcadas como descontadas."
        )

    except Exception as e:
        con.rollback()
        return False, f"No se pudieron eliminar todas las ventas: {e}"

    finally:
        con.close()


def registrar_venta(
    producto_id,
    cantidad,
    fecha_venta=None,
    precio_unitario=None,
    descontar_stock=True,
):
    con = conectar()

    try:
        producto = con.execute("""
            SELECT nombre, precio_venta, stock
            FROM productos
            WHERE id = ?
        """, (producto_id,)).fetchone()

        if producto is None:
            return False, "Producto no encontrado."

        nombre, precio_venta, stock_actual = producto

        if precio_unitario is None:
            precio_unitario = precio_venta

        if cantidad <= 0:
            return False, "La cantidad debe ser mayor que 0."

        if precio_unitario <= 0:
            return False, "El precio unitario debe ser mayor que 0."

        if descontar_stock and cantidad > stock_actual:
            return False, f"Stock insuficiente. Stock disponible: {stock_actual}"

        subtotal = precio_unitario * cantidad
        if fecha_venta is None:
            fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        elif fecha_venta == datetime.now().date():
            fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        else:
            # Las boletas antiguas suelen tener solo fecha, sin hora. El mediodía
            # evita que la fecha cambie al convertirla en zonas horarias distintas.
            fecha = f"{fecha_venta.isoformat()} 12:00:00"

        cur = con.execute("""
            INSERT INTO ventas (fecha, total, stock_descontado)
            VALUES (?, ?, ?)
            RETURNING id
        """, (fecha, subtotal, int(bool(descontar_stock))))

        venta_id = cur.fetchone()[0]

        con.execute("""
            INSERT INTO detalle_ventas (
                venta_id,
                producto_id,
                cantidad,
                precio_unitario,
                subtotal
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            venta_id,
            producto_id,
            cantidad,
            precio_unitario,
            subtotal
        ))

        nuevo_stock = stock_actual
        if descontar_stock:
            nuevo_stock = stock_actual - cantidad
            con.execute("""
                UPDATE productos
                SET stock = ?
                WHERE id = ?
            """, (nuevo_stock, producto_id))

        con.commit()
        invalidar_cache_operativa()

        return True, (
            f"Venta registrada correctamente. "
            f"Producto: {nombre}. "
            f"Total: S/ {subtotal:.2f}. "
            + (f"Stock restante: {nuevo_stock}." if descontar_stock else
               " El stock actual no se modificó.")
        )

    except Exception as e:
        con.rollback()
        return False, f"Error al registrar venta: {e}"

    finally:
        con.close()


# ==========================================================
# COMPRAS
# ==========================================================

@st.cache_data(ttl=120, show_spinner=False, max_entries=1)
def obtener_compras():
    con = conectar()

    try:
        return con.execute("""
            SELECT
                c.id,
                c.fecha,
                c.total,
                c.referencia,
                p.nombre,
                dc.cantidad,
                dc.precio_unitario,
                dc.subtotal
            FROM compras c
            JOIN detalle_compras dc
                ON c.id = dc.compra_id
            JOIN productos p
                ON dc.producto_id = p.id
            ORDER BY c.id DESC
        """).fetchall()
    except Exception:
        # Permite consultar compras existentes si aún no se aplicó la migración
        # que añade el número de comprobante al esquema remoto.
        con.close()
        con = conectar()
        return con.execute("""
            SELECT
                c.id,
                c.fecha,
                c.total,
                NULL,
                p.nombre,
                dc.cantidad,
                dc.precio_unitario,
                dc.subtotal
            FROM compras c
            JOIN detalle_compras dc
                ON c.id = dc.compra_id
            JOIN productos p
                ON dc.producto_id = p.id
            ORDER BY c.id DESC
        """).fetchall()
    finally:
        con.close()


def registrar_compra(producto_id, cantidad, precio_compra):
    con = conectar()

    try:
        producto = con.execute("""
            SELECT nombre, stock
            FROM productos
            WHERE id = ?
        """, (producto_id,)).fetchone()

        if producto is None:
            return False, "Producto no encontrado."

        nombre, stock_actual = producto

        if cantidad <= 0:
            return False, "La cantidad debe ser mayor que 0."

        if precio_compra <= 0:
            return False, "El precio de compra debe ser mayor que 0."

        subtotal = precio_compra * cantidad
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cur = con.execute("""
            INSERT INTO compras (fecha, total)
            VALUES (?, ?)
            RETURNING id
        """, (fecha, subtotal))

        compra_id = cur.fetchone()[0]

        con.execute("""
            INSERT INTO detalle_compras (
                compra_id,
                producto_id,
                cantidad,
                precio_unitario,
                subtotal
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            compra_id,
            producto_id,
            cantidad,
            precio_compra,
            subtotal
        ))

        nuevo_stock = stock_actual + cantidad

        con.execute("""
            UPDATE productos
            SET stock = ?,
                precio_compra = ?
            WHERE id = ?
        """, (
            nuevo_stock,
            precio_compra,
            producto_id
        ))

        con.commit()
        invalidar_cache_operativa()

        return True, (
            f"Compra registrada correctamente. "
            f"Producto: {nombre}. "
            f"Total: S/ {subtotal:.2f}. "
            f"Stock actualizado: {nuevo_stock}."
        )

    except Exception as e:
        con.rollback()
        return False, f"Error al registrar compra: {e}"

    finally:
        con.close()


@st.cache_data(ttl=60, show_spinner=False, max_entries=3)
def generar_excel_historial_compras(tabla):
    salida = io.BytesIO()
    with pd.ExcelWriter(salida, engine="openpyxl") as escritor:
        pd.DataFrame(tabla).to_excel(
            escritor, index=False, sheet_name="Historial de compras"
        )
    return salida.getvalue()


def crear_plantilla_compras_excel():
    """Crea una plantilla vacía y una hoja separada con filas de demostración."""
    archivo = io.BytesIO()
    columnas = [
        "Fecha",
        "Código del producto",
        "Cantidad",
        "Precio de compra unitario (S/)",
        "Comprobante",
    ]

    with pd.ExcelWriter(archivo, engine="openpyxl") as escritor:
        pd.DataFrame(columns=columnas).to_excel(
            escritor,
            index=False,
            sheet_name="Compras",
        )
        hoja = escritor.sheets["Compras"]
        hoja.freeze_panes = "A2"
        hoja.auto_filter.ref = "A1:E1"
        for columna, ancho in {
            "A": 18, "B": 24, "C": 12, "D": 32, "E": 24
        }.items():
            hoja.column_dimensions[columna].width = ancho

        pd.DataFrame({
            "Fecha": ["2026-10-01", "2026-10-01", "2026-10-02", "2026-10-03"],
            "Código del producto": [
                "ESC-001", "DEMO-ESC-002", "DEMO-CUA-001", "DEMO-PAP-001"
            ],
            "Cantidad": [24, 24, 12, 30],
            "Precio de compra unitario (S/)": [0.50, 0.70, 2.50, 0.50],
            "Comprobante": [
                "COMP-DEMO-001", "COMP-DEMO-001", "COMP-DEMO-002", "COMP-DEMO-003"
            ],
        }).to_excel(escritor, index=False, sheet_name="Ejemplo DEMO - NO IMPORTAR")
        ejemplo = escritor.sheets["Ejemplo DEMO - NO IMPORTAR"]
        ejemplo.freeze_panes = "A2"
        ejemplo.auto_filter.ref = "A1:E5"
        for columna, ancho in {
            "A": 18, "B": 24, "C": 12, "D": 32, "E": 24
        }.items():
            ejemplo.column_dimensions[columna].width = ancho

        pd.DataFrame({
            "Instrucciones": [
                "La hoja Compras está vacía y es la que lee el sistema.",
                "La hoja Ejemplo DEMO - NO IMPORTAR contiene valores ficticios para reemplazar.",
                "Copia las filas necesarias del ejemplo a Compras y reemplaza todos los valores por los del comprobante real.",
                "Cada fila representa un producto comprado; una misma factura puede ocupar varias filas.",
                "Repite el mismo Comprobante y Fecha en las filas de productos de una misma compra.",
                "Usa la fecha del comprobante, el código registrado en el sistema, cantidad entera y costo unitario real.",
                "No subas filas de demostración: los códigos DEMO y precios son solo ilustrativos.",
            ]
        }).to_excel(escritor, index=False, sheet_name="Instrucciones")
        escritor.sheets["Instrucciones"].column_dimensions["A"].width = 110

    archivo.seek(0)
    return archivo.getvalue()


@st.cache_data(ttl=180, show_spinner=False, max_entries=6)
def validar_compras_excel(_contenido, hash_contenido):
    """Valida las compras del Excel antes de insertar o modificar el inventario."""
    try:
        original = pd.read_excel(io.BytesIO(_contenido), sheet_name="Compras")
    except ValueError:
        try:
            original = pd.read_excel(io.BytesIO(_contenido), sheet_name=0)
        except Exception as e:
            return [], [f"No se pudo leer la hoja Compras: {e}"], pd.DataFrame()
    except Exception as e:
        return [], [f"No se pudo leer el archivo Excel: {e}"], pd.DataFrame()

    if original.empty:
        return [], ["La hoja Compras no contiene filas para importar."], original

    encabezados = {
        "fecha": {"fecha", "fecha de compra", "fecha comprobante"},
        "codigo": {"codigo", "codigo producto", "codigo del producto", "sku"},
        "producto": {"producto", "nombre producto", "nombre del producto"},
        "cantidad": {"cantidad", "unidades", "cantidad comprada"},
        "precio": {
            "precio unitario", "precio de compra", "precio de compra unitario",
            "precio de compra unitario s", "precio unitario s", "costo unitario",
            "costo", "precio",
        },
        "referencia": {
            "comprobante", "numero comprobante", "n comprobante", "nro comprobante",
            "factura", "numero factura", "boleta", "referencia",
        },
    }
    columnas = {}
    for columna in original.columns:
        normalizado = _normalizar_encabezado_excel(columna)
        for campo, alias in encabezados.items():
            if normalizado in alias:
                columnas[campo] = columna

    faltantes = [campo for campo in ("fecha", "cantidad", "precio") if campo not in columnas]
    if "codigo" not in columnas and "producto" not in columnas:
        faltantes.append("Código del producto o Producto")
    if faltantes:
        return [], [
            "Faltan columnas requeridas: " + ", ".join(faltantes) + ". "
            "Descarga la plantilla para ver el formato aceptado."
        ], original

    productos = obtener_productos()
    por_codigo = {str(producto[1]).strip().casefold(): producto for producto in productos}
    por_nombre = {}
    for producto in productos:
        por_nombre.setdefault(str(producto[2]).strip().casefold(), []).append(producto)

    filas_validas = []
    errores = []
    hoy = datetime.now().date()

    for numero_fila, (_, fila) in enumerate(original.iterrows(), start=2):
        if all(pd.isna(valor) or str(valor).strip() == "" for valor in fila.tolist()):
            continue

        errores_fila = []
        producto = None
        valor_codigo = fila[columnas["codigo"]] if "codigo" in columnas else None
        valor_nombre = fila[columnas["producto"]] if "producto" in columnas else None
        if not pd.isna(valor_codigo) and str(valor_codigo).strip():
            producto = por_codigo.get(str(valor_codigo).strip().casefold())
            if producto is None:
                errores_fila.append(f"código de producto no registrado: {valor_codigo}")
        elif not pd.isna(valor_nombre) and str(valor_nombre).strip():
            coincidencias = por_nombre.get(str(valor_nombre).strip().casefold(), [])
            if len(coincidencias) == 1:
                producto = coincidencias[0]
            elif len(coincidencias) > 1:
                errores_fila.append(f"nombre ambiguo; usa su código: {valor_nombre}")
            else:
                errores_fila.append(f"producto no registrado: {valor_nombre}")
        else:
            errores_fila.append("falta el código o nombre del producto")

        valor_fecha = fila[columnas["fecha"]]
        fecha_parseada = None
        if pd.isna(valor_fecha):
            errores_fila.append("falta la fecha")
        else:
            try:
                if isinstance(valor_fecha, (int, float)) and not isinstance(valor_fecha, bool):
                    fecha_parseada = (
                        pd.Timestamp("1899-12-30")
                        + pd.to_timedelta(float(valor_fecha), unit="D")
                    ).date()
                else:
                    fecha_convertida = pd.to_datetime(
                        valor_fecha,
                        dayfirst=True,
                        format="mixed",
                        errors="coerce",
                    )
                    if not pd.isna(fecha_convertida):
                        fecha_parseada = fecha_convertida.date()
            except (TypeError, ValueError, OverflowError):
                fecha_parseada = None
            if fecha_parseada is None:
                errores_fila.append("fecha inválida")
            elif fecha_parseada > hoy:
                errores_fila.append("la fecha no puede ser futura")

        cantidad_numero = _numero_excel(fila[columnas["cantidad"]])
        if cantidad_numero is None or cantidad_numero <= 0 or not cantidad_numero.is_integer():
            errores_fila.append("la cantidad debe ser un entero mayor que cero")

        precio = _numero_excel(fila[columnas["precio"]])
        if precio is None or precio <= 0:
            errores_fila.append("el precio de compra unitario debe ser mayor que cero")

        referencia = ""
        if "referencia" in columnas:
            valor_referencia = fila[columnas["referencia"]]
            if not pd.isna(valor_referencia):
                referencia = str(valor_referencia).strip()
                if referencia.endswith(".0") and referencia[:-2].isdigit():
                    referencia = referencia[:-2]

        if (
            errores_fila
            or fecha_parseada is None
            or producto is None
            or cantidad_numero is None
            or precio is None
        ):
            if not errores_fila:
                errores_fila.append("hay valores de compra que no se pudieron validar")
            errores.extend([f"Fila {numero_fila}: {error}" for error in errores_fila])
            continue

        filas_validas.append({
            "fila_excel": numero_fila,
            "fecha": fecha_parseada.isoformat() + " 12:00:00",
            "producto_id": producto[0],
            "codigo": producto[1],
            "producto": producto[2],
            "cantidad": int(cantidad_numero),
            "precio_unitario": round(precio, 2),
            "subtotal": round(precio * cantidad_numero, 2),
            "referencia": referencia,
        })

    if not filas_validas and not errores:
        errores.append("No se encontraron filas de compras para importar.")
    return filas_validas, errores, original


def hash_importacion_compras_registrada(hash_archivo):
    con = conectar()
    try:
        return con.execute(
            "SELECT nombre_archivo, fecha_importacion FROM importaciones_compras "
            "WHERE hash_archivo = ?",
            (hash_archivo,),
        ).fetchone()
    except Exception as error:
        return {"error": str(error)}
    finally:
        con.close()


@st.cache_data(ttl=30, show_spinner=False, max_entries=1)
def obtener_auditoria_compras():
    """Resume consistencia interna de compras; no sustituye cotejar comprobantes."""
    con = conectar()
    try:
        resumen = con.execute("""
            SELECT
                COUNT(*) AS compras,
                COALESCE(SUM(c.total), 0) AS total_encabezados,
                COALESCE(SUM(COALESCE(d.suma_detalles, 0)), 0) AS total_detalles,
                COALESCE(SUM(COALESCE(d.lineas, 0)), 0) AS lineas,
                MIN(c.fecha) AS primera_fecha,
                MAX(c.fecha) AS ultima_fecha,
                SUM(CASE WHEN d.compra_id IS NULL THEN 1 ELSE 0 END) AS sin_detalles
            FROM compras c
            LEFT JOIN (
                SELECT compra_id, SUM(subtotal) AS suma_detalles, COUNT(*) AS lineas
                FROM detalle_compras
                GROUP BY compra_id
            ) d ON d.compra_id = c.id
        """).fetchone()
        diferencias = con.execute("""
            SELECT COUNT(*)
            FROM (
                SELECT c.id
                FROM compras c
                LEFT JOIN detalle_compras dc ON dc.compra_id = c.id
                GROUP BY c.id, c.total
                HAVING COUNT(dc.id) = 0
                    OR ABS(c.total - COALESCE(SUM(dc.subtotal), 0)) > 0.01
            ) inconsistentes
        """).fetchone()[0]
        return {
            "compras": resumen[0] or 0,
            "total_encabezados": float(resumen[1] or 0),
            "total_detalles": float(resumen[2] or 0),
            "lineas": resumen[3] or 0,
            "primera_fecha": resumen[4],
            "ultima_fecha": resumen[5],
            "sin_detalles": resumen[6] or 0,
            "diferencias": diferencias,
        }
    finally:
        con.close()


@st.cache_data(ttl=30, show_spinner=False, max_entries=1)
def obtener_historial_importaciones_compras():
    """Devuelve cargas; sin la columna nueva, el estado del stock queda desconocido."""
    con = conectar()
    try:
        try:
            return con.execute("""
                SELECT nombre_archivo, fecha_importacion, filas_importadas, stock_actualizado
                FROM importaciones_compras
                ORDER BY fecha_importacion DESC
            """).fetchall()
        except Exception as error:
            # La migración puede no haberse aplicado todavía en bases antiguas.
            # Recupera el historial y marca esos estados como desconocidos.
            if "stock_actualizado" not in str(error).lower():
                raise
            con.rollback()
            return con.execute("""
                SELECT nombre_archivo, fecha_importacion, filas_importadas,
                       NULL AS stock_actualizado
                FROM importaciones_compras
                ORDER BY fecha_importacion DESC
            """).fetchall()
    finally:
        con.close()


def importar_compras_excel(filas, hash_archivo, nombre_archivo, actualizar_stock=False):
    """Importa el archivo completo o no importa filas; opcionalmente suma al stock."""
    con = conectar()
    try:
        existente = con.execute(
            "SELECT 1 FROM importaciones_compras WHERE hash_archivo = ?",
            (hash_archivo,),
        ).fetchone()
        if existente:
            return False, "Este mismo archivo de compras ya fue importado."

        cantidades = {}
        precios_recientes = {}
        for fila in filas:
            producto_id = fila["producto_id"]
            cantidades[producto_id] = cantidades.get(producto_id, 0) + fila["cantidad"]
            precios_recientes[producto_id] = fila["precio_unitario"]

        grupos = {}
        for fila in filas:
            clave = (
                (fila["fecha"], fila["referencia"])
                if fila["referencia"]
                else (fila["fecha"], f"__fila_{fila['fila_excel']}")
            )
            grupos.setdefault(clave, []).append(fila)

        grupos_lista = list(grupos.items())
        ids_por_grupo = {}
        for inicio in range(0, len(grupos_lista), 250):
            lote = grupos_lista[inicio:inicio + 250]
            valores = [
                (
                    detalles_grupo[0]["fecha"],
                    round(sum(detalle["subtotal"] for detalle in detalles_grupo), 2),
                    referencia or None,
                )
                for (_, referencia), detalles_grupo in lote
            ]
            marcadores = ", ".join("(?, ?, ?)" for _ in valores)
            compras_insertadas = con.execute(
                "INSERT INTO compras (fecha, total, referencia) VALUES "
                f"{marcadores} RETURNING id, fecha, referencia",
                tuple(valor for compra in valores for valor in compra),
            ).fetchall()
            ids_por_clave = {
                (str(fecha), referencia): compra_id
                for compra_id, fecha, referencia in compras_insertadas
            }
            for clave, detalles_grupo in lote:
                fecha, referencia = clave
                compra_id = ids_por_clave[(str(fecha), referencia or None)]
                ids_por_grupo[clave] = compra_id

        detalles = [
            (
                ids_por_grupo[
                    (fila["fecha"], fila["referencia"])
                    if fila["referencia"]
                    else (fila["fecha"], f"__fila_{fila['fila_excel']}")
                ],
                fila["producto_id"],
                fila["cantidad"],
                fila["precio_unitario"],
                fila["subtotal"],
            )
            for fila in filas
        ]
        for inicio in range(0, len(detalles), 150):
            lote = detalles[inicio:inicio + 150]
            marcadores = ", ".join("(?, ?, ?, ?, ?)" for _ in lote)
            con.execute(
                "INSERT INTO detalle_compras "
                "(compra_id, producto_id, cantidad, precio_unitario, subtotal) "
                f"VALUES {marcadores}",
                tuple(valor for detalle in lote for valor in detalle),
            )

        if actualizar_stock:
            for producto_id, cantidad in cantidades.items():
                con.execute(
                    "UPDATE productos SET stock = stock + ?, precio_compra = ? "
                    "WHERE id = ?",
                    (cantidad, precios_recientes[producto_id], producto_id),
                )

        con.execute(
            "INSERT INTO importaciones_compras "
            "(hash_archivo, nombre_archivo, fecha_importacion, filas_importadas, stock_actualizado) "
            "VALUES (?, ?, ?, ?, ?)",
            (
                hash_archivo,
                nombre_archivo,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                len(filas),
                actualizar_stock,
            ),
        )
        con.commit()
        invalidar_cache_operativa()
        mensaje_stock = (
            " Se sumaron las unidades al stock y se actualizó el último costo."
            if actualizar_stock
            else " El stock actual y los costos de catálogo no se modificaron."
        )
        return True, (
            f"Se importaron {len(filas)} líneas en {len(grupos_lista)} compras."
            f"{mensaje_stock}"
        )
    except Exception as e:
        con.rollback()
        return False, f"No se pudo importar el archivo de compras: {e}"
    finally:
        con.close()


# ==========================================================
# DASHBOARD
# ==========================================================

@st.cache_data(ttl=120, show_spinner=False, max_entries=1)
def resumen_dashboard():
    con = conectar()
    try:
        return con.execute("""
            SELECT
                COALESCE((SELECT SUM(total) FROM ventas), 0),
                (SELECT COUNT(*) FROM ventas),
                (SELECT COUNT(*) FROM detalle_ventas),
                COALESCE((SELECT SUM(total) FROM compras), 0),
                (SELECT COUNT(*) FROM productos WHERE stock <= stock_minimo)
        """).fetchone()
    finally:
        con.close()


def resumen_operativo():
    ventas, cantidad_ventas, cantidad_lineas_venta, compras, stock_bajo = (
        resumen_dashboard()
    )
    return {
        "ventas": ventas,
        "cantidad_ventas": cantidad_ventas,
        "cantidad_lineas_venta": cantidad_lineas_venta,
        "compras": compras,
        "stock_bajo": stock_bajo,
    }


@st.cache_data(ttl=30, show_spinner=False, max_entries=10)
def obtener_alertas_stock(limit=5):
    con = conectar()
    try:
        return con.execute("""
            SELECT codigo, nombre, stock, stock_minimo
            FROM productos
            WHERE stock <= stock_minimo
            ORDER BY stock ASC, nombre ASC
            LIMIT ?
        """, (limit,)).fetchall()
    finally:
        con.close()

# ==========================================================
# MENÚ
# ==========================================================

with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">
            <div class="sidebar-brand-kicker">SISTEMA DE GESTIÓN</div>
            <div class="sidebar-brand-title">Librería Bazar Humbertito</div>
            <div class="sidebar-brand-subtitle">Gestión comercial inteligente</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    menu = st.session_state.setdefault("menu", "Inicio")
    grupos_menu = (
        ("Resumen", (
            ("inicio", "Inicio", "home"),
            ("dashboard", "Dashboard gerencial", "dashboard"),
        )),
        ("Operaciones", (
            ("productos", "Productos", "inventory_2"),
            ("ventas", "Ventas", "point_of_sale"),
            ("compras", "Compras", "shopping_cart"),
        )),
        ("Análisis", (
            ("analisis", "Análisis inteligente", "query_stats"),
            ("prediccion", "Predicción de demanda", "trending_up"),
        )),
    )
    if es_admin:
        grupos_menu += (("Administración", (
            ("usuarios", "Administrar usuarios", "manage_accounts"),
        )),)

    with st.container(key="sidebar_navigation"):
        for titulo, opciones in grupos_menu:
            with st.container(key=f"sidebar_group_{opciones[0][0]}"):
                st.html(f'<div class="sidebar-section-title">{titulo}</div>')
                for clave, opcion, icono in opciones:
                    st.button(
                        opcion,
                        key=f"menu_{clave}",
                        type="primary" if opcion == menu else "tertiary",
                        width="stretch",
                        icon=f":material/{icono}:",
                        on_click=seleccionar_modulo,
                        args=(opcion,),
                    )

        if es_admin:
            with st.expander("Administración de datos"):
                st.caption(
                    "El reinicio elimina productos, compras, ventas y sus historiales. "
                    "Esta acción no se puede deshacer."
                )

                confirmacion = st.text_input(
                    "Escriba REINICIAR para continuar",
                    key="confirmar_reinicio",
                    max_chars=9,
                )

                if st.button(
                    "Eliminar todo y empezar de cero",
                    key="reiniciar_datos",
                    type="secondary",
                    disabled=confirmacion.strip().upper() != "REINICIAR",
                ):
                    try:
                        database.reiniciar_datos()
                        invalidar_cache_operativa()
                        st.session_state.pop("confirmar_reinicio", None)
                        notificar_exito(
                            "Sistema reiniciado correctamente. Ya puedes comenzar un nuevo registro."
                        )
                        st.rerun()
                    except Exception as error:
                        st.error(f"No se pudo reiniciar el sistema: {error}")

    with st.container(key="sidebar_account", border=True):
        rol_texto = "Administrador" if es_admin else "Empleado"
        st.html(
            f"""
            <div class="sidebar-account-profile">
                <span class="user-status-dot" aria-hidden="true"></span>
                <div>
                    <div class="user-name">{escape(str(usuario_actual['nombre']))}</div>
                    <div class="user-role">{rol_texto}</div>
                </div>
            </div>
            """
        )
        if st.button(
            "Cerrar sesión", key="cerrar_sesion", icon=":material/logout:", width="stretch"
        ):
            st.session_state.pop("usuario", None)
            st.session_state.pop("menu", None)
            st.rerun()

if menu != "Inicio":
    import pandas as pd

# Carga bajo demanda los módulos pesados solo cuando la sección los necesita.
if menu in ("Dashboard gerencial", "Análisis inteligente"):
    import analysis
if menu in ("Dashboard gerencial", "Predicción de demanda"):
    import plotly.graph_objects as go
if menu == "Predicción de demanda":
    import prediction
    import pdf_report

# ==========================================================
# INICIO
# ==========================================================

if menu == "Inicio":

    st.markdown(
        f"""
        <section class="hb-hero">
            <div class="hb-hero-content">
                <div class="hb-hero-eyebrow">Gestión comercial · Librería Bazar Humbertito</div>
                <h1>Todo tu negocio, en un solo lugar</h1>
                <p>
                    Consulta el rendimiento de tu negocio, controla el inventario
                    y registra tus operaciones desde un solo panel.
                </p>
            </div>
            <div class="hb-hero-date">{datetime.now().strftime("%d/%m/%Y")}</div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    with st.spinner("Cargando el resumen del negocio..."):
        operacion = resumen_operativo()
        alertas = obtener_alertas_stock(3)

    st.caption(":material/database: Resumen operativo")

    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        st.metric("Ingresos totales", formatear_soles(operacion["ventas"]), border=True)
    with k2:
        st.metric(
            "Boletas / transacciones",
            formatear_numero_es(operacion["cantidad_ventas"]),
            border=True,
        )
    with k3:
        st.metric(
            "Líneas de productos vendidos",
            formatear_numero_es(operacion["cantidad_lineas_venta"]),
            border=True,
        )
    with k4:
        st.metric("Compras registradas", formatear_soles(operacion["compras"]), border=True)
    with k5:
        st.metric(
            "Productos con stock crítico",
            formatear_numero_es(operacion["stock_bajo"]),
            border=True,
        )

    st.caption(
        "Una transacción agrupa una venta o boleta; las líneas cuentan cada "
        "producto registrado dentro de esas ventas. "
        "Por eso pueden ser valores distintos."
    )
    st.caption(
        "El sistema no muestra margen neto: aún no guarda el costo histórico "
        "de cada producto vendido ni los gastos operativos."
    )

    st.subheader("Accesos rápidos", icon=":material/bolt:")
    a1, a2, a3, a4 = st.columns(4, border=True)

    with a1:
        st.markdown(
            """
            <div class="quick-card">
                <strong>Registrar producto</strong>
                <p>Agrega artículos nuevos para mantener la información comercial actualizada.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.button(
            "Ir a productos",
            key="quick_productos",
            width="stretch",
            icon=":material/inventory_2:",
            on_click=seleccionar_modulo,
            args=("Productos",),
        )

    with a2:
        st.markdown(
            """
            <div class="quick-card">
                <strong>Registrar venta</strong>
                <p>Controla las salidas del inventario y actualiza ventas en tiempo real.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.button(
            "Ir a ventas",
            key="quick_ventas",
            width="stretch",
            icon=":material/point_of_sale:",
            on_click=seleccionar_modulo,
            args=("Ventas",),
        )

    with a3:
        st.markdown(
            """
            <div class="quick-card">
                <strong>Registrar compra</strong>
                <p>Actualiza el stock y el costo de adquisición para cada producto.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.button(
            "Ir a compras",
            key="quick_compras",
            width="stretch",
            icon=":material/shopping_cart:",
            on_click=seleccionar_modulo,
            args=("Compras",),
        )

    with a4:
        st.markdown(
            """
            <div class="quick-card">
                <strong>Consultar indicadores</strong>
                <p>Revisa los ingresos y los productos más vendidos.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.button(
            "Ver dashboard",
            key="quick_dashboard",
            width="stretch",
            icon=":material/dashboard:",
            on_click=seleccionar_modulo,
            args=("Dashboard gerencial",),
        )

    with st.container(border=True):
        st.subheader("Estado del inventario", icon=":material/inventory_2:")

        if alertas:
            alert_column, action_column = st.columns([3, 1], vertical_alignment="center")
            with alert_column:
                st.warning(
                    f"{operacion['stock_bajo']} producto(s) requieren revisión."
                )
            with action_column:
                st.button(
                    "Revisar inventario",
                    key="quick_stock_review",
                    icon=":material/arrow_forward:",
                    type="primary",
                    width="stretch",
                    on_click=seleccionar_modulo,
                    args=("Productos",),
                )

            mostrar_tabla(
                [
                    {
                        "Código": codigo,
                        "Producto": nombre,
                        "Stock actual": stock,
                        "Stock mínimo": stock_minimo,
                    }
                    for codigo, nombre, stock, stock_minimo in alertas
                ],
                width="stretch",
                hide_index=True,
            )
        else:
            st.success("El inventario está saludable y no requiere reposición urgente.")
            st.caption(
                "Cuando un artículo alcance su nivel mínimo, aparecerá aquí para que puedas actuar a tiempo."
            )
# ==========================================================
# ADMINISTRACIÓN DE USUARIOS
# ==========================================================

elif menu == "Administrar usuarios":

    if not es_admin:
        st.error("No tienes permisos para administrar usuarios.")
        st.stop()

    st.header("Administración de usuarios", icon=":material/manage_accounts:")

    with st.container(key="admin_create_panel", border=True):
        st.subheader("Crear una cuenta")
    
        with st.form("crear_usuario"):
            nombre = st.text_input("Nombre completo")
            username = st.text_input("Nombre de usuario")
    
            password = st.text_input(
                "Contraseña",
                type="password"
            )
    
            confirmar = st.text_input(
                "Confirmar contraseña",
                type="password"
            )
    
            rol = st.selectbox(
                "Rol del usuario",
                ["empleado", "admin"],
                format_func=lambda x: (
                    "Empleado" if x == "empleado"
                    else "Administrador"
                )
            )
    
            guardar = st.form_submit_button(
                "Crear usuario",
                type="primary"
            )
    
            if guardar:
                if password != confirmar:
                    st.error("Las contraseñas no coinciden.")
                else:
                    try:
                        if rol not in ("admin", "empleado"):
                            st.error("Seleccione un rol válido.")
                            st.stop()
                        auth.crear_usuario(username, nombre, password, rol)
                        obtener_usuarios_administracion_cache.clear()
                        preparar_tabla_usuarios.clear()
                        notificar_exito(
                            f"Usuario {username} creado correctamente."
                        )
                        st.rerun()
                    except ValueError as error:
                        st.error(str(error))
    
    st.divider()
    st.subheader("Usuarios registrados")

    usuarios = obtener_usuarios_administracion_cache()

    if usuarios:
        # La tabla estática mantiene visibles los datos sin depender
        # del canvas del dataframe interactivo.
        tabla_usuarios = [
            {
                "ID": str(u[0]),
                "Usuario": u[1],
                "Nombre": u[2],
                "Rol": (
                    "Administrador"
                    if u[3] == "admin"
                    else "Empleado"
                ),
                "Estado": (
                    "Activo" if u[4] else "Inactivo"
                ),
                "Creado": u[5]
            }
            for u in usuarios
        ]

        with st.container(key="registered_users_table_shared"):
            mostrar_tabla(
                pd.DataFrame(tabla_usuarios),
                hide_index=True,
                width="stretch",
                height="content",
            )

        usuarios_eliminables = [
            usuario for usuario in usuarios
            if str(usuario[0]) != str(usuario_actual.get("id"))
        ]

        st.divider()
        transferencia_column, eliminacion_column = st.columns(2, gap="large")

        with transferencia_column:
            with st.container(key="user_transfer_panel"):
                st.subheader(
                    "Transferir administración",
                    icon=":material/swap_horiz:",
                )
                st.caption(
                    "Asigna el control a otra cuenta. Tu cuenta se eliminará "
                    "y se cerrará tu sesión; el historial se conservará."
                )

                if usuarios_eliminables:
                    usuarios_por_id = {
                        usuario[0]: usuario for usuario in usuarios_eliminables
                    }
                    nuevo_admin_id = st.selectbox(
                        "Nuevo administrador",
                        options=list(usuarios_por_id),
                        format_func=lambda user_id: (
                            f"{usuarios_por_id[user_id][2]} "
                            f"(@{usuarios_por_id[user_id][1]})"
                        ),
                        key="nuevo_administrador",
                    )
                    nuevo_admin = usuarios_por_id[nuevo_admin_id]
                    st.markdown(
                        f"**Se transferirá a:** {nuevo_admin[2]} "
                        f"· @{nuevo_admin[1]}"
                    )
                    st.caption(
                        "Recibirá permisos de administrador al confirmar."
                    )

                    confirmar_traspaso_checkbox = st.checkbox(
                        "Confirmo el traspaso y la eliminación de mi cuenta",
                        key="confirmar_traspaso_checkbox",
                    )
                    confirmar_traspaso = st.button(
                        "Transferir y salir",
                        key="ejecutar_traspaso_administracion",
                        icon=":material/swap_horiz:",
                        type="primary",
                        disabled=not confirmar_traspaso_checkbox,
                        width="stretch",
                    )

                    if confirmar_traspaso:
                        try:
                            auth.transferir_administracion_y_eliminar_usuario(
                                usuario_actual.get("id"),
                                nuevo_admin_id,
                            )
                            obtener_usuarios_administracion_cache.clear()
                            preparar_tabla_usuarios.clear()
                            notificar_exito(
                                f"Administración transferida a @{nuevo_admin[1]}. "
                                "Tu cuenta fue eliminada; inicia sesión con la nueva cuenta."
                            )
                            st.session_state.pop("usuario", None)
                            st.session_state.pop("menu", None)
                            st.session_state.pop(
                                "usuario_pendiente_eliminar_id",
                                None,
                            )
                            st.rerun()
                        except ValueError as error:
                            st.error(str(error))
                else:
                    st.info(
                        "Crea otra cuenta primero. Después podrás transferirle "
                        "la administración y eliminar tu cuenta actual."
                    )

        with eliminacion_column:
            with st.container(key="user_delete_panel"):
                st.subheader(
                    "Eliminar una cuenta",
                    icon=":material/person_remove:",
                )
                st.caption(
                    "La eliminación es permanente. Las ventas y compras "
                    "registradas se conservarán."
                )

                if usuarios_eliminables:
                    for usuario in usuarios_eliminables:
                        usuario_id, username, nombre, rol_usuario = usuario[:4]
                        with st.container(border=True):
                            datos_usuario, accion_usuario = st.columns([3, 1])
                            with datos_usuario:
                                st.write(f"**{nombre}** · @{username}")
                                st.caption(
                                    "Administrador"
                                    if rol_usuario == "admin"
                                    else "Empleado"
                                )
                            with accion_usuario:
                                if st.button(
                                    "Eliminar",
                                    key=f"preparar_eliminar_usuario_{usuario_id}",
                                    icon=":material/delete_outline:",
                                    type="secondary",
                                    width="stretch",
                                ):
                                    st.session_state[
                                        "usuario_pendiente_eliminar_id"
                                    ] = usuario_id
                                    st.rerun()

                    usuario_pendiente_id = st.session_state.get(
                        "usuario_pendiente_eliminar_id"
                    )
                    usuario_pendiente = next(
                        (
                            usuario for usuario in usuarios_eliminables
                            if str(usuario[0]) == str(usuario_pendiente_id)
                        ),
                        None,
                    )

                    if usuario_pendiente_id is not None and usuario_pendiente is None:
                        st.session_state.pop(
                            "usuario_pendiente_eliminar_id", None
                        )
                        st.info("La cuenta seleccionada ya no está disponible.")
                    elif usuario_pendiente is not None:
                        usuario_id, username, nombre = usuario_pendiente[:3]
                        st.warning(
                            f"Vas a eliminar la cuenta de {nombre} (@{username}). "
                            "Esta acción no se puede deshacer."
                        )

                        with st.form(f"confirmar_eliminar_usuario_{usuario_id}"):
                            confirmacion_eliminar = st.text_input(
                                f"Escribe {username} para confirmar",
                                key=f"confirmacion_eliminar_usuario_{usuario_id}",
                            )
                            confirmar_eliminar = st.form_submit_button(
                                "Confirmar eliminación",
                                type="secondary",
                                disabled=confirmacion_eliminar.strip() != username,
                            )

                        cancelar_eliminar = st.button(
                            "Cancelar",
                            key=f"cancelar_eliminar_usuario_{usuario_id}",
                        )

                        if cancelar_eliminar:
                            st.session_state.pop(
                                "usuario_pendiente_eliminar_id", None
                            )
                            st.rerun()

                        if confirmar_eliminar:
                            try:
                                auth.eliminar_usuario(
                                    usuario_id,
                                    usuario_actual.get("id"),
                                )
                                obtener_usuarios_administracion_cache.clear()
                                preparar_tabla_usuarios.clear()
                                st.session_state.pop(
                                    "usuario_pendiente_eliminar_id", None
                                )
                                notificar_exito(
                                    f"La cuenta @{username} se eliminó correctamente."
                                )
                                st.rerun()
                            except ValueError as error:
                                st.error(str(error))
                else:
                    st.info(
                        "No hay otras cuentas para eliminar. Crea otra cuenta "
                        "arriba para que aparezca aquí. La cuenta que estás "
                        "usando no se puede eliminar."
                    )
    else:
        st.info("Todavía no hay usuarios registrados.")


# ==========================================================
# DASHBOARD
# ==========================================================

elif menu == "Dashboard gerencial":

    st.header("Dashboard gerencial", icon=":material/dashboard:")

    ventas, cantidad_ventas, cantidad_lineas_venta, compras, stock_bajo = (
        resumen_dashboard()
    )

    d1, d2, d3, d4, d5 = st.columns(5)

    with d1:
        st.metric("Ingresos por ventas", formatear_soles(ventas))

    with d2:
        st.metric(
            "Boletas / transacciones",
            formatear_numero_es(cantidad_ventas),
        )

    with d3:
        st.metric(
            "Líneas de productos vendidos",
            formatear_numero_es(cantidad_lineas_venta),
        )

    with d4:
        st.metric("Compras acumuladas", formatear_soles(compras))

    with d5:
        st.metric("Productos con stock bajo", formatear_numero_es(stock_bajo))

    st.caption(
        "Las transacciones agrupan las ventas por boleta cuando el Excel la "
        "incluye. Las líneas cuentan cada producto de esas boletas; no equivalen "
        "a las unidades vendidas."
    )

    st.divider()

    inicio_analisis = perf_counter()
    datos_historicos = analysis.obtener_datos_ventas()
    resumen = analysis.resumen_ventas(datos_historicos)
    tendencia = analysis.tendencia_ventas(datos_historicos)
    alertas_ventas, dias_evaluados = analysis.alertas_importes_diarios(datos_historicos)
    tiempo_analisis = perf_counter() - inicio_analisis
    st.caption(
        f"{formatear_numero_es(len(datos_historicos))} registros agregados por "
        f"producto y día · Consulta y análisis inicial en "
        f"{formatear_numero_es(tiempo_analisis, 3)} s. El tiempo puede incluir datos en caché."
    )

    s1, s2, s3 = st.columns(3)

    with s1:
        st.metric(
            "Unidades vendidas",
            formatear_numero_es(resumen["unidades_vendidas"])
        )

    with s2:
        st.metric(
            "Días con ventas",
            formatear_numero_es(resumen["dias_con_ventas"])
        )

    with s3:
        st.metric(
            "Promedio diario",
            formatear_soles(resumen["promedio_diario"])
        )

    st.subheader("Evolución de las ventas")

    datos_dia = datos_historicos.copy()
    top = pd.DataFrame()
    selector_periodo, detalle_periodo = st.columns([1, 2], vertical_alignment="bottom")
    with selector_periodo:
        periodo_grafico = st.segmented_control(
            "Periodo del gráfico",
            ["30 días", "60 días", "90 días"],
            default="90 días",
            key="dashboard_periodo_ventas",
            width="stretch",
        )
        if periodo_grafico is None:
            periodo_grafico = "90 días"
    with detalle_periodo:
        st.caption(
            "El periodo seleccionado se aplica a los dos gráficos. Las tarjetas "
            "del resumen conservan los totales de todo el historial."
        )

    dias_por_periodo = {
        "30 días": 30,
        "60 días": 60,
        "90 días": 90,
    }
    if not datos_dia.empty and periodo_grafico in dias_por_periodo:
        fechas_ventas = pd.to_datetime(datos_dia["fecha"])
        fecha_limite = fechas_ventas.max() - pd.Timedelta(
            days=dias_por_periodo[periodo_grafico] - 1
        )
        datos_dia = datos_dia.loc[fechas_ventas >= fecha_limite].copy()
        top = (
            datos_dia.groupby(
                ["producto_id", "codigo", "nombre", "categoria"],
                as_index=False,
            )
            .agg(unidades_vendidas=("cantidad", "sum"))
            .sort_values(by="unidades_vendidas", ascending=False)
        )

    panel_ventas, panel_productos = st.columns([1.2, 1], gap="large")

    with panel_ventas:
        with st.container(key="dashboard_ventas_panel"):
            st.markdown("#### Ventas diarias")
            st.caption("Importe vendido por fecha · soles")

            if not datos_dia.empty:
                diario = (
                    datos_dia.groupby(
                        datos_dia["fecha"].dt.date
                    )["subtotal"]
                    .sum()
                    .rename("Ventas")
                )

                grafico_ventas_diarias = go.Figure(
                    go.Scatter(
                        x=pd.to_datetime(diario.index),
                        y=diario.values,
                        mode="lines+markers",
                        line={"width": 2.5},
                        marker={
                            "size": 5,
                        },
                        fill="tozeroy",
                        hovertemplate="%{x|%d/%m/%Y}<br>Ventas: S/ %{y:,.2f}<extra></extra>",
                    )
                )
                grafico_ventas_diarias.update_layout(
                    height=430,
                    margin={"l": 8, "r": 12, "t": 12, "b": 12},
                    showlegend=False,
                    hovermode="x unified",
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    xaxis={
                        "title": None,
                        "tickformat": "%d/%m",
                        "nticks": 8,
                        "fixedrange": True,
                        "showgrid": False,
                        "automargin": True,
                    },
                    yaxis={
                        "title": None,
                        "tickprefix": "S/ ",
                        "tickformat": ",.0f",
                        "fixedrange": True,
                        "rangemode": "tozero",
                        "zeroline": False,
                    },
                    separators=",.",
                    uirevision="dashboard-ventas",
                )
                with st.container(key="dashboard_ventas_chart"):
                    mostrar_grafico_fijo(
                        grafico_ventas_diarias,
                        "grafico_ventas_diarias",
                    )
            else:
                st.info("Aún no hay ventas para mostrar en este periodo.")

    with panel_productos:
        with st.container(key="dashboard_productos_panel"):
            st.markdown("#### Productos más vendidos")
            if not top.empty:
                top_12 = top.head(12).iloc[::-1]
                st.caption(f"Top {len(top_12)} · {periodo_grafico.lower()}")
                max_unidades = max(float(top_12["unidades_vendidas"].max()), 1)

                grafico_productos_mas_vendidos = go.Figure(
                    go.Bar(
                        x=top_12["unidades_vendidas"],
                        y=top_12["nombre"],
                        orientation="h",
                        marker={
                            "line": {"width": 0},
                        },
                        hovertemplate="%{y}<br>Unidades: %{x}<extra></extra>",
                    )
                )
                grafico_productos_mas_vendidos.update_layout(
                    height=430,
                    margin={"l": 8, "r": 34, "t": 12, "b": 12},
                    showlegend=False,
                    hovermode="closest",
                    bargap=0.32,
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    xaxis={
                        "title": None,
                        "range": [0, max_unidades * 1.18],
                        "fixedrange": True,
                        "showgrid": True,
                        "zeroline": False,
                    },
                    yaxis={
                        "title": None,
                        "fixedrange": True,
                        "automargin": True,
                        "ticklabelstandoff": 8,
                    },
                    separators=",.",
                    uirevision="dashboard-productos",
                )
                for _, producto in top_12.iterrows():
                    grafico_productos_mas_vendidos.add_annotation(
                        x=float(producto["unidades_vendidas"]),
                        y=producto["nombre"],
                        text=str(int(producto["unidades_vendidas"])),
                        xref="x",
                        yref="y",
                        xanchor="left",
                        yanchor="middle",
                        xshift=7,
                        showarrow=False,
                        font={"size": 12},
                    )
                with st.container(key="dashboard_productos_chart"):
                    mostrar_grafico_fijo(
                        grafico_productos_mas_vendidos,
                        "grafico_productos_mas_vendidos",
                    )
            else:
                st.info("Aún no hay productos vendidos para comparar.")


# ==========================================================
# PRODUCTOS
# ==========================================================

elif menu == "Productos":

    st.header("Gestión de productos", icon=":material/inventory_2:")

    tab1, tab2 = st.tabs(
        [
            "Registrar producto",
            "Productos registrados",
        ],
        on_change="rerun",
    )

    if tab1.open:
        with tab1:

            with st.form("form_producto"):

                c1, c2 = st.columns(2)

                with c1:
                    codigo = st.text_input("Código del producto")
                    nombre = st.text_input("Nombre del producto")
                    categoria = st.text_input("Categoría")
                    precio_compra = st.number_input(
                        "Precio de compra",
                        min_value=0.0,
                        step=0.10,
                        format="%.2f"
                    )

                with c2:
                    precio_venta = st.number_input(
                        "Precio de venta",
                        min_value=0.0,
                        step=0.10,
                        format="%.2f"
                    )
                    stock = st.number_input(
                        "Stock inicial",
                        min_value=0,
                        step=1
                    )
                    stock_minimo = st.number_input(
                        "Stock mínimo",
                        min_value=0,
                        step=1,
                        value=5
                    )
                    dias_entrega = st.number_input(
                        "Días de entrega del proveedor",
                        min_value=0,
                        max_value=30,
                        step=1,
                        value=0,
                        help="Usa 0 si todavía no conoces el plazo. Se usará como mínimo para calcular los días de cobertura.",
                    )

                guardar = st.form_submit_button(
                    "Registrar producto"
                )

                if guardar:

                    if not codigo.strip():
                        st.error("Ingrese el código.")

                    elif not nombre.strip():
                        st.error("Ingrese el nombre.")

                    elif precio_venta <= 0:
                        st.error("El precio de venta debe ser mayor que 0.")

                    else:

                        ok, mensaje = registrar_producto(
                            codigo.strip(),
                            nombre.strip(),
                            categoria.strip(),
                            precio_compra,
                            precio_venta,
                            stock,
                            stock_minimo,
                            dias_entrega,
                        )

                        if ok:
                            notificar_exito(mensaje)
                            st.rerun()
                        else:
                            st.error(mensaje)

    if tab2.open:
        with tab2:

            st.subheader("Cargar productos desde Excel")
            col_plantilla, col_archivo = st.columns([1, 2])
            with col_plantilla:
                st.download_button(
                    "Descargar plantilla de productos",
                    data=crear_plantilla_productos_excel(),
                    file_name="plantilla_productos_humbertito.xlsx",
                    mime=(
                        "application/vnd.openxmlformats-officedocument."
                        "spreadsheetml.sheet"
                    ),
                    key="descargar_plantilla_productos_excel",
                )
            with col_archivo:
                version_carga_productos = st.session_state.setdefault(
                    "version_carga_productos_excel", 0
                )
                archivo_productos_excel = st.file_uploader(
                    "Seleccionar archivo Excel de productos (.xlsx)",
                    type=["xlsx"],
                    key=f"carga_productos_excel_{version_carga_productos}",
                )

            if archivo_productos_excel is not None:
                contenido_productos_excel = archivo_productos_excel.getvalue()
                hash_productos_excel = hashlib.sha256(
                    contenido_productos_excel
                ).hexdigest()[:12]
                filas_productos_excel, errores_productos_excel = (
                    validar_productos_excel(contenido_productos_excel)
                )

                if filas_productos_excel:
                    vista_productos_excel = pd.DataFrame([
                        {
                            "ID": (
                                fila["id"] if fila["id"] is not None else "Automático"
                            ),
                            "Código": fila["codigo"],
                            "Producto": fila["nombre"],
                            "Categoría": fila["categoria"],
                            "Precio compra": f"S/ {fila['precio_compra']:.2f}",
                            "Precio venta": f"S/ {fila['precio_venta']:.2f}",
                            "Stock": fila["stock"],
                            "Stock mínimo": fila["stock_minimo"],
                            "Días de entrega": fila["dias_entrega"],
                        }
                        for fila in filas_productos_excel
                    ])
                    mostrar_tabla(
                        vista_productos_excel,
                        width="stretch",
                        hide_index=True,
                        height=420,
                        key=f"vista_productos_excel_{hash_productos_excel}",
                        column_config={
                            "ID": st.column_config.TextColumn(
                                "ID", width=85, alignment="center"
                            ),
                            "Código": st.column_config.TextColumn(
                                "Código", width=125, alignment="center"
                            ),
                            "Producto": st.column_config.TextColumn(
                                "Producto", width=220, alignment="center"
                            ),
                            "Categoría": st.column_config.TextColumn(
                                "Categoría", width=170, alignment="center"
                            ),
                            "Precio compra": st.column_config.TextColumn(
                                "Precio compra", width=130, alignment="center"
                            ),
                            "Precio venta": st.column_config.TextColumn(
                                "Precio venta", width=130, alignment="center"
                            ),
                            "Stock": st.column_config.NumberColumn(
                                "Stock", width=80, alignment="center"
                            ),
                            "Stock mínimo": st.column_config.NumberColumn(
                                "Stock mínimo", width=100, alignment="center"
                            ),
                            "Días de entrega": st.column_config.NumberColumn(
                                "Días de entrega", width=120, alignment="center"
                            ),
                        },
                    )
                    st.caption(
                        f"Productos válidos: {len(filas_productos_excel)}. "
                        "La importación se realizará completa, sin omitir filas."
                    )

                if errores_productos_excel:
                    st.error(
                        f"Se encontraron {len(errores_productos_excel)} errores. "
                        "Corrige el archivo; no se importará parcialmente."
                    )
                    for error_producto_excel in errores_productos_excel[:20]:
                        st.write(f"• {error_producto_excel}")
                    if len(errores_productos_excel) > 20:
                        st.caption("Se muestran los primeros 20 errores.")

                if filas_productos_excel and not errores_productos_excel:
                    if st.button(
                        "Importar productos validados",
                        key="confirmar_importacion_productos_excel",
                        type="primary",
                    ):
                        ok, mensaje = importar_productos_excel(
                            filas_productos_excel
                        )
                        if ok:
                            st.session_state[
                                "version_carga_productos_excel"
                            ] += 1
                            notificar_exito(mensaje)
                            st.rerun()
                        else:
                            st.error(mensaje)

            st.divider()

            productos = obtener_productos()

            if productos:

                tabla = []

                productos_por_id = {p[0]: p for p in productos}

                for p in productos:
                    tabla.append({
                        "ID": p[0],
                        "Código": p[1],
                        "Producto": p[2],
                        "Categoría": p[3],
                        "Precio compra": p[4],
                        "Precio venta": p[5],
                        "Stock": p[6],
                        "Stock mínimo": p[7],
                        "Días de entrega": p[8],
                    })

                st.subheader("Inventario registrado")
                st.caption(f"{formatear_numero_es(len(tabla))} productos")
                mostrar_tabla(
                    tabla,
                    hide_index=True,
                    height=420,
                    key="productos_registrados_orden_id_asc",
                    column_config={
                        "Precio compra": st.column_config.NumberColumn(
                            "Precio de compra", format="S/ %.2f"
                        ),
                        "Precio venta": st.column_config.NumberColumn(
                            "Precio de venta", format="S/ %.2f"
                        ),
                    },
                )

                st.download_button(
                    "Descargar productos en Excel",
                    data=generar_excel_productos(productos),
                    file_name=(
                        f"productos_humbertito_{datetime.now():%Y%m%d_%H%M}.xlsx"
                    ),
                    mime=(
                        "application/vnd.openxmlformats-officedocument."
                        "spreadsheetml.sheet"
                    ),
                    key="descargar_productos_excel",
                )

                st.divider()
                st.subheader("Editar o eliminar un producto")
                producto_id = st.selectbox(
                    "Selecciona el producto",
                    options=list(productos_por_id),
                    format_func=lambda identificador: (
                        f"{productos_por_id[identificador][1]} — "
                        f"{productos_por_id[identificador][2]}"
                    ),
                    key="producto_seleccionado_edicion",
                )
                producto = productos_por_id[producto_id]

                with st.expander("Editar datos del producto"):
                    with st.form(f"form_editar_producto_{producto_id}"):
                        edit_c1, edit_c2 = st.columns(2)

                        with edit_c1:
                            nuevo_codigo = st.text_input(
                                "Código del producto",
                                value=producto[1],
                            )
                            nuevo_nombre = st.text_input(
                                "Nombre del producto",
                                value=producto[2],
                            )
                            nueva_categoria = st.text_input(
                                "Categoría",
                                value=producto[3] or "",
                            )
                            nuevo_precio_compra = st.number_input(
                                "Precio de compra",
                                min_value=0.0,
                                step=0.10,
                                format="%.2f",
                                value=float(producto[4] or 0),
                            )

                        with edit_c2:
                            nuevo_precio_venta = st.number_input(
                                "Precio de venta",
                                min_value=0.0,
                                step=0.10,
                                format="%.2f",
                                value=float(producto[5] or 0),
                            )
                            nuevo_stock = st.number_input(
                                "Stock",
                                min_value=0,
                                step=1,
                                value=int(producto[6] or 0),
                            )
                            nuevo_stock_minimo = st.number_input(
                                "Stock mínimo",
                                min_value=0,
                                step=1,
                                value=int(producto[7] or 0),
                            )
                            nuevo_dias_entrega = st.number_input(
                                "Días de entrega del proveedor",
                                min_value=0,
                                max_value=30,
                                step=1,
                                value=int(producto[8] or 0),
                                help="Usa 0 si el plazo todavía no está definido.",
                            )

                        guardar_cambios = st.form_submit_button(
                            "Guardar cambios",
                            type="primary",
                        )

                        if guardar_cambios:
                            if nuevo_codigo is None or not nuevo_codigo.strip():
                                st.error("Ingrese el código del producto.")
                            elif nuevo_nombre is None or not nuevo_nombre.strip():
                                st.error("Ingrese el nombre del producto.")
                            elif nuevo_precio_venta <= 0:
                                st.error("El precio de venta debe ser mayor que 0.")
                            else:
                                ok, mensaje = actualizar_producto(
                                    producto_id,
                                    nuevo_codigo.strip(),
                                    nuevo_nombre.strip(),
                                    (nueva_categoria or "").strip(),
                                    nuevo_precio_compra,
                                    nuevo_precio_venta,
                                    nuevo_stock,
                                    nuevo_stock_minimo,
                                    nuevo_dias_entrega,
                                )

                                if ok:
                                    notificar_exito(mensaje)
                                    st.rerun()
                                else:
                                    st.error(mensaje)

                with st.expander("Eliminar producto"):
                    st.warning(
                        "La eliminación es permanente. Si el producto ya tiene "
                        "ventas o compras registradas, se conservará para no "
                        "alterar ese historial."
                    )

                    with st.form(f"form_eliminar_producto_{producto_id}"):
                        confirmar_eliminacion = st.checkbox(
                            f"Confirmo que deseo eliminar “{producto[2]}”."
                        )
                        eliminar = st.form_submit_button(
                            "Eliminar producto",
                            type="secondary",
                        )

                        if eliminar:
                            if not confirmar_eliminacion:
                                st.error("Marca la confirmación para continuar.")
                            else:
                                ok, mensaje = eliminar_producto(producto_id)

                                if ok:
                                    notificar_exito(mensaje)
                                    st.session_state.pop(
                                        "producto_seleccionado_edicion",
                                        None,
                                    )
                                    st.rerun()
                                else:
                                    st.error(mensaje)

                if es_admin:
                    with st.expander("Eliminar todos los productos"):
                        st.warning(
                            "Esto elimina el catálogo completo. Si existen ventas o "
                            "compras asociadas, el sistema conservará los productos para "
                            "proteger ese historial."
                        )
                        with st.form("form_eliminar_todos_productos"):
                            confirmar_eliminacion_total = st.checkbox(
                                "Confirmo que deseo eliminar todos los productos registrados."
                            )
                            eliminar_todos = st.form_submit_button(
                                "Eliminar todos los productos",
                                type="secondary",
                            )

                            if eliminar_todos:
                                if not confirmar_eliminacion_total:
                                    st.error(
                                        "Marca la confirmación para eliminar el catálogo."
                                    )
                                else:
                                    ok, mensaje = eliminar_todos_productos()
                                    if ok:
                                        notificar_exito(mensaje)
                                        st.session_state.pop(
                                            "producto_seleccionado_edicion",
                                            None,
                                        )
                                        st.rerun()
                                    else:
                                        st.error(mensaje)

            else:

                st.info("Todavía no hay productos registrados.")


# ==========================================================
# VENTAS
# ==========================================================

elif menu == "Ventas":

    st.header("Gestión de ventas", icon=":material/point_of_sale:")

    productos = obtener_productos()

    if not productos:

        st.warning("Primero registre un producto.")

    else:

        opciones = [
            f"{p[1]} - {p[2]} | Stock: {p[6]} | S/ {p[5]:.2f}"
            for p in productos
        ]

        with st.container(key="sales_form_panel", border=True):
            with st.form("form_venta"):
                st.markdown(
                    """
                    <div class="sales-form-intro">
                        <span>VENTA INDIVIDUAL</span>
                        <p>Ingresa los datos tal como aparecen en la boleta.</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                with st.container(key="sales_form_fields"):
                    producto_column, boleta_column = st.columns(
                        [1.1, 1],
                        gap="large",
                    )
                    with producto_column:
                        indice = st.selectbox(
                            "Seleccionar producto",
                            range(len(opciones)),
                            format_func=lambda i: opciones[i],
                            width="stretch",
                        )

                        cantidad = st.number_input(
                            "Cantidad",
                            min_value=1,
                            step=1,
                            value=1,
                            width="stretch",
                        )

                    with boleta_column:
                        precio_unitario = st.number_input(
                            "Precio unitario de la boleta (S/)",
                            min_value=0.01,
                            value=float(productos[indice][5]),
                            step=0.10,
                            width="stretch",
                        )
                        st.caption(
                            "Si la boleta antigua indica otro precio, ingresa ese valor."
                        )

                        fecha_venta = st.date_input(
                            "Fecha de la boleta",
                            value=datetime.now().date(),
                            max_value=datetime.now().date(),
                            width="stretch",
                        )
                        st.caption(
                            "Para una venta anterior, selecciona la fecha impresa."
                        )

                with st.container(key="stock_historico_panel", border=True):
                    descontar_stock_historico = st.checkbox(
                        "Descontar esta venta histórica del stock actual",
                        value=False,
                        key="stock_historico_checkbox",
                    )

                vender = st.form_submit_button(
                    "Registrar venta",
                    type="primary",
                    icon=":material/point_of_sale:",
                    width="content",
                )

                if vender:
                    ok, mensaje = registrar_venta(
                        productos[indice][0],
                        cantidad,
                        fecha_venta,
                        precio_unitario,
                        descontar_stock=(
                            fecha_venta == datetime.now().date()
                            or descontar_stock_historico
                        )
                    )

                    if ok:
                        notificar_exito(mensaje)
                        st.rerun()
                    else:
                        st.error(mensaje)

        st.divider()
        st.subheader("Importar ventas desde Excel")
        st.caption(
            "Carga las ventas de tus boletas en bloque. Puedes usar la plantilla "
            "o un archivo con columnas equivalentes."
        )
        st.download_button(
            "Descargar plantilla de ventas",
            data=crear_plantilla_ventas_excel(),
            file_name="plantilla_ventas_humbertito.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="descargar_plantilla_ventas",
        )

        archivo_ventas_excel = st.file_uploader(
            "Seleccionar archivo Excel de ventas (.xlsx)",
            type=["xlsx"],
            key="carga_masiva_ventas_excel",
        )
        st.caption(
            "Cada fila representa un producto vendido. Comparte el mismo N° "
            "Boleta entre filas para agruparlas en una venta."
        )

        if archivo_ventas_excel is not None:
            contenido_excel = archivo_ventas_excel.getvalue()
            hash_archivo_excel = hashlib.sha256(contenido_excel).hexdigest()
            importacion_existente = hash_importacion_registrada(hash_archivo_excel)
            filas_excel, errores_excel, _ = validar_ventas_excel(contenido_excel, hash_archivo_excel)

            if importacion_existente:
                st.warning(
                    "Este archivo ya fue importado el "
                    f"{importacion_existente[1]} como "
                    f"{importacion_existente[0]}. No se volverá a registrar."
                )

            if filas_excel:
                vista_previa = pd.DataFrame([
                    {
                        "Fila Excel": fila["fila_excel"],
                        "Fecha": fila["fecha"].split()[0],
                        "Código": fila["codigo"],
                        "Producto": fila["producto"],
                        "Cantidad": fila["cantidad"],
                        "Precio unitario": f"S/ {fila['precio_unitario']:.2f}",
                        "Boleta": fila["referencia"],
                    }
                    for fila in filas_excel
                ])
                mostrar_tabla(
                    vista_previa,
                    width="stretch",
                    hide_index=True,
                    height=520,
                    key=f"previsualizacion_ventas_{hash_archivo_excel[:12]}",
                    column_config={
                        "Fila Excel": st.column_config.NumberColumn(
                            "Fila Excel", width=85, alignment="center"
                        ),
                        "Fecha": st.column_config.TextColumn(
                            "Fecha", width=125, alignment="center"
                        ),
                        "Código": st.column_config.TextColumn(
                            "Código", width=135, alignment="center"
                        ),
                        "Producto": st.column_config.TextColumn(
                            "Producto", width=250, alignment="center"
                        ),
                        "Cantidad": st.column_config.NumberColumn(
                            "Cantidad", width=85, alignment="center"
                        ),
                        "Precio unitario": st.column_config.TextColumn(
                            "Precio unitario", width=125, alignment="center"
                        ),
                        "Boleta": st.column_config.TextColumn(
                            "Boleta", width=230, alignment="center"
                        ),
                    },
                )
                st.caption(
                    f"Filas válidas: {len(filas_excel)} · "
                    f"Importe total: S/ {sum(fila['subtotal'] for fila in filas_excel):.2f}"
                )
                st.caption(
                    "La vista previa incluye todas las filas válidas. "
                    "Desplázate hacia abajo dentro del recuadro para revisarlas."
                )

            if errores_excel:
                st.error(
                    f"Se encontraron {len(errores_excel)} errores. Corrige el Excel "
                    "para importar el archivo completo."
                )
                for error_excel in errores_excel[:20]:
                    st.write(f"• {error_excel}")
                if len(errores_excel) > 20:
                    st.caption("Se muestran solo los primeros 20 errores.")

            descontar_stock_importacion = st.checkbox(
                "Descontar estas unidades del stock actual al importar",
                value=False,
                key="importar_ventas_descontar_stock",
            )
            st.caption(
                "Márcala solo si estas ventas todavía deben restarse del inventario. "
                "Si el stock no alcanza, las ventas se registran sin modificarlo."
            )

            if not errores_excel and filas_excel and not importacion_existente:
                if st.button(
                    "Importar ventas validadas",
                    key="confirmar_importacion_ventas_excel",
                    type="primary",
                ):
                    ok, mensaje = importar_ventas_excel(
                        filas_excel,
                        hash_archivo_excel,
                        archivo_ventas_excel.name,
                        descontar_stock_importacion,
                    )
                    if ok:
                        notificar_exito(mensaje)
                        st.rerun()
                    else:
                        st.error(mensaje)

        st.subheader("Historial de ventas", icon=":material/history:")

        ventas = obtener_ventas()

        if ventas:
            total_por_venta = {
                venta[0]: float(venta[2] or 0)
                for venta in ventas
            }
            unidades_vendidas = sum(int(venta[4] or 0) for venta in ventas)
            resumen_ventas = st.columns(3)
            resumen_ventas[0].metric(
                "Ventas registradas",
                formatear_numero_es(len(total_por_venta)),
            )
            resumen_ventas[1].metric(
                "Unidades vendidas",
                formatear_numero_es(unidades_vendidas),
            )
            resumen_ventas[2].metric(
                "Total vendido",
                formatear_soles(sum(total_por_venta.values())),
            )

            tabla = []
            for numero_fila, venta in enumerate(ventas, start=1):
                tabla.append({
                    "N.º": numero_fila,
                    "Boleta": venta[8] or "",
                    "Fecha": venta[1],
                    "Total de boleta": f"S/ {venta[2]:.2f}",
                    "Producto": venta[3],
                    "Cantidad": venta[4],
                    "Precio unitario": f"S/ {venta[5]:.2f}",
                    "Subtotal de línea": f"S/ {venta[6]:.2f}",
                })

            st.caption(
                "Cada fila corresponde a un producto. El total de boleta se repite "
                "cuando una venta incluye varios productos."
            )

            filas_por_pagina = 50
            total_paginas = (len(tabla) + filas_por_pagina - 1) // filas_por_pagina
            if total_paginas > 1:
                opciones_pagina = list(range(1, total_paginas + 1))
                if st.session_state.get("historial_ventas_pagina", 1) not in opciones_pagina:
                    st.session_state["historial_ventas_pagina"] = 1
                pagina = st.selectbox(
                    "Página del historial",
                    options=opciones_pagina,
                    format_func=lambda numero: f"Página {numero} de {total_paginas}",
                    key="historial_ventas_pagina",
                    width=220,
                )
            else:
                pagina = 1

            inicio = (pagina - 1) * filas_por_pagina
            fin = min(inicio + filas_por_pagina, len(tabla))
            st.caption(
                f"Mostrando filas {formatear_numero_es(inicio + 1)}–"
                f"{formatear_numero_es(fin)} de {formatear_numero_es(len(tabla))}."
            )
            tabla_pagina = pd.DataFrame(tabla[inicio:fin])
            with st.container(key="sales_history_table"):
                st.table(
                    tabla_pagina,
                    width="stretch",
                    height="content" if len(tabla_pagina) <= 10 else 520,
                    hide_index=True,
                )

            with st.expander("Eliminar una venta registrada por error"):
                ventas_por_id = {venta[0]: venta for venta in ventas}
                venta_id_seleccionada = st.selectbox(
                    "Selecciona la venta",
                    options=list(ventas_por_id),
                    format_func=lambda venta_id: (
                        f"Venta {venta_id} · {ventas_por_id[venta_id][1]} · "
                        f"{ventas_por_id[venta_id][3]} · "
                        f"{ventas_por_id[venta_id][4]} u. · "
                        f"S/ {ventas_por_id[venta_id][2]:.2f}"
                        + (
                            f" · Boleta {ventas_por_id[venta_id][8]}"
                            if ventas_por_id[venta_id][8]
                            else ""
                        )
                    ),
                    key="venta_a_eliminar",
                )
                venta_seleccionada = ventas_por_id[venta_id_seleccionada]

                restaurar_stock_venta_antigua = False
                if venta_seleccionada[7] is None:
                    st.info(
                        "Esta venta es anterior al control de stock por venta. "
                        "No se puede saber si descontó inventario."
                    )
                    restaurar_stock_venta_antigua = st.checkbox(
                        "Restaurar al stock las unidades de esta venta",
                        value=False,
                        key=f"restaurar_stock_venta_antigua_{venta_id_seleccionada}",
                    )
                    st.caption(
                        "Márcala solo si el stock actual ya incluye el descuento "
                        "de esta venta."
                    )
                elif venta_seleccionada[7] == 1:
                    st.caption("Al eliminarla, se devolverán sus unidades al stock.")
                else:
                    st.caption("Esta venta no modificó el stock al registrarse.")

                confirmar_eliminacion = st.checkbox(
                    f"Confirmo que deseo eliminar la venta {venta_id_seleccionada}",
                    value=False,
                    key=f"confirmar_eliminar_venta_{venta_id_seleccionada}",
                )

                if st.button(
                    "Eliminar venta seleccionada",
                    key=f"eliminar_venta_{venta_id_seleccionada}",
                    type="secondary",
                ):
                    if not confirmar_eliminacion:
                        st.warning("Marca la confirmación antes de eliminar la venta.")
                    else:
                        ok, mensaje = eliminar_venta(
                            venta_id_seleccionada,
                            restaurar_stock_venta_antigua,
                        )
                        if ok:
                            notificar_exito(mensaje)
                            st.rerun()
                        else:
                            st.error(mensaje)

            if es_admin:
                cantidad_ventas_total = len({venta[0] for venta in ventas})
                estados_stock_ventas = {venta[0]: venta[7] for venta in ventas}
                ventas_stock_desconocido = sum(
                    estado is None for estado in estados_stock_ventas.values()
                )

                with st.expander("Eliminar todas las ventas"):
                    with st.container(key="delete_all_sales_warning", border=True):
                        st.markdown(
                            ":material/delete_forever: **Eliminación permanente**",
                            text_alignment="center",
                        )
                        st.markdown(
                            f"Se eliminarán **{formatear_numero_es(cantidad_ventas_total)} "
                            "ventas** y sus detalles. El stock se restaurará solo para "
                            "las ventas que el sistema marcó como descontadas.",
                            text_alignment="center",
                        )
                    if ventas_stock_desconocido:
                        st.info(
                            f"{ventas_stock_desconocido} ventas antiguas no tienen "
                            "registro de si descontaron stock; su eliminación no cambiará "
                            "el inventario."
                        )
                    st.caption(
                        "También se borrará el registro de archivos importados para "
                        "que puedas importarlos nuevamente."
                    )
                    confirmar_eliminar_todas = st.checkbox(
                        f"Confirmo que deseo eliminar todas las "
                        f"{cantidad_ventas_total} ventas",
                        key=f"confirmar_eliminar_todas_ventas_{cantidad_ventas_total}",
                    )
                    if st.button(
                        "Eliminar todas las ventas",
                        key="eliminar_todas_ventas",
                        type="secondary",
                    ):
                        if not confirmar_eliminar_todas:
                            st.warning(
                                "Marca la confirmación antes de eliminar todas las ventas."
                            )
                        else:
                            ok, mensaje = eliminar_todas_ventas()
                            if ok:
                                notificar_exito(mensaje)
                                st.rerun()
                            else:
                                st.error(mensaje)

        else:

            st.info("Todavía no hay ventas registradas.")


# ==========================================================
# COMPRAS
# ==========================================================

elif menu == "Compras":

    st.header("Gestión de compras", icon=":material/shopping_cart:")

    productos = obtener_productos()

    if not productos:

        st.warning("Primero registre un producto.")

    else:

        opciones = [
            f"{p[1]} - {p[2]} | Stock actual: {p[6]}"
            for p in productos
        ]

        with st.container(key="purchase_form_panel", border=True):
            with st.form("form_compra"):
    
                indice = st.selectbox(
                    "Seleccionar producto",
                    range(len(opciones)),
                    format_func=lambda i: opciones[i]
                )
    
                cantidad = st.number_input(
                    "Cantidad comprada",
                    min_value=1,
                    step=1,
                    value=1
                )
    
                precio_compra = st.number_input(
                    "Precio de compra por unidad",
                    min_value=0.01,
                    step=0.10,
                    format="%.2f"
                )
    
                comprar = st.form_submit_button(
                    "Registrar compra"
                )
    
                if comprar:
    
                    ok, mensaje = registrar_compra(
                        productos[indice][0],
                        cantidad,
                        precio_compra
                    )
    
                    if ok:
                        notificar_exito(mensaje)
                        st.rerun()
                    else:
                        st.error(mensaje)
    
        st.divider()
        st.subheader("Importar compras desde Excel")
        st.caption(
            "La plantilla trae una hoja vacía para tus datos y otra con filas "
            "ficticias marcadas como DEMO. Reemplaza el ejemplo por los datos "
            "de tus comprobantes reales antes de importarlo."
        )
        st.download_button(
            "Descargar plantilla de compras",
            data=crear_plantilla_compras_excel(),
            file_name="plantilla_compras_humbertito.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="descargar_plantilla_compras",
        )

        archivo_compras_excel = st.file_uploader(
            "Seleccionar archivo Excel de compras (.xlsx)",
            type=["xlsx"],
            key="carga_masiva_compras_excel",
        )
        st.caption(
            "Cada fila representa una línea de compra con fecha, producto, "
            "cantidad y costo unitario."
        )

        if archivo_compras_excel is not None:
            contenido_compras = archivo_compras_excel.getvalue()
            hash_archivo_compras = hashlib.sha256(contenido_compras).hexdigest()
            importacion_existente = hash_importacion_compras_registrada(
                hash_archivo_compras
            )

            if isinstance(importacion_existente, dict) and "error" in importacion_existente:
                st.error(
                    "La importación de compras todavía no está habilitada en la "
                    "base de datos. Ejecuta una vez "
                    "migracion_importar_compras.sql en Supabase SQL Editor."
                )
            elif isinstance(importacion_existente, (tuple, list)) and len(importacion_existente) > 1:
                st.warning(
                    "Este mismo archivo ya se importó el "
                    f"{importacion_existente[1]}. No se volverá a cargar para "
                    "evitar duplicar compras y stock."
                )
            elif importacion_existente:
                st.error("No se pudo interpretar el registro de importación existente.")
            else:
                filas_compras, errores_compras, _ = validar_compras_excel(
                    contenido_compras,
                    hash_archivo_compras,
                )
                if errores_compras:
                    st.error(
                        f"Se encontraron {len(errores_compras)} errores. "
                        "Corrige el Excel para importar el archivo completo."
                    )
                    for error_excel in errores_compras[:20]:
                        st.write(f"• {error_excel}")
                    if len(errores_compras) > 20:
                        st.caption("Se muestran solo los primeros 20 errores.")

                if filas_compras:
                    tabla_compras_excel = [
                        {
                            "Fila Excel": fila["fila_excel"],
                            "Fecha": fila["fecha"][:10],
                            "Código": fila["codigo"],
                            "Producto": fila["producto"],
                            "Comprobante": fila["referencia"],
                            "Cantidad": fila["cantidad"],
                            "Precio compra unitario": f"S/ {fila['precio_unitario']:.2f}",
                            "Subtotal": f"S/ {fila['subtotal']:.2f}",
                        }
                        for fila in filas_compras
                    ]
                    mostrar_tabla(
                        tabla_compras_excel,
                        width="stretch",
                        hide_index=True,
                        height=min(420, 40 + 35 * min(len(filas_compras), 10)),
                    )
                    total_compras_excel = sum(
                        fila["subtotal"] for fila in filas_compras
                    )
                    st.caption(
                        f"Filas válidas: {len(filas_compras)} · "
                        f"Total de compras: {formatear_soles(total_compras_excel)}"
                    )

                    actualizar_stock_compras = st.checkbox(
                        "Sumar estas unidades al stock actual",
                        value=False,
                        key="importar_compras_actualizar_stock",
                    )
                    st.caption(
                        "Déjala desmarcada si el stock actual ya refleja esas compras. "
                        "Márcala solo si esas unidades aún no están incluidas."
                    )
                    if not actualizar_stock_compras:
                        st.caption(
                            "El archivo se guardará como historial sin cambiar el "
                            "stock ni el costo actual del catálogo."
                        )

                    if not errores_compras and st.button(
                        "Importar compras validadas",
                        key="confirmar_importacion_compras_excel",
                        type="primary",
                    ):
                        ok, mensaje = importar_compras_excel(
                            filas_compras,
                            hash_archivo_compras,
                            archivo_compras_excel.name,
                            actualizar_stock_compras,
                        )
                        if ok:
                            notificar_exito(mensaje)
                            st.rerun()
                        else:
                            st.error(mensaje)

        st.subheader("Historial de compras")

        try:
            auditoria = obtener_auditoria_compras()
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Comprobantes", formatear_numero_es(auditoria["compras"]))
            m2.metric("Total registrado", formatear_soles(auditoria["total_encabezados"]))
            m3.metric("Líneas de compra", formatear_numero_es(auditoria["lineas"]))
            m4.metric("Total en detalle", formatear_soles(auditoria["total_detalles"]))
            st.caption(
                "Fechas registradas: "
                f"{auditoria['primera_fecha'] or '—'} a {auditoria['ultima_fecha'] or '—'}. "
                "La conciliación verifica que los encabezados coincidan con sus líneas; "
                "no confirma por sí sola que importes y fechas coincidan con los comprobantes."
            )
            if auditoria["diferencias"]:
                st.error(
                    f"Hay {auditoria['diferencias']} comprobantes cuyo total no coincide "
                    "con sus líneas o que no tienen detalle. Revisa el historial antes "
                    "de usarlo en el informe."
                )
            elif auditoria["compras"]:
                st.success("Los totales registrados coinciden con las líneas de compra.")
            if auditoria["sin_detalles"]:
                st.error(
                    f"Hay {auditoria['sin_detalles']} compras sin líneas de detalle."
                )
        except Exception as error:
            st.warning(
                f"No se pudo mostrar la auditoría de compras. Detalle: {error}"
            )

        compras = obtener_compras()

        if compras:

            tabla = []

            for compra in compras:
                tabla.append({
                    "Compra": compra[0],
                    "Fecha": compra[1],
                    "Total": formatear_soles(compra[2]),
                    "Comprobante": compra[3] or "",
                    "Producto": compra[4],
                    "Cantidad": compra[5],
                    "Precio unitario": formatear_soles(compra[6]),
                    "Subtotal": formatear_soles(compra[7])
                })

            mostrar_tabla(
                tabla,
                width="stretch",
                hide_index=True,
                height=420,
            )

            st.download_button(
                "Descargar historial de compras en Excel",
                data=generar_excel_historial_compras(tabla),
                file_name="historial_compras_humbertito.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="descargar_historial_compras",
            )

        else:

            st.info("Todavía no hay compras registradas.")

        try:
            historial_importaciones = obtener_historial_importaciones_compras()
            if historial_importaciones:
                with st.expander("Auditoría de archivos importados"):
                    filas_importaciones = []
                    for nombre, fecha, filas, stock_actualizado in historial_importaciones:
                        if stock_actualizado is None:
                            estado_stock = "No registrado en esa versión"
                        else:
                            estado_stock = "Sí" if stock_actualizado else "No"
                        filas_importaciones.append({
                            "Archivo": nombre,
                            "Fecha de importación": fecha,
                            "Filas": filas,
                            "Sumó al stock": estado_stock,
                        })
                    mostrar_tabla(
                        filas_importaciones,
                        width="stretch",
                        hide_index=True,
                    )
        except Exception:
            st.caption("No se pudo cargar el historial de archivos importados.")


# ==========================================================
# ANÁLISIS INTELIGENTE
# ==========================================================

elif menu == "Análisis inteligente":

    st.header("Análisis inteligente", icon=":material/query_stats:")

    inicio_analisis = perf_counter()
    datos_historicos = analysis.obtener_datos_ventas()
    resumen = analysis.resumen_ventas(datos_historicos)
    tendencia = analysis.tendencia_ventas(datos_historicos)
    alertas_ventas, dias_evaluados = analysis.alertas_importes_diarios(datos_historicos)
    tiempo_analisis = perf_counter() - inicio_analisis
    st.caption(
        f"{formatear_numero_es(len(datos_historicos))} registros agregados por "
        f"producto y día · Consulta y análisis inicial en "
        f"{formatear_numero_es(tiempo_analisis, 3)} s. El tiempo puede incluir datos en caché."
    )

    st.subheader("Resumen comercial")

    a1, a2, a3, a4 = st.columns(4, border=True)

    with a1:
        st.metric(
            "Ventas",
            formatear_soles(resumen["total_ventas"])
        )

    with a2:
        st.metric(
            "Unidades vendidas",
            formatear_numero_es(resumen["unidades_vendidas"])
        )

    with a3:
        st.metric(
            "Días con ventas",
            formatear_numero_es(resumen["dias_con_ventas"])
        )

    with a4:
        st.metric(
            "Promedio diario",
            formatear_soles(resumen["promedio_diario"])
        )

    st.caption(
        "Las unidades suman las cantidades vendidas; pueden ser más que las "
        "líneas de productos registradas. El promedio diario se calcula sobre "
        "los días que sí tuvieron ventas."
    )

    st.divider()

    st.subheader("Tendencia de ventas")

    st.caption(
        "Comparación de los últimos 90 días: primeros 45 frente a los "
        "últimos 45. Los días sin ventas se cuentan como S/ 0."
    )

    tipo_tendencia = tendencia.get("tipo", "Sin datos")
    explicacion_tendencia = tendencia.get(
        "explicacion",
        "La explicación detallada no está disponible para este resultado.",
    )
    st.info(f"Tendencia {tipo_tendencia}: {explicacion_tendencia}")

    fecha_inicio = tendencia.get("fecha_inicio")
    fecha_fin = tendencia.get("fecha_fin")
    dias_por_periodo = tendencia.get("dias_por_periodo")
    if (
        fecha_inicio is not None
        and fecha_fin is not None
        and dias_por_periodo is not None
        and "ventas_periodo_base" in tendencia
        and "ventas_periodo_reciente" in tendencia
        and "valor" in tendencia
    ):
        inicio_base = fecha_inicio.strftime("%d/%m/%Y")
        fin_base = (
            fecha_inicio
            + pd.Timedelta(days=dias_por_periodo - 1)
        ).strftime("%d/%m/%Y")
        inicio_reciente = (
            fecha_inicio
            + pd.Timedelta(days=dias_por_periodo)
        ).strftime("%d/%m/%Y")
        fin_reciente = fecha_fin.strftime("%d/%m/%Y")

        periodo_base, periodo_reciente, variacion_col = st.columns(3)
        with periodo_base:
            st.metric(
                f"Periodo base · {inicio_base}–{fin_base}",
                formatear_soles(tendencia.get("ventas_periodo_base"))
            )
        with periodo_reciente:
            st.metric(
                f"Periodo reciente · {inicio_reciente}–{fin_reciente}",
                formatear_soles(tendencia.get("ventas_periodo_reciente"))
            )
        with variacion_col:
            valor_variacion = tendencia.get("valor")
            st.metric(
                "Variación entre periodos",
                f"{valor_variacion:+.1f}%" if valor_variacion is not None else "—"
            )

    if tipo_tendencia == "Decreciente":
        st.warning(f"**Tendencia decreciente.** {explicacion_tendencia}")
    elif tipo_tendencia == "Creciente":
        st.success(f"**Tendencia creciente.** {explicacion_tendencia}")
    elif tipo_tendencia == "Estable":
        st.info(f"**Tendencia estable.** {explicacion_tendencia}")
    else:
        st.info(explicacion_tendencia)

    st.subheader("Importes diarios atípicos")
    st.caption(
        "Se revisan los días con ventas de los últimos 90 días del historial. "
        "Se señalan importes fuera de 1,5 rangos intercuartílicos. "
        "Cada alerta es un importe que conviene revisar."
    )
    if dias_evaluados < 14:
        st.info("Se necesitan al menos 14 días con ventas para detectar importes atípicos.")
    elif alertas_ventas.empty:
        st.info(f"Sin importes atípicos en {dias_evaluados} días con ventas.")
    else:
        st.caption(f"{len(alertas_ventas)} alertas en {dias_evaluados} días con ventas.")
        mostrar_tabla(
            alertas_ventas,
            hide_index=True,
            column_config={"Ventas (S/)": st.column_config.NumberColumn(format="S/ %.2f")},
        )

    st.subheader("Productos más vendidos")

    top = analysis.productos_mas_vendidos(datos_historicos)

    if not top.empty:
        mostrar_tabla(top, width="stretch", hide_index=True, height=360)

    else:

        st.info(
            "Todavía no existen ventas suficientes para realizar este análisis."
        )

    st.subheader("Productos con stock bajo")

    bajo = analysis.productos_stock_bajo()

    if not bajo.empty:
        mostrar_tabla(bajo, width="stretch", hide_index=True, height=360)

    else:

        st.success(
            "No existen productos con stock bajo."
        )

    st.subheader("Clasificación del comportamiento de productos")

    comportamiento = analysis.analisis_productos()

    if not comportamiento.empty:
        mostrar_tabla(
            comportamiento[
                [
                    "codigo",
                    "nombre",
                    "categoria",
                    "stock",
                    "stock_minimo",
                    "unidades_vendidas",
                    "analisis"
                ]
            ],
            width="stretch",
            hide_index=True,
            height=420,
        )

    else:

        st.info(
            "No existen productos para analizar."
        )

# ==========================================================
# PREDICCIÓN DE DEMANDA
# ==========================================================

elif menu == "Predicción de demanda":

    st.header("Predicción de demanda", icon=":material/trending_up:")

    st.write(
        "Pronóstico de demanda a partir del historial de ventas. El sistema "
        "compara alternativas en tres periodos históricos y conserva "
        "la que obtiene menor error de forma consistente."
    )

    st.info(
        "El entrenamiento prueba tres cortes cronológicos de 7 días, muestra el "
        "error por producto y solo activa un modelo que supera la referencia de "
        "ventas de hace 7 días en el conjunto y en la mayoría de los periodos."
    )

    def mostrar_detalle_evaluacion(evaluacion):
        cortes = evaluacion.get("cortes_evaluacion", [])
        if cortes:
            detalle_cortes = pd.DataFrame(cortes).rename(
                columns={
                    "fecha_corte": "Fecha de corte",
                    "fecha_inicio_prueba": "Inicio de prueba",
                    "fecha_fin_prueba": "Fin de prueba",
                    "observaciones_entrenamiento": "Días de entrenamiento",
                    "observaciones_prueba": "Días evaluados",
                    "mae": "MAE del modelo",
                    "mae_baseline_7_dias": "MAE de referencia",
                    "ventanas_prueba_7_dias": "Ventanas de 7 días",
                }
            )
            st.subheader("Evaluación por periodo")
            st.dataframe(
                detalle_cortes,
                width="stretch",
                hide_index=True,
            )

        precision = evaluacion.get("precision_por_producto", [])
        if not precision:
            return
        detalle = pd.DataFrame(precision).rename(
            columns={
                "codigo_producto": "Código",
                "observaciones": "Días evaluados",
                "mae": "MAE del modelo",
                "mae_baseline_7_dias": "MAE de referencia",
                "wape_porcentaje": "WAPE (%)",
                "supera_baseline": "Supera referencia",
            }
        )
        st.subheader("Precisión por producto")
        st.dataframe(
            detalle,
            width="stretch",
            height=360,
            hide_index=True,
        )

    st.warning(
        "Los días sin ventas registradas se interpretan como cero ventas. "
        "Si el producto estuvo agotado, la demanda real podría ser mayor."
    )

    estado_actual = prediction.estado_modelo()
    if estado_actual["estado"] == "ok":
        st.success(
            "Pronóstico disponible con el historial validado. "
            f"Entrenado el {estado_actual['fecha_entrenamiento']}; "
            f"historial hasta {estado_actual['fecha_fin_historial']}."
        )
        if (
            estado_actual.get("almacenamiento") == "archivo local"
            and database.usar_supabase()
        ):
            st.warning(
                "Este modelo solo está guardado en el almacenamiento temporal del "
                "servidor. Al entrenar, la aplicación intenta crear la tabla de "
                "Supabase automáticamente. Si la conexión no tiene permiso, ejecute "
                "migracion_modelo_demanda.sql en Supabase y vuelva a entrenarlo."
            )
        st.caption(
            "Las ventas nuevas se usan como contexto para pronosticar. "
            "Vuelve a entrenar para que el modelo aprenda también de esos registros."
        )
        evaluacion_actual = estado_actual.get("evaluacion")
        if isinstance(evaluacion_actual, dict) and evaluacion_actual:
            st.caption(
                f"Evaluación temporal: MAE {evaluacion_actual['mae']:.2f} unidades; "
                f"referencia de 7 días {evaluacion_actual['mae_baseline_7_dias']:.2f}; "
                f"{evaluacion_actual.get('cortes_que_superan_baseline', 0)} de "
                f"{evaluacion_actual.get('cantidad_cortes', 0)} periodos superaron la referencia."
            )
            mostrar_detalle_evaluacion(evaluacion_actual)
    else:
        st.info(estado_actual.get("mensaje", "Entrene el modelo para habilitar predicciones."))

    if es_admin and st.button("Entrenar y evaluar modelo", key="entrenar_modelo_demanda"):
        with st.spinner("Preparando el historial y evaluando el pronóstico..."):
            resultado_entrenamiento = prediction.entrenar_modelo()
        evaluacion = resultado_entrenamiento.get("evaluacion")
        if resultado_entrenamiento["estado"] in ("ok", "ok_local"):
            st.success(resultado_entrenamiento["mensaje"])
        elif resultado_entrenamiento["estado"] == "no_supera_baseline":
            st.warning(resultado_entrenamiento["mensaje"])
        else:
            st.warning(resultado_entrenamiento["mensaje"])
        if isinstance(evaluacion, dict) and evaluacion:
            m1, m2, m3 = st.columns(3)
            m1.metric("MAE del modelo", f"{evaluacion['mae']:.2f} unidades")
            m2.metric("MAE de referencia", f"{evaluacion['mae_baseline_7_dias']:.2f} unidades")
            m3.metric("WAPE del modelo", f"{evaluacion['wape_porcentaje']:.1f}%")
            st.caption(
                f"Prueba cronológica: {evaluacion['fecha_inicio_prueba']} a "
                f"{evaluacion['fecha_fin_prueba']}; "
                f"{evaluacion['observaciones_prueba']} observaciones en "
                f"{evaluacion['ventanas_prueba_7_dias']} ventanas de 7 días y "
                f"{evaluacion['cantidad_cortes']} cortes temporales."
            )
            st.caption(
                f"La referencia se superó en "
                f"{evaluacion['cortes_que_superan_baseline']} de "
                f"{evaluacion['cantidad_cortes']} cortes. "
                "Los errores por producto agregan las observaciones de todos los cortes."
            )
            mostrar_detalle_evaluacion(evaluacion)

    if estado_actual["estado"] == "ok":
        with st.expander("Resumen de reposición del catálogo"):
            st.caption("Calcula la necesidad de reposición de cada producto según su plazo de entrega.")
            if st.button("Evaluar reposición del catálogo", key="evaluar_reposicion_catalogo"):
                inicio_reposicion = perf_counter()
                with st.spinner("Evaluando el catálogo..."):
                    reposicion = prediction.analizar_productos()
                if reposicion.empty:
                    st.info("No hay productos para evaluar.")
                else:
                    validos = reposicion["estado_prediccion"].eq("ok")
                    pedidos = reposicion.loc[validos & reposicion["cantidad_sugerida"].gt(0)]
                    st.metric("Recomendaciones de reposición", len(pedidos))
                    st.caption(
                        f"{int(validos.sum())} de {len(reposicion)} productos con pronóstico "
                        f"válido · {formatear_numero_es(perf_counter() - inicio_reposicion, 3)} s."
                    )
                    if not pedidos.empty:
                        mostrar_tabla(
                            pedidos[["codigo", "nombre", "dias_cobertura", "demanda_cobertura",
                                     "stock_actual", "stock_minimo", "cantidad_sugerida"]].rename(
                                columns={
                                    "codigo": "Código", "nombre": "Producto",
                                    "dias_cobertura": "Días de cobertura",
                                    "demanda_cobertura": "Demanda estimada",
                                    "stock_actual": "Stock actual", "stock_minimo": "Stock mínimo",
                                    "cantidad_sugerida": "Unidades sugeridas",
                                }
                            ),
                            hide_index=True,
                        )

    productos = prediction.obtener_productos()

    if productos.empty:

        st.warning(
            "No existen productos registrados."
        )

    else:

        opciones = {
            int(fila["id"]): (
                f"{fila['codigo']} - {fila['nombre']} | "
                f"Stock: {fila['stock']}"
            )
            for _, fila in productos.iterrows()
        }

        producto_id = st.selectbox(
            "Seleccionar producto",
            list(opciones.keys()),
            format_func=lambda valor: opciones[valor]
        )

        producto_seleccionado = productos[
            productos["id"] == producto_id
        ].iloc[0]
        dias_entrega = int(producto_seleccionado.get("dias_entrega", 0) or 0)
        dias = st.number_input(
            "Días de cobertura",
            min_value=max(1, dias_entrega),
            max_value=30,
            value=max(7, dias_entrega),
            step=1,
            key=f"dias_cobertura_prediccion_{producto_id}",
            help="El periodo cubre como mínimo el plazo de entrega configurado para este producto.",
        )

        if st.button("Generar predicción"):

            resultado = prediction.predecir_demanda(
                producto_id,
                int(dias)
            )

            if resultado["estado"] == "ok":

                c1, c2, c3 = st.columns(3)

                with c1:
                    st.metric(
                        "Días históricos",
                        resultado["dias_historicos"]
                    )

                with c2:
                    st.metric(
                        "Demanda estimada",
                        f"{resultado['demanda_predicha']:.2f} unidades"
                    )

                with c3:
                    st.metric(
                        "Estado del pronóstico",
                        "Disponible"
                    )

                st.caption(
                    f"El pronóstico cubre {resultado['dias_cobertura']} días "
                    f"para un plazo de entrega configurado de {resultado['dias_entrega']} días. "
                    "La reposición también conserva el stock mínimo como reserva."
                )

                evaluacion = resultado.get("evaluacion")
                if isinstance(evaluacion, dict) and evaluacion:
                    st.caption(
                        f"Error MAE en evaluación temporal: "
                        f"{evaluacion['mae']:.2f} unidades por producto y día."
                    )

                st.divider()

                st.subheader(
                    f"Demanda estimada del "
                    f"{pd.to_datetime(resultado['fechas_prediccion'][0]).strftime('%d/%m/%Y')} "
                    f"al {pd.to_datetime(resultado['fechas_prediccion'][-1]).strftime('%d/%m/%Y')}"
                )

                st.caption(
                    "Última venta registrada del producto: "
                    f"{pd.to_datetime(resultado['fecha_ultima_venta_producto']).strftime('%d/%m/%Y')}. "
                    "La predicción parte del día posterior a la fecha de corte "
                    f"{pd.to_datetime(resultado['fecha_base_prediccion']).strftime('%d/%m/%Y')}; "
                    "los días sin registros se interpretan como cero ventas."
                )

                fechas_grafico_pred = pd.to_datetime(
                    resultado["fechas_prediccion"]
                )
                valores_grafico_pred = [
                    round(float(valor), 2)
                    for valor in resultado["predicciones"]
                ]
                datos_tabla_pred = {
                    "Fecha": [
                        pd.to_datetime(fecha).strftime("%d/%m/%Y")
                        for fecha in resultado["fechas_prediccion"]
                    ],
                    "Unidades estimadas": [
                        formatear_numero_es(valor, 2)
                        for valor in resultado["predicciones"]
                    ]
                }

                grafico_prediccion = go.Figure(
                    go.Scatter(
                        x=fechas_grafico_pred,
                        y=valores_grafico_pred,
                        mode="lines+markers",
                        line={"width": 3},
                        marker={"size": 7},
                        hovertemplate=(
                            "%{x|%d/%m/%Y}<br>"
                            "Unidades estimadas: %{y:.2f}<extra></extra>"
                        ),
                    )
                )
                grafico_prediccion.update_layout(
                    height=430,
                    margin={"l": 20, "r": 20, "t": 20, "b": 20},
                    hovermode="x unified",
                    xaxis={
                        "title": None,
                        "tickmode": "array",
                        "tickvals": fechas_grafico_pred,
                        "tickformat": "%d/%m",
                        "fixedrange": True,
                    },
                    yaxis={
                        "title": "Unidades estimadas",
                        "rangemode": "tozero",
                        "fixedrange": True,
                    },
                    separators=",.",
                    uirevision="prediccion-demanda",
                )
                mostrar_grafico_fijo(
                    grafico_prediccion,
                    "grafico_prediccion_demanda",
                )

                st.subheader("Detalle de la predicción")

                mostrar_tabla(
                    datos_tabla_pred,
                    width="stretch",
                    hide_index=True,
                    column_config={
                        "Unidades estimadas": st.column_config.TextColumn(
                            "Unidades estimadas",
                            alignment="center",
                        ),
                    },
                )

                st.subheader("Necesidad de reposición")

                producto = productos[
                    productos["id"] == producto_id
                ].iloc[0]

                stock_actual = float(producto["stock"])
                stock_minimo = float(producto["stock_minimo"])

                cantidad_sugerida = max(
                    0,
                    math.ceil(
                        float(resultado["demanda_predicha"])
                        + stock_minimo
                        - stock_actual
                    )
                )

                if cantidad_sugerida > 0:

                    st.warning(
                        f"Se estima una necesidad de reposición "
                        f"de aproximadamente {cantidad_sugerida} unidad(es), "
                        f"considerando la demanda proyectada y el stock mínimo."
                    )

                else:

                    st.success(
                        "El stock actual cubre la demanda estimada "
                        "y el stock mínimo configurado."
                    )

                filas_pdf = [
                    [
                        pd.to_datetime(fecha).strftime("%d/%m/%Y"),
                        formatear_numero_es(valor, 2),
                    ]
                    for fecha, valor in zip(
                        resultado["fechas_prediccion"],
                        resultado["predicciones"],
                    )
                ]
                periodo_pdf = (
                    f"{pd.to_datetime(resultado['fechas_prediccion'][0]).strftime('%d/%m/%Y')} "
                    f"al {pd.to_datetime(resultado['fechas_prediccion'][-1]).strftime('%d/%m/%Y')}"
                )
                datos_informe_pdf = {
                    "nombre_producto": producto["nombre"],
                    "codigo_producto": producto["codigo"],
                    "periodo": periodo_pdf,
                    "dias_historicos": resultado["dias_historicos"],
                    "fecha_ultima_venta": pd.to_datetime(
                        resultado["fecha_ultima_venta_producto"]
                    ).strftime("%d/%m/%Y"),
                    "fecha_base": pd.to_datetime(
                        resultado["fecha_base_prediccion"]
                    ).strftime("%d/%m/%Y"),
                    "demanda_predicha": resultado["demanda_predicha"],
                    "promedio_diario": resultado["promedio_diario_predicho"],
                    "dias_entrega": resultado["dias_entrega"],
                    "dias_cobertura": resultado["dias_cobertura"],
                    "stock_actual": stock_actual,
                    "stock_minimo": stock_minimo,
                    "cantidad_sugerida": cantidad_sugerida,
                    "filas_prediccion": filas_pdf,
                    "evaluacion": resultado.get("evaluacion", {}),
                }
                try:
                    contenido_pdf = pdf_report.construir_informe_prediccion(
                        datos_informe_pdf
                    )
                    codigo_archivo = re.sub(
                        r"[^a-z0-9_-]+",
                        "-",
                        str(producto["codigo"]).lower(),
                    ).strip("-") or "producto"
                    st.download_button(
                        "Descargar informe PDF",
                        data=contenido_pdf,
                        file_name=f"diagnostico_demanda_{codigo_archivo}.pdf",
                        mime="application/pdf",
                        on_click="ignore",
                        key="descargar_informe_prediccion_pdf",
                        use_container_width=True,
                    )
                except ImportError:
                    st.error(
                        "No está instalada la dependencia para generar PDF. "
                        "Instale las dependencias del proyecto y vuelva a intentarlo."
                    )

            else:

                st.warning(resultado["mensaje"])
