import hashlib
import hmac
import secrets
from datetime import datetime
import database


PASSWORD_HASH_ITERATIONS = 600_000
PASSWORD_HASH_PREFIX = "pbkdf2_sha256"


# ==========================================================
# CONFIGURACIÓN DE LA BASE DE DATOS
# ==========================================================

def conectar():
    return database.conectar()


# ==========================================================
# SEGURIDAD DE CONTRASEÑAS
# ==========================================================

def generar_hash(password):
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PASSWORD_HASH_ITERATIONS,
    )
    return (
        f"{PASSWORD_HASH_PREFIX}${PASSWORD_HASH_ITERATIONS}$"
        f"{salt.hex()}${digest.hex()}"
    )


def verificar_hash(password, hash_guardado):
    """Verifica hashes PBKDF2 nuevos y SHA-256 legado durante la transición."""
    if not isinstance(hash_guardado, str):
        return False, False

    partes = hash_guardado.split("$")
    if len(partes) == 4 and partes[0] == PASSWORD_HASH_PREFIX:
        try:
            iteraciones = int(partes[1])
            sal = bytes.fromhex(partes[2])
            digest_guardado = bytes.fromhex(partes[3])
        except (ValueError, TypeError):
            return False, False

        if not 100_000 <= iteraciones <= 1_000_000 or len(sal) < 16:
            return False, False

        digest_calculado = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            sal,
            iteraciones,
        )
        return hmac.compare_digest(digest_calculado, digest_guardado), False

    hash_legado = hashlib.sha256(password.encode("utf-8")).hexdigest()
    valido = hmac.compare_digest(hash_legado, hash_guardado)
    return valido, valido


# ==========================================================
# INICIALIZAR TABLA DE USUARIOS
# ==========================================================

def inicializar():
    """Crea la tabla de usuarios y devuelve su cantidad con una conexión."""
    con = conectar()
    try:
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
        cur.execute("SELECT COUNT(*) FROM usuarios")
        return cur.fetchone()[0]
    finally:
        con.close()
# ==========================================================
# CANTIDAD DE USUARIOS
# ==========================================================

def cantidad_usuarios():
    con = conectar()
    try:
        cur = con.cursor()
        cur.execute("SELECT COUNT(*) FROM usuarios")
        return cur.fetchone()[0]
    finally:
        con.close()
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
        raise ValueError("El nombre de usuario es obligatorio.")
    if not nombre:
        raise ValueError("El nombre completo es obligatorio.")
    if not password:
        raise ValueError("La contraseña es obligatoria.")
    if rol not in ("admin", "empleado"):
        raise ValueError("El rol seleccionado no es válido.")

    # El cálculo PBKDF2 ocurre antes de reservar la conexión del pool.
    password_hash = generar_hash(password)
    fecha_creacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    con = conectar()
    try:
        cur = con.cursor()
        cur.execute("SELECT id FROM usuarios WHERE username = ?", (username,))
        if cur.fetchone():
            raise ValueError("El nombre de usuario ya existe.")
        cur.execute("""
            INSERT INTO usuarios (username, nombre, password, rol, activo, creado)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (username, nombre, password_hash, rol, 1, fecha_creacion))
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()

# ==========================================================
# VERIFICAR USUARIO
# ==========================================================

def verificar_usuario(
    username,
    password
):
    username = username.strip()
    con = conectar()
    try:
        cur = con.cursor()
        cur.execute("""
            SELECT id, username, nombre, rol, activo, password
            FROM usuarios
            WHERE username = ? AND activo = 1
        """, (username,))
        fila = cur.fetchone()
    finally:
        con.close()

    if fila is None:
        return None

    # No mantener una conexión ocupada durante el cálculo costoso de PBKDF2.
    valido, actualizar_hash = verificar_hash(password, fila[5])
    if not valido:
        return None

    if actualizar_hash:
        nuevo_hash = generar_hash(password)
        con_actualizacion = conectar()
        try:
            cur_actualizacion = con_actualizacion.cursor()
            cur_actualizacion.execute(
                "UPDATE usuarios SET password = ? WHERE id = ? AND password = ?",
                (nuevo_hash, fila[0], fila[5]),
            )
            con_actualizacion.commit()
        except Exception:
            con_actualizacion.rollback()
        finally:
            con_actualizacion.close()

    return {
        "id": fila[0],
        "username": fila[1],
        "nombre": fila[2],
        "rol": fila[3],
        "activo": fila[4],
    }

# ==========================================================
# LISTAR USUARIOS
# ==========================================================

def listar_usuarios():
    con = conectar()
    try:
        cur = con.cursor()
        cur.execute("""
            SELECT id, username, nombre, rol, activo, creado
            FROM usuarios
            ORDER BY id
        """)
        return cur.fetchall()
    finally:
        con.close()
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
            SELECT rol, activo
            FROM usuarios
            WHERE id = ?
        """, (usuario_id,))
        usuario = cur.fetchone()

        if usuario is None:
            raise ValueError("La cuenta seleccionada ya no existe.")

        if usuario[0] == "admin" and usuario[1]:
            cur.execute("""
                SELECT COUNT(*)
                FROM usuarios
                WHERE rol = 'admin' AND activo = 1
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
            SELECT id, activo
            FROM usuarios
            WHERE id = ?
        """, (nuevo_admin_id,))
        nuevo_admin = cur.fetchone()
        if nuevo_admin is None:
            raise ValueError("La cuenta elegida como reemplazo ya no existe.")
        if not nuevo_admin[1]:
            raise ValueError(
                "Activa la cuenta elegida antes de transferirle la administración."
            )

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
