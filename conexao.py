import mysql.connector
import os

def conectar():
    return mysql.connector.connect(host='localhost', port=3306, user='cafeteria', password=os.getenv('GRAO_DB_PASSWORD', 'GraoSerra2026'), database='grao_da_serra', autocommit=True)

class Dados:
    def __init__(self): self.banco = conectar()
    def consultar(self, sql, args=()):
        c = self.banco.cursor()
        try:
            c.execute(sql,args)
            return c.fetchall()
        finally: c.close()
    def chamar(self, nome, args):
        c=self.banco.cursor()
        try:
            r=c.callproc(nome,args)
            for resultado in c.stored_results(): resultado.fetchall()
            return r
        finally: c.close()
    def listarCardapio(self): return self.consultar('SELECT * FROM vw_cardapio ORDER BY categoria, produto')
    def listarClientes(self): return self.consultar('SELECT id_cliente,nome FROM cliente ORDER BY nome')
    def listarFuncionarios(self): return self.consultar('SELECT id_funcionario,nome FROM funcionario ORDER BY nome')
    def abrirPedido(self,c,f): return self.chamar('sp_abrir_pedido',(c,f,0))[2]
    def adicionarItem(self,p,i,q): self.chamar('sp_adicionar_item',(p,i,q))
    def removerItem(self,p,i):
        c=self.banco.cursor()
        try:
            c.execute("DELETE i FROM item_pedido i JOIN pedido p ON p.id_pedido=i.id_pedido WHERE i.id_pedido=%s AND i.id_produto=%s AND p.status='ABERTO'",(p,i))
            if not c.rowcount: raise ValueError('Item inexistente ou pedido encerrado.')
        finally: c.close()
    def finalizarPedido(self,p):
        self.chamar('sp_finalizar_pedido',(p,))
        return self.consultar('SELECT desconto_percentual,valor_total FROM pedido WHERE id_pedido=%s',(p,))[0]
    def listarPedidos(self,status='TODOS'):
        if status=='TODOS': return self.consultar('SELECT * FROM vw_pedidos_detalhados ORDER BY id_pedido DESC')
        return self.consultar('SELECT * FROM vw_pedidos_detalhados WHERE status=%s ORDER BY id_pedido DESC',(status,))
    def listarProdutosParaRepor(self): return self.consultar('SELECT * FROM vw_produtos_para_repor')
    def listarVendasPorCategoria(self): return self.consultar('SELECT * FROM vw_vendas_por_categoria')
    def reajustarPrecos(self,c,p):
        cur=self.banco.cursor()
        try:
            cur.execute('SET SQL_SAFE_UPDATES=0')
            self.chamar('sp_reajustar_precos_categoria',(c,p))
        finally:
            try: cur.execute('SET SQL_SAFE_UPDATES=1')
            finally: cur.close()
    def listarHistoricoPrecos(self): return self.consultar('SELECT * FROM historico_preco ORDER BY id_historico DESC')
    def categorias(self): return self.consultar('SELECT id_categoria,nome FROM categoria ORDER BY nome')
    def itens(self,p): return self.consultar('SELECT i.id_produto,p.nome,i.quantidade,i.preco_unitario FROM item_pedido i JOIN produto p ON p.id_produto=i.id_produto WHERE i.id_pedido=%s',(p,))
    def total(self,p): return self.consultar('SELECT fn_total_pedido(%s)',(p,))[0][0]
    def fechar(self): self.banco.close()
