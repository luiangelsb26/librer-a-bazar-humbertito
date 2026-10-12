import hashlib
from datetime import datetime
import database


# ==========================================================
# CONFIGURACIÓN DE LA BASE DE DATOS
# ==========================================================

def conectar():
    return database.conectar()


# ==========================================================
# SEGURIDAD DE CONTRASEÑAS
# ==========================================================

def generar_hash(password):
    return hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()


# ==========================================================
# INICIALIZAR TABLA DE USUARIOS
# ==========================================================

def inicializar():

    con = conectar()
    cur = con.cursor()
    id_type = (
        "SERIAL PRIMARY KEY"
        if database.usar_supabase()
        else "INTEGER PRIMARY KEY AUTOINCREMENT"
    )

    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS usuarios (
            id {id_type},
            username TEXT UNIQUE NOT NULL,
            nombre TEXT NOT NULL,
            password TEXT NOT NULL,
            rol TEXT NOT NULL DEFAULT 'empleado',
            activo INTEGER NOT NULL DEFAULT 1,
            creado TEXT NOT NULL
        )
    """)

    con.commit()
    con.close()


# ==========================================================
# CANTIDAD DE USUARIOS
# ==========================================================

def cantidad_usuarios():

    con = conectar()
    cur = con.cursor()

    cur.execute("""
        SELECT COUNT(*)
        FROM usuarios
    """)

    cantidad = cur.fetchone()[0]

    con.close()

    return cantidad


# ==========================================================
# CREAR USUARIO
# ==========================================================

def crear_usuario(
    username,
    nombre,
    password,
    rol="empleado"
):

    username = username.strip()
    nombre = nombre.strip()

    if not username:
        raise ValueError(
            "El nombre de usuario es obligatorio."
        )

    if not nombre:
        raise ValueError(
            "El nombre completo es obligatorio."
        )

    if not password:
        raise ValueError(
            "La contraseña es obligatoria."
        )

    if rol not in ("admin", "empleado"):
        raise ValueError(
            "El rol seleccionado no es válido."
        )

    con = conectar()
    cur = con.cursor()

    # Comprobar si ya existe
    cur.execute("""
        SELECT id
        FROM usuarios
        WHERE username = ?
    """, (
        username,
    ))

    existente = cur.fetchone()

    if existente:
        con.close()

        raise ValueError(
            "El nombre de usuario ya existe."
        )

    password_hash = generar_hash(password)

    fecha_creacion = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    cur.execute("""
        INSERT INTO usuarios (
            username,
            nombre,
            password,
            rol,
            activo,
            creado
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        username,
        nombre,
        password_hash,
        rol,
        1,
        fecha_creacion
    ))

    con.commit()
    con.close()


# ==========================================================
# VERIFICAR USUARIO
# ==========================================================

def verificar_usuario(
    username,
    password
):

    username = username.strip()

    password_hash = generar_hash(password)

    con = conectar()
    cur = con.cursor()

    cur.execute("""
        SELECT
            id,
            username,
            nombre,
            rol,
            activo
        FROM usuarios
        WHERE username = ?
          AND password = ?
          AND activo = 1
    """, (
        username,
        password_hash
    ))

    fila = cur.fetchone()

    con.close()

    # Usuario incorrecto
    if fila is None:
        return None

    # IMPORTANTE:
    # app.py utiliza:
    # usuario_actual["rol"]
    #
    # Por eso debemos devolver un diccionario,
    # no una tupla.

    return {
        "id": fila[0],
        "username": fila[1],
        "nombre": fila[2],
        "rol": fila[3],
        "activo": fila[4]
    }


# ==========================================================
# LISTAR USUARIOS
# ==========================================================

def listar_usuarios():

    con = conectar()
    cur = con.cursor()

    cur.execute("""
        SELECT
            id,
            username,
            nombre,
            rol,
            activo,
            creado
        FROM usuarios
        ORDER BY id
    """)

    usuarios = cur.fetchall()

    con.close()

    return usuarios


# ==========================================================
# ELIMINAR USUARIO
# ==========================================================

def eliminar_usuario(usuario_id, usuario_actual_id=None):
    if usuario_id is None:
        raise ValueError("Selecciona una cuenta válida.")

    if str(usuario_id) == str(usuario_actual_id):
        raise ValueError("No puedes eliminar la cuenta que estás usando.")

    con = conectar()
    cur = con.cursor()

    try:
        cur.execute("""
            SELECT rol
            FROM usuarios
            WHERE id = ?
        """, (usuario_id,))
        usuario = cur.fetchone()

        if usuario is None:
            raise ValueError("La cuenta seleccionada ya no existe.")

        if usuario[0] == "admin":
            cur.execute("""
                SELECT COUNT(*)
                FROM usuarios
                WHERE rol = 'admin'
            """)
            if cur.fetchone()[0] <= 1:
                raise ValueError(
                    "No se puede eliminar el último administrador."
                )

        cur.execute("""
            DELETE FROM usuarios
            WHERE id = ?
        """, (usuario_id,))

        if cur.rowcount != 1:
            raise ValueError("No se pudo encontrar la cuenta para eliminar.")

        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


# ==========================================================
# TRANSFERIR ADMINISTRACIÓN Y ELIMINAR CUENTA ACTUAL
# ==========================================================

def transferir_administracion_y_eliminar_usuario(
    usuario_actual_id,
    nuevo_admin_id,
):
    if usuario_actual_id is None or nuevo_admin_id is None:
        raise ValueError("Selecciona una cuenta válida para el traspaso.")

    if str(usuario_actual_id) == str(nuevo_admin_id):
        raise ValueError("Debes seleccionar otra cuenta como nuevo administrador.")

    con = conectar()
    cur = con.cursor()

    try:
        cur.execute("""
            SELECT rol
            FROM usuarios
            WHERE id = ?
        """, (usuario_actual_id,))
        usuario_actual = cur.fetchone()
        if usuario_actual is None or usuario_actual[0] != "admin":
            raise ValueError(
                "La cuenta actual ya no tiene permisos de administrador."
            )

        cur.execute("""
            SELECT id
            FROM usuarios
            WHERE id = ?
        """, (nuevo_admin_id,))
        if cur.fetchone() is None:
            raise ValueError("La cuenta elegida como reemplazo ya no existe.")

        cur.execute("""
            UPDATE usuarios
            SET rol = 'admin'
            WHERE id = ?
        """, (nuevo_admin_id,))

        cur.execute("""
            DELETE FROM usuarios
            WHERE id = ?
        """, (usuario_actual_id,))
        if cur.rowcount != 1:
            raise ValueError(
                "No se pudo eliminar la cuenta administrativa actual."
            )

        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()