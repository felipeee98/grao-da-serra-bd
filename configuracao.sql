USE grao_da_serra;

CREATE USER IF NOT EXISTS 'cafeteria'@'localhost'
IDENTIFIED BY 'GraoSerra2026';

GRANT SELECT, EXECUTE
ON grao_da_serra.*
TO 'cafeteria'@'localhost';

GRANT DELETE
ON grao_da_serra.item_pedido
TO 'cafeteria'@'localhost';