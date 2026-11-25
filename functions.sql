USE grao_da_serra;

DELIMITER $$

CREATE FUNCTION fn_total_pedido(p_id_pedido INT)
RETURNS DECIMAL(10,2)
READS SQL DATA
BEGIN
    DECLARE total DECIMAL(10,2);

    SELECT COALESCE(SUM(quantidade * preco_unitario), 0)
    INTO total
    FROM __________
    WHERE id_pedido = __________;

    RETURN total;
END $$

DELIMITER ;
