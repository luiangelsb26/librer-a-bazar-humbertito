import sqlite3
import hashlib
from pathlib import Path
from datetime import datetime


DB_PATH = Path(__file__).resolve().parent / "data" / "humbertito.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def conectar():
    return sqlite3.connect(DB_PATH)


def generar_hash(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def inicializar():
    con = conectar()
    cur = con.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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


def cantidad_usuarios():
    con = conectar()
    cur = con.cursor()

    cur.execute("SELECT COUNT(*) FROM usuarios")

    cantidad = cur.fetchone()[0]

    con.close()

    return cantidad


def crear_usuario(username, nombre, password, rol="empleado"):
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

    con = conectar()
    cur = con.cursor()

    cur.execute(
        "SELECT id FROM usuarios WHERE username = ?",
        (username,)
    )

    if cur.fetchone():
        con.close()
        raise ValueError("El nombre de usuario ya existe.")

    password_hash = generar_hash(password)

    cur.execute("""
        INSERT INTO usuarios (
            username,
            nombre,
            password,
            rol,
            activo,
            creado
        )
        VALUES (?, ?, ?, ?, 1, ?)
    """, (
        username,
        nombre,
        password_hash,
        rol,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    con.commit()
    con.close()


def verificar_usuario(username, password):
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

    usuario = cur.fetchone()

    con.close()

    return usuario


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