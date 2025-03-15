-- Listar todos los usuarios activos
SELECT id, username, phone, created_at
FROM CLIENTE
WHERE active = 1
ORDER BY created_at DESC;

--  Consultar los emails confirmados de cada usuario
SELECT c.username, ec.email
FROM CLIENTE c
JOIN EMAILCLIENTE ec ON ec.client_id = c.id
WHERE ec.confirmed = 1;

-- Obtener las direcciones de envío de un usuario específico
SELECT c.username, d.address
FROM CLIENTE c
JOIN DIRECCION d ON d.client_id = c.id
WHERE c.username = 'user4';

-- Mostrar el inventario por sede y producto
SELECT s.name AS sede, p.name AS producto, i.quantity AS stock
FROM INVENTARIO i
JOIN PRODUCTO p ON p.id = i.product_id
JOIN SEDE s ON s.id = i.location_id
ORDER BY s.name, p.name;

-- Productos sin stock (agotados en todas las sedes)
SELECT p.id, p.name
FROM PRODUCTO p
LEFT JOIN INVENTARIO i ON p.id = i.product_id
GROUP BY p.id, p.name
HAVING SUM(NVL(i.quantity, 0)) = 0;

-- Listar todas las órdenes y su cliente asociado
SELECT o.id AS order_id, c.username, o.created_at
FROM ORDENCOMPRA o
JOIN CLIENTE c ON c.id = o.client_id
ORDER BY o.created_at DESC;

-- Detalle de una orden (productos, cantidades, precios)
SELECT do.order_id, p.name AS producto, do.quantity, do.unit_price
FROM DETALLEORDEN do
JOIN PRODUCTO p ON p.id = do.product_id
WHERE do.order_id = 1;

-- Total gastado por cada cliente
SELECT c.username, SUM(do.quantity * do.unit_price) AS total_gastado
FROM CLIENTE c
JOIN ORDENCOMPRA o ON o.client_id = c.id
JOIN DETALLEORDEN do ON do.order_id = o.id
GROUP BY c.username
ORDER BY total_gastado DESC;

-- Listar todos los pagos realizados
SELECT p.id AS pago_id, o.id AS orden_id, ep.name AS estado_pago,
       p.total_amount, p.created_at
FROM PAGO p
JOIN ORDENCOMPRA o ON o.id = p.order_id
JOIN ESTADOPAGO ep ON ep.id = p.estado_pago_id
ORDER BY p.created_at DESC;

-- Total de pagos por método de pago
SELECT mp.name AS metodo_pago, SUM(p.total_amount) AS total_pagado
FROM PAGO p
JOIN METODOPAGO mp ON mp.id = p.metodo_pago_id
GROUP BY mp.name;


-- Listar todos los envíos pendientes de entrega
SELECT e.id AS envio_id, o.id AS orden_id, et.name AS empresa_transporte, es.name AS estado_envio
FROM ENVIO e
JOIN EMPRESATRANSPORTE et ON et.id = e.company_id
JOIN ESTADOENVIO es ON es.id = e.shipping_status_id
WHERE e.delivered_at IS NULL;

-- Ver los detalles de un envío específico
SELECT e.id AS envio_id, o.id AS orden_id, et.name AS empresa_transporte, e.address, e.dispatch_date, es.name AS estado_envio
FROM ENVIO e
JOIN ORDENCOMPRA o ON o.id = e.order_id
JOIN EMPRESATRANSPORTE et ON et.id = e.company_id
JOIN ESTADOENVIO es ON es.id = e.shipping_status_id
WHERE e.id = 1;


-- Productos más vendidos (TOP 5)
SELECT p.name, SUM(do.quantity) AS total_vendido
FROM DETALLEORDEN do
JOIN PRODUCTO p ON p.id = do.product_id
GROUP BY p.name
ORDER BY total_vendido DESC
FETCH FIRST 5 ROWS ONLY;

-- Sedes con más movimiento de inventario (envíos + ventas)
SELECT s.name AS sede,
       NVL(SUM(i.quantity), 0) AS stock_actual
FROM SEDE s
LEFT JOIN INVENTARIO i ON i.location_id = s.id
GROUP BY s.name
ORDER BY stock_actual DESC;

-- Auditoría rápida de usuarios registrados por día
SELECT TO_CHAR(created_at, 'YYYY-MM-DD') AS fecha_registro,
       COUNT(*) AS usuarios_registrados
FROM CLIENTE
GROUP BY TO_CHAR(created_at, 'YYYY-MM-DD')
ORDER BY fecha_registro DESC;


-- 1.1 Top 10 clientes con mayor número de órdenes realizadas
SELECT
    c.id AS cliente_id,
    c.username,
    COUNT(o.id) AS total_ordenes,
    SUM(do.quantity * do.unit_price) AS total_comprado
FROM CLIENTE c
JOIN ORDENCOMPRA o ON o.client_id = c.id
JOIN DETALLEORDEN do ON do.order_id = o.id
WHERE c.active = 1
GROUP BY c.id, c.username
ORDER BY total_comprado DESC
FETCH FIRST 10 ROWS ONLY;

-- 1.2 Clientes que nunca han realizado una orden
SELECT c.id, c.username
FROM CLIENTE c
LEFT JOIN ORDENCOMPRA o ON o.client_id = c.id
WHERE o.id IS NULL;

-- 1.3 Usuarios con métodos de pago configurados y sin órdenes
SELECT c.id, c.username, COUNT(mpc.id) AS metodos_pago
FROM CLIENTE c
LEFT JOIN METODOPAGOCLIENTE mpc ON mpc.client_id = c.id
LEFT JOIN ORDENCOMPRA o ON o.client_id = c.id
WHERE o.id IS NULL
GROUP BY c.id, c.username
HAVING COUNT(mpc.id) > 0;

-- 2.1 Productos más vendidos por categoría
SELECT
    cat.name AS categoria,
    p.name AS producto,
    SUM(do.quantity) AS unidades_vendidas,
    SUM(do.quantity * do.unit_price) AS total_vendido
FROM DETALLEORDEN do
JOIN PRODUCTO p ON p.id = do.product_id
JOIN CATEGORIA cat ON cat.id = p.category_id
GROUP BY cat.name, p.name
ORDER BY categoria, total_vendido DESC;

-- 2.2 Consulta de stock actual por producto y sede, con alerta de bajo stock (<5 unidades)
SELECT
    p.name AS producto,
    s.name AS sede,
    i.quantity AS stock_disponible,
    CASE
        WHEN i.quantity < 5 THEN 'BAJO STOCK'
        ELSE 'OK'
    END AS estado_stock
FROM INVENTARIO i
JOIN PRODUCTO p ON p.id = i.product_id
JOIN SEDE s ON s.id = i.location_id
ORDER BY estado_stock, sede;

-- 2.3 Productos sin inventario en ninguna sede
SELECT p.id, p.name
FROM PRODUCTO p
LEFT JOIN INVENTARIO i ON p.id = i.product_id
GROUP BY p.id, p.name
HAVING SUM(NVL(i.quantity, 0)) = 0;


-- 3.1 Reporte de órdenes con detalle de envío y estado
SELECT
    o.id AS orden_id,
    c.username AS cliente,
    e.address AS direccion_envio,
    et.name AS empresa_transporte,
    es.name AS estado_envio,
    e.dispatch_date,
    e.delivered_at,
    SUM(do.quantity * do.unit_price) AS total_orden
FROM ORDENCOMPRA o
JOIN CLIENTE c ON c.id = o.client_id
LEFT JOIN ENVIO e ON e.order_id = o.id
LEFT JOIN EMPRESATRANSPORTE et ON et.id = e.company_id
LEFT JOIN ESTADOENVIO es ON es.id = e.shipping_status_id
JOIN DETALLEORDEN do ON do.order_id = o.id
GROUP BY o.id, c.username, e.address, et.name, es.name, e.dispatch_date, e.delivered_at
ORDER BY o.id DESC;

-- 3.2 Órdenes que nunca han sido enviadas (sin registro en ENVIO)
SELECT
    o.id AS orden_id,
    c.username AS cliente,
    o.created_at AS fecha_creacion
FROM ORDENCOMPRA o
JOIN CLIENTE c ON c.id = o.client_id
LEFT JOIN ENVIO e ON e.order_id = o.id
WHERE e.id IS NULL
ORDER BY o.created_at DESC;

-- 4.1 Reporte completo de pagos, método y estado
SELECT
    p.id AS pago_id,
    o.id AS orden_id,
    c.username AS cliente,
    mp.name AS metodo_pago,
    ep.name AS estado_pago,
    p.total_amount AS monto_pagado,
    p.created_at AS fecha_pago
FROM PAGO p
JOIN ORDENCOMPRA o ON o.id = p.order_id
JOIN CLIENTE c ON c.id = o.client_id
JOIN METODOPAGO mp ON mp.id = p.metodo_pago_id
JOIN ESTADOPAGO ep ON ep.id = p.estado_pago_id
ORDER BY p.created_at DESC;

-- 4.2 Total de pagos agrupados por estado
SELECT
    ep.name AS estado_pago,
    COUNT(p.id) AS cantidad_pagos,
    SUM(p.total_amount) AS monto_total
FROM PAGO p
JOIN ESTADOPAGO ep ON ep.id = p.estado_pago_id
GROUP BY ep.name
ORDER BY monto_total DESC;

-- 4.3 Clientes con pagos rechazados
SELECT DISTINCT
    c.id AS cliente_id,
    c.username,
    COUNT(p.id) AS pagos_rechazados
FROM PAGO p
JOIN ORDENCOMPRA o ON o.id = p.order_id
JOIN CLIENTE c ON c.id = o.client_id
JOIN ESTADOPAGO ep ON ep.id = p.estado_pago_id
WHERE ep.name = 'REJECT'
GROUP BY c.id, c.username;


-- 5.1 Clientes registrados por mes
SELECT
    TO_CHAR(created_at, 'YYYY-MM') AS mes_registro,
    COUNT(*) AS clientes_nuevos
FROM CLIENTE
GROUP BY TO_CHAR(created_at, 'YYYY-MM')
ORDER BY mes_registro DESC;

-- 5.2 Órdenes creadas por día y su total en dinero
SELECT
    TO_CHAR(created_at, 'YYYY-MM-DD') AS dia,
    COUNT(*) AS total_ordenes,
    SUM(
        (SELECT SUM(do.quantity * do.unit_price)
         FROM DETALLEORDEN do
         WHERE do.order_id = o.id)
    ) AS total_facturado
FROM ORDENCOMPRA o
GROUP BY TO_CHAR(created_at, 'YYYY-MM-DD')
ORDER BY dia DESC;

-- 5.3 Promedio de gasto por cliente
SELECT
    c.username,
    AVG(oc_total.total) AS promedio_gasto
FROM CLIENTE c
JOIN (
    SELECT o.client_id, SUM(do.quantity * do.unit_price) AS total
    FROM ORDENCOMPRA o
    JOIN DETALLEORDEN do ON do.order_id = o.id
    GROUP BY o.client_id
) oc_total ON oc_total.client_id = c.id
GROUP BY c.username
ORDER BY promedio_gasto DESC;


-- 6.1 Listado rápido de órdenes para el endpoint /api/orders (resumido)
SELECT
    o.id AS order_id,
    o.client_id AS user_id,
    NVL((
        SELECT SUM(do.quantity * do.unit_price)
        FROM DETALLEORDEN do
        WHERE do.order_id = o.id
    ), 0) AS total_amount,
    o.created_at
FROM ORDENCOMPRA o
ORDER BY o.created_at DESC;

-- 6.2 Detalle de una orden para el endpoint /api/orders/:id
SELECT
    do.order_id,
    do.product_id,
    p.name AS producto,
    do.quantity,
    do.unit_price
FROM DETALLEORDEN do
JOIN PRODUCTO p ON p.id = do.product_id
WHERE do.order_id = 1;