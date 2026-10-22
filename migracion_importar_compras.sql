-- Ejecutar una sola vez en Supabase > SQL Editor para habilitar
-- la protección contra volver a importar el mismo Excel de compras.
ALTER TABLE public.compras
    ADD COLUMN IF NOT EXISTS referencia TEXT;

CREATE TABLE IF NOT EXISTS public.importaciones_compras (
    hash_archivo TEXT PRIMARY KEY,
    nombre_archivo TEXT NOT NULL,
    fecha_importacion TEXT NOT NULL,
    filas_importadas INTEGER NOT NULL
);
