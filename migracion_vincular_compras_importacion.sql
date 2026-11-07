-- Ejecutar una sola vez en Supabase > SQL Editor para asociar las compras
-- importadas con su archivo y permitir borrar cada importación de forma segura.
ALTER TABLE public.compras
    ADD COLUMN IF NOT EXISTS hash_importacion TEXT;

CREATE INDEX IF NOT EXISTS idx_compras_hash_importacion
    ON public.compras (hash_importacion);

-- Las compras existentes quedan sin vínculo y no se borrarán al quitar
-- registros antiguos de auditoría.
