
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
