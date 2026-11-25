
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
