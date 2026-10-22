-- Ejecutar una sola vez en Supabase > SQL Editor para conservar el modelo
-- entrenado entre reinicios y despliegues de la aplicación.
CREATE TABLE IF NOT EXISTS public.modelo_demanda (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    artefacto BYTEA NOT NULL,
    actualizado_en TEXT NOT NULL
);
