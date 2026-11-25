
USE grao_da_serra;

DELIMITER $$

-- Questao 1
CREATE FUNCTION fn_total_pedido(p_id_pedido INT)
RETURNS DECIMAL(10,2)
READS SQL DATA
BEGIN
    DECLARE total DECIMAL(10,2);

    SELECT COALESCE(SUM(quantidade * preco_unitario), 0)
    INTO total
    FROM item_pedido
    WHERE id_pedido = p_id_pedido;

    RETURN total;
END $$

-- Questao 2
CREATE FUNCTION fn_situacao_estoque(p_id_produto INT)
RETURNS VARCHAR(10)
READS SQL DATA
BEGIN
    DECLARE qtd INT;
    DECLARE minimo INT;

    SELECT estoque, estoque_minimo
    INTO qtd, minimo
    FROM produto
    WHERE id_produto = p_id_produto;

    IF qtd = 0 THEN
        RETURN 'ESGOTADO';
    ELSEIF qtd > 0 AND qtd <= minimo THEN
        RETURN 'REPOR';
    ELSE
        RETURN 'OK';
    END IF;
END $$

-- Questao 3
CREATE FUNCTION fn_desconto_fidelidade(p_id_cliente INT)
RETURNS DECIMAL(4,2)
READS SQL DATA
BEGIN
    DECLARE pedidos_pagos INT;

    SELECT COUNT(*)
    INTO pedidos_pagos
    FROM pedido
    WHERE id_cliente = p_id_cliente
    AND status = 'PAGO';

    IF pedidos_pagos >= 4 THEN
        RETURN 10;
    ELSEIF pedidos_pagos >= 2 THEN
        RETURN 5;
    ELSE
        RETURN 0;
    END IF;
END $$

DELIMITER ;

-- Testes da questao 1
SELECT fn_total_pedido(1),
       fn_total_pedido(3),
       fn_total_pedido(99);

-- Testes da questao 2
SELECT nome, estoque, estoque_minimo,
       fn_situacao_estoque(id_produto)
FROM produto;

-- Testes da questao 3
SELECT nome, fn_desconto_fidelidade(id_cliente)
FROM cliente;
