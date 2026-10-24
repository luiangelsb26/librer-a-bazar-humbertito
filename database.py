import atexit
import os
import sqlite3
import threading
from pathlib import Path

# Ubicación de la base de datos local
DB_PATH = Path(__file__).resolve().parent / "data" / "humbertito.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
_DATABASE_URL = os.environ.get("SUPABASE_DB_URL") or os.environ.get("DATABASE_URL")

# Si la conexión a Supabase falla, la app debe seguir funcionando con sqlite local.
_FALLBACK_SQLITE = False
_POSTGRES_POOL = None
_POOL_LOCK = threading.Lock()


class _CursorPostgres:
    def __init__(self, cursor):
        self._cursor = cursor

    def execute(self, consulta, parametros=()):
        self._cursor.execute(consulta.replace("?", "%s"), parametros)
        return self

    def executemany(self, consulta, parametros):
        self._cursor.executemany(consulta.replace("?", "%s"), parametros)
        return self

    def fetchone(self):
        return self._cursor.fetchone()

    def fetchmany(self, cantidad=None):
        if cantidad is None:
            return self._cursor.fetchmany()
        return self._cursor.fetchmany(cantidad)

    def fetchall(self):
        return self._cursor.fetchall()

    def close(self):
        self._cursor.close()

    @property
    def rowcount(self):
        return self._cursor.rowcount

    @property
    def description(self):
        return self._cursor.description


class _ConexionPostgres:
    def __init__(self, conexion, pool=None):
        self._conexion = conexion
        self._pool = pool

    def cursor(self):
        return _CursorPostgres(self._conexion.cursor())

    def execute(self, consulta, parametros=()):
        return self.cursor().execute(consulta, parametros)

    def executemany(self, consulta, parametros):
        return self.cursor().executemany(consulta, parametros)

    def commit(self):
        self._conexion.commit()

    def rollback(self):
        self._conexion.rollback()

    def close(self):
        conexion = self._conexion
        if conexion is None:
            return
        self._conexion = None
        if self._pool is None:
            conexion.close()
        else:
            self._pool.putconn(conexion)


def _obtener_pool_postgres():
    """Crea una piscina pequeña compartida para reutilizar conexiones TLS."""
    global _POSTGRES_POOL

    if _POSTGRES_POOL is None:
        with _POOL_LOCK:
            if _POSTGRES_POOL is None:
                from psycopg_pool import ConnectionPool

                _POSTGRES_POOL = ConnectionPool(
                    conninfo=_DATABASE_URL,
                    min_size=1,
                    max_size=5,
                    timeout=10,
                    open=True,
                    kwargs={
                        "connect_timeout": 8,
                        "sslmode": "require",
                    },
                )
                atexit.register(_POSTGRES_POOL.close)
    return _POSTGRES_POOL


def configurar_desde_streamlit():
    """Lee la URL de Supabase desde los secrets de Streamlit, si existe."""
    global _DATABASE_URL

    if _DATABASE_URL:
        return

    import streamlit as st
    from streamlit.errors import StreamlitSecretNotFoundError

    try:
        _DATABASE_URL = (
            st.secrets.get("SUPABASE_DB_URL")
            or st.secrets.get("DATABASE_URL")
        )
    except StreamlitSecretNotFoundError:
        return


def usar_supabase():
    return bool(_DATABASE_URL) and not _FALLBACK_SQLITE


def es_error_integridad(error):
    if isinstance(error, sqlite3.IntegrityError):
        return True

    try:
        from psycopg import IntegrityError
    except ModuleNotFoundError:
        return False

    return isinstance(error, IntegrityError)


def conectar():
    """Conecta a Supabase si está configurado; si falla, usa SQLite local."""
    global _DATABASE_URL, _FALLBACK_SQLITE

    if _DATABASE_URL and not _FALLBACK_SQLITE:
        try:
            import psycopg
        except ModuleNotFoundError:
            _FALLBACK_SQLITE = True
            return sqlite3.connect(DB_PATH)

        try:
            from psycopg_pool import PoolTimeout
        except ModuleNotFoundError:
            # Conserva compatibilidad si el pool todavía no está instalado.
            try:
                return _ConexionPostgres(
                    psycopg.connect(
                        _DATABASE_URL,
                        connect_timeout=8,
                        sslmode="require",
                    )
                )
            except Exception:
                _FALLBACK_SQLITE = True
                _DATABASE_URL = None
                return sqlite3.connect(DB_PATH)

        pool = None
        try:
            pool = _obtener_pool_postgres()
            conexion = pool.getconn(timeout=10)
            return _ConexionPostgres(conexion, pool)
        except PoolTimeout:
            # No cambiar de base si las conexiones existentes solo están ocupadas:
            # hacerlo separaría las escrituras entre Supabase y SQLite.
            if pool is not None and pool.get_stats().get("pool_size", 0) > 0:
                raise
        except Exception:
            pass

        if pool is not None:
            try:
                pool.close()
            except Exception:
                pass
        _FALLBACK_SQLITE = True
        _DATABASE_URL = None
        return sqlite3.connect(DB_PATH)

    return sqlite3.connect(DB_PATH)


def crear_base_datos():
    """Crea las tablas principales en SQLite o PostgreSQL."""
    conexion = conectar()

    # El esquema de Supabase se administra con migraciones explícitas desde el
    # Dashboard. Ejecutar DDL en cada rerun de Streamlit puede esperar bloqueos
    # de tabla y cancelar el arranque de la aplicación.
    if usar_supabase():
        conexion.close()
        return

    cursor = conexion.cursor()
    id_type = (
        "SERIAL PRIMARY KEY"
        if usar_supabase()
        else "INTEGER PRIMARY KEY AUTOINCREMENT"
    )
    real_type = "DOUBLE PRECISION" if usar_supabase() else "REAL"

    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS productos (
            id {id_type},
            codigo TEXT UNIQUE NOT NULL,
            nombre TEXT NOT NULL,
            categoria TEXT,
            precio_compra {real_type} NOT NULL,
            precio_venta {real_type} NOT NULL,
            stock INTEGER NOT NULL DEFAULT 0,
            stock_minimo INTEGER NOT NULL DEFAULT 5
        )
    """)

    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS ventas (
            id {id_type},
            fecha TEXT NOT NULL,
            total {real_type} NOT NULL,
            stock_descontado INTEGER,
            referencia TEXT
        )
    """)

    # Registra si una venta afectó el stock para poder restaurarlo al borrar.
    # En Supabase el esquema se actualiza mediante migración SQL, no en cada
    # arranque de Streamlit, porque ALTER TABLE puede bloquearse si hay consultas
    # concurrentes. Las ventas antiguas quedan en NULL.
    if not usar_supabase():
        columnas_ventas = cursor.execute("PRAGMA table_info(ventas)").fetchall()
        if not any(columna[1] == "stock_descontado" for columna in columnas_ventas):
            cursor.execute(
                "ALTER TABLE ventas ADD COLUMN stock_descontado INTEGER"
            )
        if not any(columna[1] == "referencia" for columna in columnas_ventas):
            cursor.execute("ALTER TABLE ventas ADD COLUMN referencia TEXT")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS importaciones_ventas (
            hash_archivo TEXT PRIMARY KEY,
            nombre_archivo TEXT NOT NULL,
            fecha_importacion TEXT NOT NULL,
            filas_importadas INTEGER NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS importaciones_compras (
            hash_archivo TEXT PRIMARY KEY,
            nombre_archivo TEXT NOT NULL,
            fecha_importacion TEXT NOT NULL,
            filas_importadas INTEGER NOT NULL,
            stock_actualizado INTEGER
        )
    """)

    if not usar_supabase():
        columnas_importaciones = cursor.execute(
            "PRAGMA table_info(importaciones_compras)"
        ).fetchall()
        if not any(columna[1] == "stock_actualizado" for columna in columnas_importaciones):
            cursor.execute(
                "ALTER TABLE importaciones_compras ADD COLUMN stock_actualizado INTEGER"
            )

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS modelo_demanda (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            artefacto BLOB NOT NULL,
            actualizado_en TEXT NOT NULL
        )
    """)

    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS detalle_ventas (
            id {id_type},
            venta_id INTEGER NOT NULL,
            producto_id INTEGER NOT NULL,
            cantidad INTEGER NOT NULL,
            precio_unitario {real_type} NOT NULL,
            subtotal {real_type} NOT NULL,
            FOREIGN KEY (venta_id) REFERENCES ventas(id),
            FOREIGN KEY (producto_id) REFERENCES productos(id)
        )
    """)

    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS compras (
            id {id_type},
            fecha TEXT NOT NULL,
            total {real_type} NOT NULL,
            referencia TEXT
        )
    """)

    if not usar_supabase():
        columnas_compras = cursor.execute("PRAGMA table_info(compras)").fetchall()
        if not any(columna[1] == "referencia" for columna in columnas_compras):
            cursor.execute("ALTER TABLE compras ADD COLUMN referencia TEXT")

    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS detalle_compras (
            id {id_type},
            compra_id INTEGER NOT NULL,
            producto_id INTEGER NOT NULL,
            cantidad INTEGER NOT NULL,
            precio_unitario {real_type} NOT NULL,
            subtotal {real_type} NOT NULL,
            FOREIGN KEY (compra_id) REFERENCES compras(id),
            FOREIGN KEY (producto_id) REFERENCES productos(id)
        )
    """)

    conexion.commit()
    conexion.close()


def reiniciar_datos():
    """Elimina todos los registros y conserva las tablas del sistema."""
    conexion = conectar()

    try:
        cursor = conexion.cursor()
        tablas = (
            "detalle_ventas",
            "detalle_compras",
            "ventas",
            "importaciones_ventas",
            "importaciones_compras",
            "compras",
            "productos",
        )
        registros_eliminados = {}

        for tabla in tablas:
            registros_eliminados[tabla] = cursor.execute(
                f"SELECT COUNT(*) FROM {tabla}"
            ).fetchone()[0]

        if usar_supabase():
            lista_tablas = ", ".join(tablas)
            conexion.execute(
                f"TRUNCATE TABLE {lista_tablas} RESTART IDENTITY"
            )
        else:
            for tabla in tablas:
                cursor.execute(f"DELETE FROM {tabla}")

            for tabla in tablas:
                cursor.execute(
                    "DELETE FROM sqlite_sequence WHERE name = ?",
                    (tabla,)
                )

        conexion.commit()
        return registros_eliminados

    except Exception:
        conexion.rollback()
        raise

    finally:
        conexion.close()


if __name__ == "__main__":
    crear_base_datos()
    print("Base de datos creada correctamente.")
