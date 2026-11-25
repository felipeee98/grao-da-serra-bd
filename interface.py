import customtkinter as ct
from tkinter import ttk, messagebox
from decimal import Decimal
from conexao import Dados
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

ct.set_appearance_mode('light')
BG='#F7EFE2'; INK='#382820'; SIDE='#692D39'; ACC='#A85138'; GREEN='#466549'; WHITE='#FFFCF5'; MUTED='#796558'; GOLD='#D6AD75'; LINE='#E6D5BF'

def moeda(v): return ('R$ '+format(v,',.2f')).replace(',','@').replace('.',',').replace('@','.')
def ident(s):
    if not s: raise ValueError('Selecione uma opção primeiro.')
    return int(s.split(' - ',1)[0])

class App(ct.CTk):
    def __init__(self):
        super().__init__(); self.title('Grão da Serra | Empório & Café'); self.geometry('1200x780'); self.minsize(1000,650); self.configure(fg_color=BG)
        self.pedido=None; self.pagina='Cardápio'; self.filtro='Todos'; self.status='TODOS'; self.ger='Reposição'; self.busca=''; self.nav={}; self.dados=None
        try: self.dados=Dados()
        except Exception as e:
            self.withdraw(); messagebox.showerror('Conexão MySQL',str(e),parent=self); self.destroy(); return
        self.protocol('WM_DELETE_WINDOW',self.fechar)
        self.geometry('1240x820'); self.minsize(1000,690)
        self.grid_columnconfigure(0,weight=1); self.grid_rowconfigure(2,weight=1)
        header=ct.CTkFrame(self,fg_color=SIDE,corner_radius=0,height=88)
        header.grid(row=0,column=0,sticky='ew'); header.pack_propagate(False)
        logo=ct.CTkFrame(header,fg_color=GOLD,corner_radius=25,width=50,height=50)
        logo.pack(side='left',padx=(28,15),pady=12); logo.pack_propagate(False)
        self.label(logo,'☕',28,SIDE).pack(expand=True)
        brand=ct.CTkFrame(header,fg_color='transparent'); brand.pack(side='left',pady=10)
        ct.CTkLabel(brand,text='Grão da Serra',font=('Georgia',30,'bold'),text_color=WHITE).pack(anchor='w')
        self.label(brand,'E M P Ó R I O   &   C A F É',10,'#EAD3B8').pack(anchor='w')
        self.label(header,'●  MySQL conectado',12,'#EAD3B8').pack(side='right',padx=28)
        nav=ct.CTkFrame(self,fg_color=WHITE,corner_radius=0,height=56)
        nav.grid(row=1,column=0,sticky='ew'); nav.pack_propagate(False)
        for num,nome in enumerate(['Cardápio','Novo pedido','Pedidos','Gerência'],1):
            b=ct.CTkButton(nav,text=nome,height=36,width=155,corner_radius=6,fg_color='transparent',text_color=INK,hover_color='#F0DFCA',font=('Segoe UI',14,'bold'),command=lambda n=nome:self.acao(lambda:self.mostrar(n)))
            b.pack(side='left',padx=(28 if num==1 else 8,0),pady=10); self.nav[nome]=b
        self.label(nav,'ATENDIMENTO  •  GESTÃO',10,MUTED).pack(side='right',padx=28)
        self.main=ct.CTkFrame(self,fg_color=BG,corner_radius=0); self.main.grid(row=2,column=0,sticky='nsew'); self.mostrar('Cardápio')
    def label(self,p,t,size=14,color=INK,bold=False): return ct.CTkLabel(p,text=t,text_color=color,font=('Segoe UI',size,'bold' if bold else 'normal'),justify='left')
    def botao(self,p,t,fn,color=ACC): return ct.CTkButton(p,text=t,command=lambda:self.acao(fn),fg_color=color,hover_color=SIDE,height=36,corner_radius=9,font=('Segoe UI',13,'bold'))
    def acao(self,fn):
        try: fn()
        except Exception as e: messagebox.showerror('Grão da Serra',getattr(e,'msg',str(e)),parent=self)
    def fechar(self):
        if self.dados: self.dados.fechar()
        self.destroy()
    def mostrar(self,n):
        self.pagina=n
        for nome,b in self.nav.items(): b.configure(fg_color=ACC if nome==n else 'transparent',text_color=WHITE if nome==n else INK,hover_color=SIDE if nome==n else '#F0DFCA')
        for w in self.main.winfo_children(): w.destroy()
        head=ct.CTkFrame(self.main,fg_color='transparent'); head.pack(fill='x',padx=28,pady=(22,12))
        ct.CTkLabel(head,text={'Cardápio':'Cardápio da casa','Novo pedido':'Nova comanda','Pedidos':'Caderno de pedidos','Gerência':'Gestão da cafeteria'}[n],font=('Georgia',30,'bold'),text_color=INK).pack(anchor='w'); self.label(head,{'Cardápio':'Conheça os produtos e escolha o que servir.','Novo pedido':'Atendimento e fechamento de comandas.','Pedidos':'Acompanhe os pedidos registrados.','Gerência':'Estoque, desempenho e preços.'}[n],14,MUTED).pack(anchor='w')
        self.label(self.main,'Felipe Lopes de Goes Couto  •  Banco de Dados',11,MUTED).pack(side='bottom',pady=10)
        self.area=ct.CTkFrame(self.main,fg_color='transparent'); self.area.pack(fill='both',expand=True,padx=28,pady=(0,8))
        {'Cardápio':self.cardapio,'Novo pedido':self.novo,'Pedidos':self.pedidos,'Gerência':self.gerencia}[n]()
    def cardapio(self):
        self.catalogo=self.dados.listarCardapio()
        bar=ct.CTkFrame(self.area,fg_color='transparent'); bar.pack(fill='x',pady=(0,10))
        cats=['Todos']+list(dict.fromkeys(x[1] for x in self.catalogo))
        self.cat=self.combo(bar,cats); self.cat.configure(command=self.filtrar,width=190); self.cat.set(self.filtro); self.cat.pack(side='left')
        busca=ct.CTkEntry(bar,placeholder_text='Buscar no cardápio...',width=250,fg_color=WHITE,border_color=LINE,text_color=INK); busca.pack(side='left',padx=10)
        if self.busca: busca.insert(0,self.busca)
        busca.bind('<KeyRelease>',lambda e:self.buscar(busca.get()))
        self.botao(bar,'Atualizar',lambda:self.mostrar('Cardápio')).pack(side='right')
        corpo=ct.CTkFrame(self.area,fg_color='transparent'); corpo.pack(fill='both',expand=True)
        corpo.grid_columnconfigure(0,weight=0); corpo.grid_columnconfigure(1,weight=1); corpo.grid_rowconfigure(0,weight=1)
        poster=ct.CTkFrame(corpo,fg_color=SIDE,corner_radius=14,width=245); poster.grid(row=0,column=0,sticky='nsew',padx=(0,14)); poster.pack_propagate(False)
        self.label(poster,'✦   GRÃO DA SERRA   ✦',11,GOLD,True).pack(pady=(25,6))
        self.label(poster,'☕',72,GOLD).pack(pady=(12,0))
        ct.CTkLabel(poster,text='Sabores\n da serra',font=('Georgia',30,'italic'),text_color=WHITE,justify='center').pack(pady=10)
        ct.CTkFrame(poster,fg_color=GOLD,height=1,width=130).pack(pady=12)
        self.label(poster,'Cafés • Doces • Salgados',12,'#EAD3B8').pack(pady=5)
        self.label(poster,'Bebidas e produtos do empório',11,'#EAD3B8').pack()
        self.label(poster,'Escolha um produto no menu\npara iniciar a sua comanda.',12,WHITE).pack(side='bottom',pady=25)
        self.menu=ct.CTkScrollableFrame(corpo,fg_color=WHITE,corner_radius=14,border_width=1,border_color=LINE,scrollbar_button_color='#D6BCA2',scrollbar_button_hover_color=ACC); self.menu.grid(row=0,column=1,sticky='nsew')
        self.render_cards()
    def filtrar(self,v): self.filtro=v; self.acao(self.render_cards)
    def buscar(self,v): self.busca=v; self.acao(self.render_cards)
    def render_cards(self):
        for w in self.menu.winfo_children(): w.destroy()
        dados=[x for x in self.catalogo if (self.filtro=='Todos' or x[1]==self.filtro) and self.busca.casefold() in x[2].casefold()]
        if not dados: self.label(self.menu,'Nenhum produto encontrado.',16,MUTED).pack(pady=30); return
        icones={'Cafés':'☕','Doces':'♧','Salgados':'✦','Empório':'◇','Bebidas geladas':'❄'}
        for cat in dict.fromkeys(x[1] for x in dados):
            cab=ct.CTkFrame(self.menu,fg_color='#F3E5D2',corner_radius=6); cab.pack(fill='x',padx=12,pady=(13,3))
            ct.CTkLabel(cab,text=f'{icones.get(cat,"•")}   {cat}',text_color=SIDE,font=('Georgia',19,'bold')).pack(side='left',padx=12,pady=6)
            for id,c,n,p,s in (x for x in dados if x[1]==cat):
                linha=ct.CTkFrame(self.menu,fg_color='transparent'); linha.pack(fill='x',padx=14,pady=3)
                info=ct.CTkFrame(linha,fg_color='transparent'); info.pack(side='left',fill='x',expand=True,padx=5)
                self.label(info,n,15,INK,True).pack(anchor='w')
                self.label(info,{'OK':'Disponível','REPOR':'Estoque baixo','ESGOTADO':'Esgotado'}.get(s,s),11,{'OK':GREEN,'REPOR':'#9A5B20','ESGOTADO':'#8D827A'}.get(s,MUTED)).pack(anchor='w')
                b=self.botao(linha,'Escolher',lambda id=id:self.escolher(id)); b.configure(width=92,height=32); b.pack(side='right',padx=(10,0))
                if s=='ESGOTADO': b.configure(state='disabled',text='Esgotado',fg_color='#E6DCD0')
                ct.CTkLabel(linha,text=moeda(p),font=('Georgia',17,'bold'),text_color=SIDE,width=110,anchor='e').pack(side='right')
                ct.CTkFrame(self.menu,fg_color=LINE,height=1,corner_radius=0).pack(fill='x',padx=18)
    def escolher(self,id):
        self.mostrar('Novo pedido')
        for s in self.prod.cget('values'):
            if ident(s)==id: self.prod.set(s); break
    def combo(self,p,values):
        c=ct.CTkComboBox(p,values=values or [''],state='readonly',width=240,fg_color=WHITE,border_color=LINE,button_color=ACC,button_hover_color=SIDE,text_color=INK,dropdown_fg_color=WHITE,dropdown_text_color=INK); c.set(values[0] if values else ''); return c
    def tabela(self,p,headers,rows):
        f=ct.CTkFrame(p,fg_color=WHITE); f.pack(fill='both',expand=True,pady=8)
        style=ttk.Style(); style.theme_use('clam'); style.configure('Treeview',rowheight=34,font=('Segoe UI',10),background=WHITE,fieldbackground=WHITE,borderwidth=0); style.configure('Treeview.Heading',background=SIDE,foreground=WHITE,font=('Segoe UI',10,'bold'),padding=6); style.map('Treeview',background=[('selected','#EAD3B8')],foreground=[('selected',INK)])
        t=ttk.Treeview(f,columns=headers,show='headings',height=6); y=ttk.Scrollbar(f,orient='vertical',command=t.yview); x=ttk.Scrollbar(f,orient='horizontal',command=t.xview); t.configure(yscrollcommand=y.set,xscrollcommand=x.set); y.pack(side='right',fill='y'); x.pack(side='bottom',fill='x'); t.pack(fill='both',expand=True)
        for h in headers:
            t.heading(h,text=h); t.column(h,width={'ID':55,'Produto':230,'Categoria':160,'Data':160,'Cliente':200,'Atendente':160,'Situação':110,'Usuário':145,'Preço unitário':135}.get(h,105),minwidth=50,anchor='w' if h in ('Produto','Categoria','Cliente','Atendente') else 'center')
        for i,r in enumerate(rows): t.insert('', 'end',values=r,tags=('odd' if i%2 else 'even',))
        t.tag_configure('odd',background='#F8F1E7'); return t
    def novo(self):
        corpo=ct.CTkFrame(self.area,fg_color='transparent'); corpo.pack(fill='both',expand=True)
        corpo.grid_columnconfigure(0,weight=2,uniform='comanda'); corpo.grid_columnconfigure(1,weight=3,uniform='comanda'); corpo.grid_rowconfigure(0,weight=1)
        f=ct.CTkFrame(corpo,fg_color=WHITE,corner_radius=14,border_width=1,border_color=LINE); f.grid(row=0,column=0,sticky='nsew',padx=(0,12))
        self.label(f,'1. Identificação',19,SIDE,True).pack(anchor='w',padx=18,pady=(18,4))
        clientes=[f'{a} - {b}' for a,b in self.dados.listarClientes()]; funcionarios=[f'{a} - {b}' for a,b in self.dados.listarFuncionarios()]
        atual=next((r for r in self.dados.listarPedidos('ABERTO') if r[0]==self.pedido),None) if self.pedido else None
        self.label(f,'Cliente',12,MUTED).pack(anchor='w',padx=18,pady=(8,0))
        self.cliente=self.combo(f,clientes); self.cliente.pack(fill='x',padx=18,pady=(0,8))
        self.label(f,'Funcionário',12,MUTED).pack(anchor='w',padx=18)
        self.func=self.combo(f,funcionarios); self.func.pack(fill='x',padx=18,pady=(0,10))
        abrir=self.botao(f,'Abrir pedido',self.abrir); abrir.pack(fill='x',padx=18,pady=4)
        if atual:
            for combo,opcoes,nome in [(self.cliente,clientes,atual[3]),(self.func,funcionarios,atual[4])]:
                opcao=next((v for v in opcoes if v.split(' - ',1)[1]==nome),None)
                if opcao: combo.set(opcao)
                combo.configure(state='disabled')
            abrir.configure(state='disabled',text='Comanda aberta')
        ct.CTkFrame(f,fg_color=LINE,height=1).pack(fill='x',padx=18,pady=15)
        self.label(f,'2. Adicionar produto',19,SIDE,True).pack(anchor='w',padx=18)
        self.label(f,'Produto',12,MUTED).pack(anchor='w',padx=18,pady=(8,0))
        self.prod=self.combo(f,[f'{x[0]} - {x[2]}' for x in self.dados.listarCardapio() if x[4]!='ESGOTADO']); self.prod.pack(fill='x',padx=18)
        row=ct.CTkFrame(f,fg_color='transparent'); row.pack(fill='x',padx=18,pady=10)
        self.label(row,'Qtd.',12,MUTED).pack(side='left'); self.q=ct.CTkEntry(row,width=56,fg_color=WHITE,border_color=LINE); self.q.insert(0,'1'); self.q.pack(side='left',padx=8)
        self.botao(row,'Adicionar',self.adicionar).pack(side='left',fill='x',expand=True)
        recibo=ct.CTkFrame(corpo,fg_color=WHITE,corner_radius=14,border_width=1,border_color=LINE); recibo.grid(row=0,column=1,sticky='nsew')
        ct.CTkLabel(recibo,text='Grão da Serra',font=('Georgia',24,'bold'),text_color=SIDE).pack(pady=(16,0))
        self.label(recibo,f'COMANDA #{self.pedido:03d}' if self.pedido else 'COMANDA NÃO ABERTA',13,MUTED,True).pack(pady=(0,6))
        ct.CTkFrame(recibo,fg_color=LINE,height=1).pack(fill='x',padx=18)
        itens=self.dados.itens(self.pedido) if self.pedido else []
        total=self.dados.total(self.pedido) if self.pedido else Decimal(0)
        rod=ct.CTkFrame(recibo,fg_color='#F3E5D2',corner_radius=8); rod.pack(side='bottom',fill='x',padx=12,pady=12)
        self.label(rod,'TOTAL BRUTO',11,MUTED,True).pack(anchor='w',padx=15,pady=(10,0))
        ct.CTkLabel(rod,text=moeda(total),font=('Georgia',29,'bold'),text_color=SIDE).pack(anchor='w',padx=15)
        self.label(rod,'Desconto e total final calculados no fechamento.',11,MUTED).pack(anchor='w',padx=15,pady=(0,7))
        botoes=ct.CTkFrame(rod,fg_color='transparent'); botoes.pack(fill='x',padx=12,pady=(0,10))
        self.botao(botoes,'Remover item',self.remover,ACC).pack(side='left',padx=(0,6))
        self.botao(botoes,'Finalizar pedido',self.finalizar,GREEN).pack(side='right',fill='x',expand=True)
        area_itens=ct.CTkFrame(recibo,fg_color='transparent'); area_itens.pack(fill='both',expand=True,padx=12,pady=(4,0))
        self.tab=self.tabela(area_itens,('ID','Produto','Qtd.','Preço unitário'),[(a,b,c,moeda(d)) for a,b,c,d in itens])
        self.tab.column('ID',width=38,minwidth=30,stretch=False); self.tab.column('Qtd.',width=54,minwidth=45,stretch=False); self.tab.column('Preço unitário',width=105,minwidth=90,stretch=False); self.tab.column('Produto',width=160,minwidth=110)
    def abrir(self):
        if self.pedido: raise ValueError('Finalize a comanda atual primeiro.')
        produto_escolhido=self.prod.get(); quantidade=self.q.get()
        self.pedido=self.dados.abrirPedido(ident(self.cliente.get()),ident(self.func.get())); self.mostrar('Novo pedido')
        if produto_escolhido in self.prod.cget('values'): self.prod.set(produto_escolhido)
        self.q.delete(0,'end'); self.q.insert(0,quantidade)
    def exigir(self):
        if not self.pedido: raise ValueError('Abra uma comanda primeiro.')
    def adicionar(self): self.exigir(); self.dados.adicionarItem(self.pedido,ident(self.prod.get()),int(self.q.get())); self.mostrar('Novo pedido')
    def remover(self):
        self.exigir(); s=self.tab.selection()
        if not s: raise ValueError('Selecione um item.')
        self.dados.removerItem(self.pedido,int(self.tab.item(s[0])['values'][0])); self.mostrar('Novo pedido')
    def finalizar(self):
        self.exigir(); d,t=self.dados.finalizarPedido(self.pedido); p=self.pedido; self.pedido=None; messagebox.showinfo('Comanda finalizada',f'Pedido #{p}\nDesconto: {d}%\nTotal: {moeda(t)}',parent=self); self.mostrar('Novo pedido')
    def pedidos(self):
        bar=ct.CTkFrame(self.area,fg_color='transparent'); bar.pack(fill='x'); c=ct.CTkComboBox(bar,values=['TODOS','ABERTO','PAGO','CANCELADO'],state='readonly',command=self.status_mudar,fg_color=WHITE,border_color=LINE,button_color=ACC,button_hover_color=SIDE,text_color=INK); c.set(self.status); c.pack(side='left'); self.botao(bar,'Atualizar',lambda:self.mostrar('Pedidos')).pack(side='right')
        dados=self.dados.listarPedidos(self.status); self.tabp=self.tabela(self.area,('ID','Data','Status','Cliente','Atendente','Itens','Bruto','Desc. %','Total'),[(*r[:6],moeda(r[6]),r[7],moeda(r[8])) for r in dados]); self.botao(self.area,'Continuar pedido aberto',self.continuar).pack(anchor='e',pady=5)
    def status_mudar(self,v): self.status=v; self.mostrar('Pedidos')
    def continuar(self):
        s=self.tabp.selection()
        if not s: raise ValueError('Selecione um pedido.')
        r=self.tabp.item(s[0])['values']
        if r[2]!='ABERTO': raise ValueError('O pedido não está aberto.')
        
        if self.pedido and self.pedido!=int(r[0]):
            if not messagebox.askyesno('Trocar comanda','A comanda atual permanecerá aberta. Continuar outra?',parent=self): return
        self.pedido=int(r[0]); self.mostrar('Novo pedido')
    def gerencia(self):
        seg=ct.CTkSegmentedButton(self.area,values=['Reposição','Vendas','Preços'],command=self.ger_mudar,selected_color=ACC,selected_hover_color=SIDE,fg_color='#806151',unselected_color='#806151',unselected_hover_color=SIDE,text_color=WHITE); seg.set(self.ger); seg.pack(fill='x',pady=6)
        if self.ger=='Reposição': self.tabela(self.area,('ID','Produto','Categoria','Estoque','Mínimo','Faltam'),self.dados.listarProdutosParaRepor())
        elif self.ger=='Vendas':
            rows=self.dados.listarVendasPorCategoria(); self.tabela(self.area,('Categoria','Unidades','Faturamento'),[(a,b,moeda(c)) for a,b,c in rows]); fig=Figure(figsize=(7,2.6),dpi=100,facecolor=BG); ax=fig.add_subplot(111); barras=ax.barh([r[0] for r in rows],[float(r[2]) for r in rows],color=ACC); ax.invert_yaxis(); ax.set_xlabel('R$'); ax.set_title('Faturamento bruto por categoria',loc='left',color=INK); ax.spines[['top','right','left']].set_visible(False); ax.tick_params(axis='both',labelsize=9); ax.grid(axis='x',alpha=.16); ax.set_axisbelow(True); ax.margins(x=.2); ax.bar_label(barras,labels=[moeda(r[2]) for r in rows],padding=4,fontsize=8,color=INK); fig.tight_layout(); canvas=FigureCanvasTkAgg(fig,master=self.area); canvas.draw(); canvas.get_tk_widget().pack(fill='both',expand=True)
        else:
            row=ct.CTkFrame(self.area,fg_color=WHITE); row.pack(fill='x',pady=8); self.catpre=self.combo(row,[f'{a} - {b}' for a,b in self.dados.categorias()]); self.catpre.pack(side='left',padx=8,pady=12); self.per=ct.CTkEntry(row,placeholder_text='Percentual (%)',width=130,fg_color=WHITE,border_color=LINE); self.per.pack(side='left',padx=8); self.botao(row,'Aplicar reajuste',self.reajustar).pack(side='left'); self.tabela(self.area,('ID','Produto ID','Preço antigo','Preço novo','Data','Usuário'),[(a,b,moeda(c),moeda(d),e,f) for a,b,c,d,e,f in self.dados.listarHistoricoPrecos()])
    def ger_mudar(self,v): self.ger=v; self.mostrar('Gerência')
    def reajustar(self):
        v=Decimal(self.per.get().replace(',','.')); c=ident(self.catpre.get())
        if messagebox.askyesno('Confirmar reajuste',f'Aplicar {v}% nesta categoria?',parent=self): self.dados.reajustarPrecos(c,v); self.mostrar('Gerência')

if __name__=='__main__':
    app=App(); app.mainloop()
