
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

USE grao_da_serra;

DELIMITER $$

-- Questao 4
CREATE PROCEDURE sp_abrir_pedido(
    IN p_id_cliente INT,
    IN p_id_funcionario INT,
    OUT p_id_pedido INT
)
BEGIN
    INSERT INTO pedido (id_cliente, id_funcionario)
    VALUES (p_id_cliente, p_id_funcionario);

    SET p_id_pedido = LAST_INSERT_ID();
END $$

-- Questao 5
CREATE PROCEDURE sp_adicionar_item(
    IN p_id_pedido INT,
    IN p_id_produto INT,
    IN p_quantidade INT
)
BEGIN
    DECLARE situacao VARCHAR(10);
    DECLARE produto_ativo BOOLEAN;
    DECLARE qtd_estoque INT;
    DECLARE valor DECIMAL(8,2);

    IF NOT EXISTS (
        SELECT 1 FROM pedido
        WHERE id_pedido = p_id_pedido
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Pedido inexistente';
    END IF;

    SELECT status INTO situacao
    FROM pedido
    WHERE id_pedido = p_id_pedido;

    IF situacao <> 'ABERTO' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Pedido nao esta aberto';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM produto
        WHERE id_produto = p_id_produto
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Produto inexistente';
    END IF;

    SELECT ativo, estoque, preco
    INTO produto_ativo, qtd_estoque, valor
    FROM produto
    WHERE id_produto = p_id_produto;

    IF produto_ativo = FALSE THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Produto inativo';
    END IF;

    IF p_quantidade IS NULL OR p_quantidade <= 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Quantidade invalida';
    END IF;

    IF qtd_estoque < p_quantidade THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Estoque insuficiente';
    END IF;

    INSERT INTO item_pedido (
        id_pedido, id_produto, quantidade, preco_unitario
    )
    VALUES (
        p_id_pedido, p_id_produto, p_quantidade, valor
    );
END $$

-- Questao 6
CREATE PROCEDURE sp_finalizar_pedido(
    IN p_id_pedido INT
)
BEGIN
    DECLARE situacao VARCHAR(10);
    DECLARE cliente_pedido INT;
    DECLARE total DECIMAL(10,2);
    DECLARE desconto DECIMAL(4,2);

    IF NOT EXISTS (
        SELECT 1 FROM pedido
        WHERE id_pedido = p_id_pedido
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Pedido inexistente';
    END IF;

    SELECT status, id_cliente
    INTO situacao, cliente_pedido
    FROM pedido
    WHERE id_pedido = p_id_pedido;

    IF situacao <> 'ABERTO' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Pedido nao esta aberto';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM item_pedido
        WHERE id_pedido = p_id_pedido
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Pedido sem itens';
    END IF;

    SET total = fn_total_pedido(p_id_pedido);
    SET desconto = fn_desconto_fidelidade(cliente_pedido);

    UPDATE pedido
    SET desconto_percentual = desconto,
        valor_total = ROUND(total * (1 - desconto / 100), 2),
        status = 'PAGO'
    WHERE id_pedido = p_id_pedido;
END $$

-- Questao 7
CREATE PROCEDURE sp_reajustar_precos_categoria(
    IN p_id_categoria INT,
    IN p_percentual DECIMAL(5,2)
)
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM categoria
        WHERE id_categoria = p_id_categoria
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Categoria inexistente';
    END IF;

    IF p_percentual IS NULL OR p_percentual <= -100 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Percentual invalido';
    END IF;

    UPDATE produto
    SET preco = ROUND(preco * (1 + p_percentual / 100), 2)
    WHERE id_categoria = p_id_categoria;
END $$

DELIMITER ;

USE grao_da_serra;

-- Questao 8
CREATE VIEW vw_cardapio AS
SELECT
    p.id_produto,
    c.nome AS categoria,
    p.nome AS produto,
    p.preco,
    fn_situacao_estoque(p.id_produto) AS situacao
FROM produto p
JOIN categoria c
    ON p.id_categoria = c.id_categoria
WHERE p.ativo = TRUE;


-- Questao 9
CREATE VIEW vw_pedidos_detalhados AS
SELECT
    p.id_pedido,
    p.data_pedido,
    p.status,
    c.nome AS cliente,
    f.nome AS atendente,
    (
        SELECT COUNT(*)
        FROM item_pedido i
        WHERE i.id_pedido = p.id_pedido
    ) AS qtd_itens,
    fn_total_pedido(p.id_pedido) AS valor_bruto,
    p.desconto_percentual,
    p.valor_total
FROM pedido p
JOIN cliente c
    ON p.id_cliente = c.id_cliente
JOIN funcionario f
    ON p.id_funcionario = f.id_funcionario;


-- Questao 10
CREATE VIEW vw_produtos_para_repor AS
SELECT
    p.id_produto,
    p.nome AS produto,
    c.nome AS categoria,
    p.estoque,
    p.estoque_minimo,
    (p.estoque_minimo - p.estoque) AS faltam
FROM produto p
JOIN categoria c
    ON p.id_categoria = c.id_categoria
WHERE p.ativo = TRUE
AND p.estoque <= p.estoque_minimo;


-- Questao 11
CREATE VIEW vw_vendas_por_categoria AS
SELECT
    c.nome AS categoria,
    COALESCE(SUM(
        CASE WHEN pe.status = 'PAGO'
        THEN i.quantidade ELSE 0 END
    ), 0) AS unidades,
    COALESCE(SUM(
        CASE WHEN pe.status = 'PAGO'
        THEN i.quantidade * i.preco_unitario
        ELSE 0 END
    ), 0) AS faturamento
FROM categoria c
LEFT JOIN produto p
    ON c.id_categoria = p.id_categoria
LEFT JOIN item_pedido i
    ON p.id_produto = i.id_produto
LEFT JOIN pedido pe
    ON i.id_pedido = pe.id_pedido
GROUP BY c.id_categoria, c.nome;

USE grao_da_serra;

DELIMITER $$

-- Questao 12
CREATE TRIGGER trg_item_baixa_estoque
AFTER INSERT ON item_pedido
FOR EACH ROW
BEGIN
    UPDATE produto
    SET estoque = estoque - NEW.quantidade
    WHERE id_produto = NEW.id_produto;
END $$

-- Questao 13
CREATE TRIGGER trg_item_devolve_estoque
AFTER DELETE ON item_pedido
FOR EACH ROW
BEGIN
    UPDATE produto
    SET estoque = estoque + OLD.quantidade
    WHERE id_produto = OLD.id_produto;
END $$

-- Questao 14
CREATE TRIGGER trg_produto_historico_preco
AFTER UPDATE ON produto
FOR EACH ROW
BEGIN
    IF OLD.preco <> NEW.preco THEN
        INSERT INTO historico_preco (
            id_produto,
            preco_antigo,
            preco_novo,
            usuario
        )
        VALUES (
            NEW.id_produto,
            OLD.preco,
            NEW.preco,
            CURRENT_USER()
        );
    END IF;
END $$

-- Questao 15
CREATE TRIGGER trg_pedido_bloqueia_alteracao
BEFORE UPDATE ON pedido
FOR EACH ROW
BEGIN
    IF OLD.status IN ('PAGO', 'CANCELADO') THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Pedido encerrado nao pode ser alterado';
    END IF;
END $$

DELIMITER ;
