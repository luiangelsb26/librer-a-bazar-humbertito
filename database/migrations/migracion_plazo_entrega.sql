-- Ejecutar una sola vez en Supabase > SQL Editor para guardar el plazo
-- de entrega configurado para cada producto (0 a 30 días).
ALTER TABLE public.productos
    ADD COLUMN IF NOT EXISTS dias_entrega INTEGER NOT NULL DEFAULT 0
    CHECK (dias_entrega BETWEEN 0 AND 30);
