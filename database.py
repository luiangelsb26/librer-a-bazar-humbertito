import atexit
import logging
import os
import sqlite3
import threading
from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import Any

# Ubicación de la base de datos local
DB_PATH = Path(__file__).resolve().parent / "data" / "humbertito.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
_database_url: str | None = (
    os.environ.get("SUPABASE_DB_URL") or os.environ.get("DATABASE_URL")
)

# Si la conexión a Supabase falla, la app debe seguir funcionando con sqlite local.
_fallback_sqlite = False
_postgres_pool: Any | None = None
_POOL_LOCK = threading.Lock()
_LOGGER = logging.getLogger(__name__)


class _CursorPostgres:
    def __init__(self, cursor: Any) -> None:
        self._cursor = cursor

    def execute(
        self,
        consulta: str,
        parametros: Sequence[Any] = (),
    ) -> _CursorPostgres:
        self._cursor.execute(consulta.replace("?", "%s"), parametros)
        return self

    def executemany(
        self,
        consulta: str,
        parametros: Iterable[Sequence[Any]],
    ) -> _CursorPostgres:
        self._cursor.executemany(consulta.replace("?", "%s"), parametros)
        return self

    def fetchone(self) -> Any:
        return self._cursor.fetchone()

    def fetchmany(self, cantidad: int | None = None) -> list[Any]:
        if cantidad is None:
            return self._cursor.fetchmany()
        return self._cursor.fetchmany(cantidad)

    def fetchall(self) -> list[Any]:
        return self._cursor.fetchall()

    def close(self) -> None:
        self._cursor.close()

    @property
    def rowcount(self) -> int:
        return self._cursor.rowcount

    @property
    def description(self) -> Any:
        return self._cursor.description


class _ConexionPostgres:
    def __init__(self, conexion: Any, pool: Any | None = None) -> None:
        self._conexion = conexion
        self._pool = pool

    def cursor(self) -> _CursorPostgres:
        if self._conexion is None:
            raise RuntimeError("La conexión a la base de datos ya está cerrada.")
        return _CursorPostgres(self._conexion.cursor())

    def execute(
        self,
        consulta: str,
        parametros: Sequence[Any] = (),
    ) -> _CursorPostgres:
        return self.cursor().execute(consulta, parametros)

    def executemany(
        self,
        consulta: str,
        parametros: Iterable[Sequence[Any]],
    ) -> _CursorPostgres:
        return self.cursor().executemany(consulta, parametros)

    def commit(self) -> None:
        if self._conexion is None:
            raise RuntimeError("La conexión a la base de datos ya está cerrada.")
        self._conexion.commit()

    def rollback(self) -> None:
        if self._conexion is None:
            raise RuntimeError("La conexión a la base de datos ya está cerrada.")
        self._conexion.rollback()

    def close(self) -> None:
        conexion = self._conexion
        if conexion is None:
            return
        self._conexion = None
        if self._pool is None:
            conexion.close()
        else:
            self._pool.putconn(conexion)


DatabaseConnection = sqlite3.Connection | _ConexionPostgres


def _obtener_pool_postgres() -> Any:
    """Crea una piscina pequeña compartida para reutilizar conexiones TLS."""
    global _postgres_pool

    if _postgres_pool is None:
        with _POOL_LOCK:
            if _postgres_pool is None:
                from psycopg_pool import ConnectionPool

                if _database_url is None:
                    raise RuntimeError(
                        "No se configuró la URL de conexión de PostgreSQL."
                    )

                _postgres_pool = ConnectionPool(
                    conninfo=_database_url,
                    # Keep the app-side pool small. Supabase's transaction-mode
                    # pooler (port 6543) multiplexes these client connections.
                    min_size=1,
                    max_size=3,
                    timeout=20,
                    open=True,
                    kwargs={
                        "connect_timeout": 8,
                        "sslmode": "require",
                        # Supabase transaction mode does not support prepared statements.
                        "prepare_threshold": None,
                    },
                )
                atexit.register(_postgres_pool.close)
    return _postgres_pool


def configurar_desde_streamlit() -> None:
    """Lee la URL de Supabase desde los secrets de Streamlit, si existe."""
    global _database_url

    if _database_url:
        return

    import streamlit as st
    from streamlit.errors import StreamlitSecretNotFoundError

    try:
        _database_url = (
            st.secrets.get("SUPABASE_DB_URL")
            or st.secrets.get("DATABASE_URL")
        )
    except StreamlitSecretNotFoundError:
        return


def usar_supabase() -> bool:
    return bool(_database_url) and not _fallback_sqlite


def es_error_integridad(error: BaseException) -> bool:
    if isinstance(error, sqlite3.IntegrityError):
        return True

    try:
        from psycopg import IntegrityError
    except ModuleNotFoundError:
        return False

    return isinstance(error, IntegrityError)


def conectar() -> DatabaseConnection:
    """Conecta a Supabase si está configurado; si falla, usa SQLite local."""
    global _database_url, _fallback_sqlite

    if _database_url and not _fallback_sqlite:
        try:
            import psycopg
        except ModuleNotFoundError:
            _fallback_sqlite = True
            return sqlite3.connect(DB_PATH)

        try:
            from psycopg_pool import PoolTimeout
        except ModuleNotFoundError:
            # Conserva compatibilidad si el pool todavía no está instalado.
            try:
                return _ConexionPostgres(
                    psycopg.connect(
                        _database_url,
                        connect_timeout=8,
                        sslmode="require",
                    )
                )
            except Exception:
                _fallback_sqlite = True
                _database_url = None
                return sqlite3.connect(DB_PATH)

        pool = None
        try:
            pool = _obtener_pool_postgres()
            conexion = pool.getconn(timeout=20)
            return _ConexionPostgres(conexion, pool)
        except PoolTimeout:
            # Log only pool statistics; never include the DSN or credentials.
            if pool is not None:
                try:
                    _LOGGER.error("Supabase connection pool timed out: %s", pool.get_stats())
                except Exception:
                    _LOGGER.error("Supabase connection pool timed out; stats unavailable")
            raise
        except Exception:
            pass

        if pool is not None:
            try:
                pool.close()
            except Exception:
                pass
        _fallback_sqlite = True
        _database_url = None
        return sqlite3.connect(DB_PATH)

    return sqlite3.connect(DB_PATH)


def crear_base_datos() -> None:
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
            stock_minimo INTEGER NOT NULL DEFAULT 5,
            dias_entrega INTEGER NOT NULL DEFAULT 0
                CHECK (dias_entrega BETWEEN 0 AND 30)
        )
    """)

    if not usar_supabase():
        columnas_productos = cursor.execute(
            "PRAGMA table_info(productos)"
        ).fetchall()
        if not any(columna[1] == "dias_entrega" for columna in columnas_productos):
            cursor.execute(
                "ALTER TABLE productos ADD COLUMN dias_entrega "
                "INTEGER NOT NULL DEFAULT 0 "
                "CHECK (dias_entrega BETWEEN 0 AND 30)"
            )

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

    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_detalle_ventas_venta_id "
        "ON detalle_ventas(venta_id)"
    )
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_detalle_ventas_producto_id "
        "ON detalle_ventas(producto_id)"
    )
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_detalle_compras_compra_id "
        "ON detalle_compras(compra_id)"
    )
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_detalle_compras_producto_id "
        "ON detalle_compras(producto_id)"
    )

    conexion.commit()
    conexion.close()


def reiniciar_datos() -> dict[str, int]:
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
        registros_eliminados: dict[str, int] = {}

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
