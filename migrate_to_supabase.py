import sqlite3
from contextlib import closing

import auth
import database


TABLAS = (
    "productos",
    "ventas",
    "compras",
    "detalle_ventas",
    "detalle_compras",
    "usuarios",
)
BATCH_SIZE = 500


def migrar():
    database.configurar_desde_streamlit()

    if not database.usar_supabase():
        raise RuntimeError(
            "Configura SUPABASE_DB_URL en .streamlit/secrets.toml "
            "o como variable de entorno antes de migrar."
        )

    if not database.DB_PATH.is_file():
        raise FileNotFoundError(
            f"No se encontró la base local: {database.DB_PATH}"
        )

    database.crear_base_datos()
    auth.inicializar()

    conteos_origen = {}
    with closing(sqlite3.connect(
        database.DB_PATH.resolve().as_uri() + "?mode=ro",
        uri=True
    )) as origen:
        for tabla in TABLAS:
            conteos_origen[tabla] = origen.execute(
                f"SELECT COUNT(*) FROM {tabla}"
            ).fetchone()[0]

        destino = database.conectar()
        try:
            conteos_destino = {
                tabla: destino.execute(
                    f"SELECT COUNT(*) FROM {tabla}"
                ).fetchone()[0]
                for tabla in TABLAS
            }
            if any(conteos_destino.values()):
                raise RuntimeError(
                    "La base de Supabase ya contiene datos. "
                    "La migración se detuvo para evitar duplicados."
                )

            for tabla in TABLAS:
                lector = origen.execute(
                    f"SELECT * FROM {tabla} ORDER BY id"
                )
                columnas = [columna[0] for columna in lector.description]
                marcadores = ", ".join("?" for _ in columnas)
                lista_columnas = ", ".join(columnas)
                sentencia = (
                    f"INSERT INTO {tabla} ({lista_columnas}) "
                    f"VALUES ({marcadores})"
                )

                while lote := lector.fetchmany(BATCH_SIZE):
                    destino.executemany(sentencia, lote)

                destino.execute(
                    "SELECT setval(pg_get_serial_sequence(?, 'id'), "
                    f"COALESCE(MAX(id), 1), COUNT(*) > 0) FROM {tabla}",
                    (tabla,)
                )

            destino.commit()
        except Exception:
            destino.rollback()
            raise
        finally:
            destino.close()

    print("Migración completada. Registros transferidos:")
    for tabla, cantidad in conteos_origen.items():
        print(f"- {tabla}: {cantidad}")


if __name__ == "__main__":
    migrar()
