import sqlite3

DB = "data/humbertito.db"

conn = sqlite3.connect(DB)
cursor = conn.cursor()

cursor.execute(
    "SELECT id, precio_venta FROM productos WHERE codigo = ?",
    ("LIB002",)
)

producto = cursor.fetchone()

if not producto:
    print("No se encontró el producto LIB002.")
    conn.close()
    exit()

producto_id, precio_venta = producto

ventas = [
    ("2026-09-14 10:00:00", 2),
    ("2026-09-15 11:00:00", 3),
    ("2026-09-16 12:00:00", 4),
]

try:
    for fecha, cantidad in ventas:

        subtotal = cantidad * precio_venta

        cursor.execute(
            """
            INSERT INTO ventas (fecha, total)
            VALUES (?, ?)
            """,
            (fecha, subtotal)
        )

        venta_id = cursor.lastrowid

        cursor.execute(
            """
            INSERT INTO detalle_ventas
            (venta_id, producto_id, cantidad, precio_unitario, subtotal)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                venta_id,
                producto_id,
                cantidad,
                precio_venta,
                subtotal
            )
        )

    conn.commit()

    print("===================================")
    print("   HISTORIAL DE PRUEBA CREADO")
    print("===================================")
    print("Producto: LIB002 - Lapicero Azul")
    print("14/09/2026 -> 2 unidades")
    print("15/09/2026 -> 3 unidades")
    print("16/09/2026 -> 4 unidades")
    print("-----------------------------------")
    print("3 días diferentes registrados.")
    print("Predicción lista para ser probada.")

except Exception as e:
    conn.rollback()
    print("ERROR:", e)

finally:
    conn.close()