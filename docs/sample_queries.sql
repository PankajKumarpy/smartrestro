-- Smart Restaurant Management System (Smart RMS)
-- Sample SQL queries for academic evaluation (PostgreSQL-friendly)

-- 1) Today's paid sales total
SELECT COALESCE(SUM(total), 0) AS total_sales
FROM billing_invoice
WHERE status = 'PAID' AND DATE(paid_at) = CURRENT_DATE;

-- 2) Payment mode breakdown for a date
SELECT payment_mode, COUNT(*) AS invoices, COALESCE(SUM(total), 0) AS amount
FROM billing_invoice
WHERE status = 'PAID' AND DATE(paid_at) = DATE '2026-03-03'
GROUP BY payment_mode
ORDER BY payment_mode;

-- 3) Most sold menu item (by quantity) for a date
SELECT mi.name, SUM(oi.quantity) AS qty
FROM orders_orderitem oi
JOIN orders_order o ON o.id = oi.order_id
JOIN billing_invoice inv ON inv.order_id = o.id
JOIN menu_menuitem mi ON mi.id = oi.menu_item_id
WHERE inv.status = 'PAID' AND DATE(inv.paid_at) = DATE '2026-03-03'
GROUP BY mi.name
ORDER BY qty DESC
LIMIT 10;

-- 4) Low stock raw materials
SELECT name, unit, quantity_in_stock, min_stock_level
FROM inventory_rawmaterial
WHERE is_active = TRUE AND quantity_in_stock <= min_stock_level
ORDER BY name;

-- 5) Stock movement history for a material
SELECT sm.created_at, sm.movement_type, sm.quantity, sm.note, u.username AS done_by
FROM inventory_stockmovement sm
JOIN users_user u ON u.id = sm.created_by_id
WHERE sm.material_id = 1
ORDER BY sm.created_at DESC;

