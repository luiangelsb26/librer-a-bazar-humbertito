-- Ejecutar una sola vez en Supabase > SQL Editor para habilitar
-- la protección contra volver a importar el mismo Excel de compras y la auditoría
-- de si cada importación modificó el stock.
ALTER TABLE public.compras
    ADD COLUMN IF NOT EXISTS referencia TEXT;

CREATE TABLE IF NOT EXISTS public.importaciones_compras (
    hash_archivo TEXT PRIMARY KEY,
    nombre_archivo TEXT NOT NULL,
    fecha_importacion TEXT NOT NULL,
    filas_importadas INTEGER NOT NULL,
    stock_actualizado BOOLEAN
);

-- Los registros anteriores quedan NULL porque el sistema no guardaba esta opción.
ALTER TABLE public.importaciones_compras
    ADD COLUMN IF NOT EXISTS stock_actualizado BOOLEAN;
