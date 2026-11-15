"""Operaciones de inventario, ventas y compras compartidas por ambas interfaces."""

import io
import math
import re
import sys
import unicodedata
from datetime import date, datetime

import pandas as pd
import streamlit as st

import database


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

COLUMNAS_EXCEL_PRODUCTOS = (
    "ID", "Código", "Producto", "Categoría", "Precio compra (S/)",
    "Precio venta (S/)", "Stock", "Stock mínimo", "Días de entrega",
)
ANCHOS_EXCEL_PRODUCTOS = (11, 21, 37, 26, 21, 21, 13, 17, 19)
MONEDA_EXCEL = '"S/ " #,##0.00'
FORMATOS_EXCEL_PRODUCTOS = {"B": "@", "E": MONEDA_EXCEL, "F": MONEDA_EXCEL}
ANCHOS_EXCEL_MOVIMIENTOS = (19, 25, 14, 32, 26)
FORMATOS_EXCEL_MOVIMIENTOS = {"A": "dd/mm/yyyy", "B": "@", "D": MONEDA_EXCEL, "E": "@"}


def dar_formato_excel(hoja, anchos, formatos, *, captura=False, nombre_tabla=None):
    """Formatea datos y plantillas con el encabezado en la primera fila."""
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter
    from openpyxl.worksheet.table import Table, TableStyleInfo

    hoja.freeze_panes = "A2"
    hoja.sheet_view.showGridLines = False
    hoja.sheet_properties.tabColor = "2457B4"
    hoja.row_dimensions[1].height = 32
    for celda in hoja[1]:
        celda.font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        celda.fill = PatternFill("solid", fgColor="20385F")
        celda.alignment = Alignment(vertical="center", wrap_text=True, indent=1)

    ultima_fila = hoja.max_row
    if nombre_tabla and ultima_fila > 1:
        tabla = Table(displayName=nombre_tabla, ref=hoja.dimensions)
        tabla.tableStyleInfo = TableStyleInfo(name="TableStyleMedium2", showRowStripes=True)
        hoja.add_table(tabla)
    else:
        hoja.auto_filter.ref = hoja.dimensions

    fondo_alterno = PatternFill("solid", fgColor="EDF3FC")
    fondo_claro = PatternFill("solid", fgColor="FFFFFF")
    texto = Font(name="Calibri", size=11, color="182B48")
    alineacion = Alignment(vertical="center")
    for i, ancho in enumerate(anchos, start=1):
        letra = get_column_letter(i)
        columna = hoja.column_dimensions[letra]
        columna.width = ancho
        if letra in formatos:
            columna.number_format = formatos[letra]

    if captura:
        ultima_fila = max(ultima_fila, 26)
        hoja.auto_filter.ref = f"A1:{get_column_letter(len(anchos))}{ultima_fila}"
    for fila in hoja.iter_rows(min_row=2, max_row=ultima_fila):
        for celda in fila:
            if celda.data_type in ("f", "e"):
                celda.data_type = "s"
            if captura:
                celda.fill = fondo_alterno if celda.row % 2 == 0 else fondo_claro
            celda.font = texto
            celda.alignment = alineacion
            if celda.column_letter in formatos:
                celda.number_format = formatos[celda.column_letter]


def agregar_guia_excel(libro, titulo, instrucciones):
    """Presenta las instrucciones fuera de la hoja que lee el importador."""
    from openpyxl.styles import Alignment, Font, PatternFill

    hoja = libro.create_sheet("Instrucciones")
    hoja.sheet_view.showGridLines = False
    hoja.sheet_properties.tabColor = "227D72"
    hoja.column_dimensions["A"].width = 10
    hoja.column_dimensions["B"].width = 82
    hoja.merge_cells("A1:B1")
    hoja["A1"] = titulo
    hoja["A1"].font = Font(name="Calibri", size=16, bold=True, color="FFFFFF")
    hoja["A1"].fill = PatternFill("solid", fgColor="20385F")
    hoja["A1"].alignment = Alignment(vertical="center", indent=1)
    hoja.row_dimensions[1].height = 35
    for fila, texto in enumerate(instrucciones, start=3):
        hoja.cell(fila, 1, fila - 2)
        hoja.cell(fila, 2, texto)
        for celda in hoja[fila]:
            celda.fill = PatternFill("solid", fgColor="EDF3FC" if fila % 2 else "F7F9FD")
            celda.font = Font(name="Calibri", size=11, color="182B48", bold=celda.column == 1)
            celda.alignment = Alignment(
                horizontal="center" if celda.column == 1 else "left",
                vertical="center", wrap_text=True,
            )
        hoja.row_dimensions[fila].height = 36 if len(texto) > 85 else 26


def validar_columna_excel(hoja, columna, tipo, operador, minimo, maximo=None):
    from openpyxl.worksheet.datavalidation import DataValidation

    regla = DataValidation(
        type=tipo, operator=operador, formula1=minimo, formula2=maximo,
        allow_blank=True, showErrorMessage=True,
    )
    regla.errorTitle = "Valor fuera de rango"
    regla.error = "Consulta la hoja Instrucciones para conocer los valores admitidos."
    hoja.add_data_validation(regla)
    regla.add(f"{columna}2:{columna}1048576")


@st.cache_data(ttl=60, show_spinner=False, max_entries=3)
def generar_excel_productos(productos):
    filas = [
        {
            "ID": p[0],
            "Código": p[1],
            "Producto": p[2],
            "Categoría": p[3] or "",
            "Precio compra (S/)": float(p[4]),
            "Precio venta (S/)": float(p[5]),
            "Stock": p[6],
            "Stock mínimo": p[7],
            "Días de entrega": p[8],
        }
        for p in productos
    ]

    archivo = io.BytesIO()
    with pd.ExcelWriter(archivo, engine="openpyxl") as escritor:
        pd.DataFrame(filas, columns=list(COLUMNAS_EXCEL_PRODUCTOS)).to_excel(
            escritor, index=False, sheet_name="Productos",
        )
        dar_formato_excel(
            escritor.sheets["Productos"], ANCHOS_EXCEL_PRODUCTOS,
            FORMATOS_EXCEL_PRODUCTOS, nombre_tabla="TablaProductos",
        )
        agregar_guia_excel(escritor.book, "Catálogo de productos", [
            "Conserva los encabezados y la hoja Productos si vas a importar este archivo.",
            "Conserva el ID y el código al actualizar un producto existente.",
            "Para agregar un producto, deja el ID vacío y usa un código nuevo.",
        ])
    return archivo.getvalue()


@st.cache_data(ttl=60, show_spinner=False, max_entries=3)
def crear_plantilla_productos_excel():
    """Genera una plantilla para registrar productos desde Excel."""
    archivo = io.BytesIO()
    with pd.ExcelWriter(archivo, engine="openpyxl") as escritor:
        pd.DataFrame(columns=list(COLUMNAS_EXCEL_PRODUCTOS)).to_excel(
            escritor, index=False, sheet_name="Productos",
        )
        hoja = escritor.sheets["Productos"]
        dar_formato_excel(hoja, ANCHOS_EXCEL_PRODUCTOS, FORMATOS_EXCEL_PRODUCTOS, captura=True)
        validar_columna_excel(hoja, "E", "decimal", "greaterThanOrEqual", 0)
        validar_columna_excel(hoja, "F", "decimal", "greaterThan", 0)
        for columna in ("G", "H"):
            validar_columna_excel(hoja, columna, "whole", "greaterThanOrEqual", 0)
        validar_columna_excel(hoja, "I", "whole", "between", 0, 30)
        agregar_guia_excel(escritor.book, "Plantilla de productos", [
            "Completa una fila por producto en la hoja Productos. Conserva los encabezados y evita filas de totales.",
            "Deja el ID vacío para un producto nuevo. Para actualizar, conserva el ID y el código exportados.",
            "Escribe un código único y el nombre del producto. La categoría es opcional.",
            "El precio de compra puede ser cero. El precio de venta debe ser mayor que cero.",
            "Ingresa cantidades enteras no negativas. Si omites el stock mínimo, se usará 5.",
            "El plazo admite 0 a 30 días. Si lo omites, se conserva el valor actual o se usa 0 para productos nuevos.",
        ])
    return archivo.getvalue()


def validar_productos_excel(contenido):
    """Valida el catálogo de productos de Excel sin modificar la base de datos."""
    try:
        original = pd.read_excel(io.BytesIO(contenido), sheet_name=0, dtype=object)
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

    for numero_fila, (_, datos_fila) in enumerate(original.iterrows(), start=2):
        fila = datos_fila.to_dict()
        if all(_celda_excel_vacia(valor) for valor in fila.values()):
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
            5.0 if _celda_excel_vacia(valor_stock_minimo)
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
        if _celda_excel_vacia(valor_dias_entrega):
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
        dar_formato_excel(hoja, ANCHOS_EXCEL_MOVIMIENTOS, FORMATOS_EXCEL_MOVIMIENTOS, captura=True)
        validar_columna_excel(hoja, "C", "whole", "greaterThan", 0)
        validar_columna_excel(hoja, "D", "decimal", "greaterThan", 0)
        agregar_guia_excel(escritor.book, "Plantilla de ventas", [
            "Completa una fila por producto vendido en la hoja Ventas. Conserva los encabezados y evita filas de totales.",
            "Usa la fecha de la boleta y el código del producto registrado en Humbertito.",
            "Ingresa la cantidad entera y el precio unitario de la venta en soles.",
            "El número de boleta es opcional. Repite la fecha y la boleta para agrupar sus productos.",
        ])

    archivo.seek(0)
    return archivo.getvalue()


def _normalizar_encabezado_excel(valor):
    texto = unicodedata.normalize("NFKD", str(valor))
    texto = "".join(caracter for caracter in texto if not unicodedata.combining(caracter))
    return re.sub(r"[^a-z0-9]+", " ", texto.lower()).strip()


def _celda_excel_vacia(valor: object) -> bool:
    """Comprueba si una celda de Excel está vacía, incluida una cadena en blanco."""
    if isinstance(valor, str):
        return not valor.strip()
    return pd.api.types.is_scalar(valor) and bool(pd.isna([valor])[0])


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


def _fecha_excel(valor) -> date | None:
    """Convierte una fecha de Excel o su número de serie a una fecha de calendario."""
    try:
        if isinstance(valor, (int, float)) and not isinstance(valor, bool):
            fecha = pd.Timestamp("1899-12-30") + pd.to_timedelta(float(valor), unit="D")
        else:
            fecha = pd.to_datetime(valor, dayfirst=True, format="mixed", errors="coerce")
    except (TypeError, ValueError, OverflowError):
        return None
    return fecha.date() if isinstance(fecha, pd.Timestamp) else None


@st.cache_data(ttl=180, show_spinner=False, max_entries=6)
def validar_ventas_excel(_contenido, hash_contenido):
    """Lee y valida el Excel sin modificar la base de datos."""
    try:
        original = pd.read_excel(io.BytesIO(_contenido), sheet_name=0, dtype=object)
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

    for numero_fila, (_, datos_fila) in enumerate(original.iterrows(), start=2):
        fila = datos_fila.to_dict()
        if all(_celda_excel_vacia(valor) for valor in fila.values()):
            continue

        errores_fila = []
        producto = None

        valor_codigo = fila[columnas["codigo"]] if "codigo" in columnas else None
        valor_nombre = fila[columnas["producto"]] if "producto" in columnas else None
        if not _celda_excel_vacia(valor_codigo):
            producto = por_codigo.get(str(valor_codigo).strip().casefold())
            if producto is None:
                errores_fila.append(f"código de producto no registrado: {valor_codigo}")
        elif not _celda_excel_vacia(valor_nombre):
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
            fecha_parseada = _fecha_excel(valor_fecha)
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
def generar_excel_historial(tabla, nombre_hoja, campos_importe):
    datos = pd.DataFrame(tabla).copy()
    formatos = {}
    if not datos.empty:
        from openpyxl.utils import get_column_letter

        def fecha_de_excel(valor):
            if isinstance(valor, str):
                try:
                    fecha = datetime.fromisoformat(valor)
                except ValueError:
                    return valor
                if fecha.tzinfo is None:
                    return fecha
            return valor

        datos["Fecha"] = datos["Fecha"].map(fecha_de_excel)
        for campo in campos_importe:
            datos[campo] = pd.to_numeric(datos[campo])
        for i, columna in enumerate(datos.columns, start=1):
            letra = get_column_letter(i)
            if columna in campos_importe:
                formatos[letra] = MONEDA_EXCEL
            elif columna == "Fecha":
                formatos[letra] = "dd/mm/yyyy hh:mm:ss"
            elif columna in ("Boleta", "Comprobante"):
                formatos[letra] = "@"

    salida = io.BytesIO()
    with pd.ExcelWriter(salida, engine="openpyxl") as escritor:
        datos.to_excel(escritor, index=False, sheet_name=nombre_hoja)
        dar_formato_excel(
            escritor.sheets[nombre_hoja],
            (13, 25, 23, 23, 38, 14, 21, 23)[:len(datos.columns)],
            formatos, nombre_tabla="TablaHistorial",
        )
        agregar_guia_excel(escritor.book, nombre_hoja, [
            "Cada fila corresponde a un producto de una transacción.",
            "Suma los subtotales de las líneas para obtener el importe total. "
            "El total del comprobante puede repetirse en varias filas.",
        ])
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
        dar_formato_excel(hoja, ANCHOS_EXCEL_MOVIMIENTOS, FORMATOS_EXCEL_MOVIMIENTOS, captura=True)
        validar_columna_excel(hoja, "C", "whole", "greaterThan", 0)
        validar_columna_excel(hoja, "D", "decimal", "greaterThan", 0)

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
        dar_formato_excel(
            escritor.sheets["Ejemplo DEMO - NO IMPORTAR"],
            ANCHOS_EXCEL_MOVIMIENTOS, FORMATOS_EXCEL_MOVIMIENTOS,
            nombre_tabla="TablaEjemploCompras",
        )
        agregar_guia_excel(escritor.book, "Plantilla de compras", [
            "Completa una fila por producto comprado en la hoja Compras. Conserva los encabezados y evita filas de totales.",
            "Usa la fecha y el código de producto registrados, una cantidad entera y el costo unitario real.",
            "Repite la fecha y el comprobante en las líneas que pertenecen a la misma compra.",
            "La hoja de ejemplo contiene datos ficticios. Usa los datos del comprobante real en Compras.",
        ])

    archivo.seek(0)
    return archivo.getvalue()


@st.cache_data(ttl=180, show_spinner=False, max_entries=6)
def validar_compras_excel(_contenido, hash_contenido):
    """Valida las compras del Excel antes de insertar o modificar el inventario."""
    try:
        original = pd.read_excel(io.BytesIO(_contenido), sheet_name="Compras", dtype=object)
    except ValueError:
        try:
            original = pd.read_excel(io.BytesIO(_contenido), sheet_name=0, dtype=object)
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

    for numero_fila, (_, datos_fila) in enumerate(original.iterrows(), start=2):
        fila = datos_fila.to_dict()
        if all(_celda_excel_vacia(valor) for valor in fila.values()):
            continue

        errores_fila = []
        producto = None
        valor_codigo = fila[columnas["codigo"]] if "codigo" in columnas else None
        valor_nombre = fila[columnas["producto"]] if "producto" in columnas else None
        if not _celda_excel_vacia(valor_codigo):
            producto = por_codigo.get(str(valor_codigo).strip().casefold())
            if producto is None:
                errores_fila.append(f"código de producto no registrado: {valor_codigo}")
        elif not _celda_excel_vacia(valor_nombre):
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
            fecha_parseada = _fecha_excel(valor_fecha)
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
