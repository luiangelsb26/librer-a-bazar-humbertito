-- Ejecutar una sola vez en Supabase > SQL Editor para acelerar las consultas
-- de ventas, compras y análisis que buscan detalles por operación o producto.
CREATE INDEX IF NOT EXISTS idx_detalle_ventas_venta_id
    ON public.detalle_ventas (venta_id);

CREATE INDEX IF NOT EXISTS idx_detalle_ventas_producto_id
    ON public.detalle_ventas (producto_id);

CREATE INDEX IF NOT EXISTS idx_detalle_compras_compra_id
    ON public.detalle_compras (compra_id);

CREATE INDEX IF NOT EXISTS idx_detalle_compras_producto_id
    ON public.detalle_compras (producto_id);
