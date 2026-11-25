
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
