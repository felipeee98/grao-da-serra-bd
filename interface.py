import customtkinter as ct
from tkinter import ttk, messagebox
from decimal import Decimal
from conexao import Dados
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

ct.set_appearance_mode('light')
BG='#F5F1E9'; INK='#30251E'; SIDE='#30251E'; ACC='#98643D'; GREEN='#527452'; WHITE='#FFFFFF'; MUTED='#807568'

def moeda(v): return ('R$ '+format(v,',.2f')).replace(',','@').replace('.',',').replace('@','.')
def ident(s): return int(s.split(' - ',1)[0])

class App(ct.CTk):
    def __init__(self):
        super().__init__(); self.title('Grão da Serra | Empório & Café'); self.geometry('1200x780'); self.minsize(1000,650); self.configure(fg_color=BG)
        self.pedido=None; self.pagina='Cardápio'; self.filtro='Todos'; self.status='TODOS'; self.ger='Reposição'; self.busca=''; self.nav={}; self.dados=None
        try: self.dados=Dados()
        except Exception as e:
            self.withdraw(); messagebox.showerror('Conexão MySQL',str(e),parent=self); self.destroy(); return
        self.protocol('WM_DELETE_WINDOW',self.fechar)
        self.grid_columnconfigure(1,weight=1); self.grid_rowconfigure(0,weight=1)
        side=ct.CTkFrame(self,fg_color=SIDE,corner_radius=0,width=230); side.grid(row=0,column=0,sticky='nsew'); side.grid_propagate(False)
        self.label(side,'☕',42,'#EAC69B').pack(anchor='w',padx=24,pady=(28,0)); self.label(side,'GRÃO DA\nSERRA',28,'#FFFFFF',True).pack(anchor='w',padx=24,pady=(0,4)); self.label(side,'EMPÓRIO & CAFÉ',12,'#D3BDA6').pack(anchor='w',padx=24,pady=(0,36))
        for nome in ['Cardápio','Novo pedido','Pedidos','Gerência']:
            b=ct.CTkButton(side,text=nome,anchor='w',height=46,corner_radius=10,fg_color='transparent',hover_color='#624735',font=('Segoe UI',15),command=lambda n=nome:self.acao(lambda:self.mostrar(n))); b.pack(fill='x',padx=14,pady=4); self.nav[nome]=b
        self.label(side,'●  MySQL conectado',13,'#A8D3A7').pack(side='bottom',anchor='w',padx=20,pady=22)
        self.main=ct.CTkFrame(self,fg_color=BG,corner_radius=0); self.main.grid(row=0,column=1,sticky='nsew'); self.mostrar('Cardápio')
    def label(self,p,t,size=14,color=INK,bold=False): return ct.CTkLabel(p,text=t,text_color=color,font=('Segoe UI',size,'bold' if bold else 'normal'),justify='left')
    def botao(self,p,t,fn,color=ACC): return ct.CTkButton(p,text=t,command=lambda:self.acao(fn),fg_color=color,hover_color='#765033',height=36,corner_radius=9,font=('Segoe UI',13,'bold'))
    def acao(self,fn):
        try: fn()
        except Exception as e: messagebox.showerror('Grão da Serra',getattr(e,'msg',str(e)),parent=self)
    def fechar(self):
        if self.dados: self.dados.fechar()
        self.destroy()
    def mostrar(self,n):
        self.pagina=n
        for nome,b in self.nav.items(): b.configure(fg_color=ACC if nome==n else 'transparent')
        for w in self.main.winfo_children(): w.destroy()
        head=ct.CTkFrame(self.main,fg_color='transparent'); head.pack(fill='x',padx=28,pady=(22,12))
        self.label(head,n,32,INK,True).pack(anchor='w'); self.label(head,{'Cardápio':'Sabores da serra, preparados com carinho.','Novo pedido':'Atendimento e fechamento de comandas.','Pedidos':'Acompanhe os pedidos registrados.','Gerência':'Estoque, desempenho e preços.'}[n],14,MUTED).pack(anchor='w')
        self.label(self.main,'Felipe Lopes de Goes Couto  •  Banco de Dados',11,MUTED).pack(side='bottom',pady=10)
        self.area=ct.CTkFrame(self.main,fg_color='transparent'); self.area.pack(fill='both',expand=True,padx=28,pady=(0,8))
        {'Cardápio':self.cardapio,'Novo pedido':self.novo,'Pedidos':self.pedidos,'Gerência':self.gerencia}[n]()
    def cardapio(self):
        dados=self.dados.listarCardapio(); bar=ct.CTkFrame(self.area,fg_color='transparent'); bar.pack(fill='x',pady=(0,12))
        cats=['Todos']+list(dict.fromkeys(x[1] for x in dados)); self.cat=ct.CTkComboBox(bar,values=cats,state='readonly',command=self.filtrar); self.cat.set(self.filtro); self.cat.pack(side='left')
        busca=ct.CTkEntry(bar,placeholder_text='Buscar produto...',width=220); busca.pack(side='left',padx=10); busca.insert(0,self.busca); busca.bind('<KeyRelease>',lambda e:self.buscar(busca.get()))
        self.botao(bar,'Atualizar',lambda:self.mostrar('Cardápio')).pack(side='right')
        self.cards=ct.CTkScrollableFrame(self.area,fg_color='transparent'); self.cards.pack(fill='both',expand=True); self.render_cards()
    def filtrar(self,v): self.filtro=v; self.acao(self.render_cards)
    def buscar(self,v): self.busca=v; self.acao(self.render_cards)
    def render_cards(self):
        for w in self.cards.winfo_children(): w.destroy()
        for j in range(3): self.cards.grid_columnconfigure(j,weight=1,uniform='cards')
        dados=[x for x in self.dados.listarCardapio() if (self.filtro=='Todos' or x[1]==self.filtro) and self.busca.casefold() in x[2].casefold()]
        for i,(id,c,n,p,s) in enumerate(dados):
            f=ct.CTkFrame(self.cards,fg_color=WHITE,corner_radius=16,border_width=1,border_color='#E5DED3'); f.grid(row=i//3,column=i%3,padx=6,pady=6,sticky='nsew')
            banner=ct.CTkFrame(f,fg_color='#EEE2D1',height=76,corner_radius=12); banner.pack(fill='x',padx=10,pady=10); banner.pack_propagate(False)
            self.label(banner,{'Cafés':'☕','Doces':'🍰','Salgados':'🥐','Empório':'🍯','Bebidas geladas':'🥤'}.get(c,'☕'),36,ACC).pack(expand=True)
            self.label(f,c.upper(),10,MUTED,True).pack(anchor='w',padx=12); l=self.label(f,n,15,INK,True); l.configure(wraplength=190); l.pack(anchor='w',padx=12,pady=(3,5)); self.label(f,moeda(p),21,ACC,True).pack(anchor='w',padx=12)
            self.label(f,{'OK':'● Disponível','REPOR':'● Estoque baixo','ESGOTADO':'● Esgotado'}[s],12,{'OK':GREEN,'REPOR':'#A76A16','ESGOTADO':'#999999'}[s]).pack(anchor='w',padx=12,pady=(4,10))
            b=self.botao(f,'Adicionar ao pedido',lambda id=id:self.escolher(id)); b.pack(fill='x',padx=10,pady=(0,10));
            if s=='ESGOTADO': b.configure(state='disabled',fg_color='#DFDAD2')
    def escolher(self,id):
        self.mostrar('Novo pedido')
        for s in self.prod.cget('values'):
            if ident(s)==id: self.prod.set(s); break
    def combo(self,p,values):
        c=ct.CTkComboBox(p,values=values or [''],state='readonly',width=240); c.set(values[0] if values else ''); return c
    def tabela(self,p,headers,rows):
        f=ct.CTkFrame(p,fg_color=WHITE); f.pack(fill='both',expand=True,pady=8)
        style=ttk.Style(); style.theme_use('clam'); style.configure('Treeview',rowheight=34,font=('Segoe UI',10),background=WHITE,fieldbackground=WHITE,borderwidth=0); style.configure('Treeview.Heading',background='#EAE0D2',foreground=INK,font=('Segoe UI',10,'bold'),padding=6); style.map('Treeview',background=[('selected','#C9AB8C')],foreground=[('selected',INK)])
        t=ttk.Treeview(f,columns=headers,show='headings',height=6); y=ttk.Scrollbar(f,orient='vertical',command=t.yview); x=ttk.Scrollbar(f,orient='horizontal',command=t.xview); t.configure(yscrollcommand=y.set,xscrollcommand=x.set); y.pack(side='right',fill='y'); x.pack(side='bottom',fill='x'); t.pack(fill='both',expand=True)
        for h in headers: t.heading(h,text=h); t.column(h,width=110,minwidth=65,anchor='center')
        for i,r in enumerate(rows): t.insert('', 'end',values=r,tags=('odd' if i%2 else 'even',))
        t.tag_configure('odd',background='#F8F5EF'); return t
    def novo(self):
        f=ct.CTkFrame(self.area,fg_color=WHITE,corner_radius=14); f.pack(fill='x',pady=6); self.label(f,'01  •  Identificação',16,INK,True).pack(anchor='w',padx=14,pady=8)
        row=ct.CTkFrame(f,fg_color='transparent'); row.pack(fill='x',padx=14,pady=(0,12)); self.cliente=self.combo(row,[f'{a} - {b}' for a,b in self.dados.listarClientes()]); self.cliente.pack(side='left',padx=4); self.func=self.combo(row,[f'{a} - {b}' for a,b in self.dados.listarFuncionarios()]); self.func.pack(side='left',padx=4); self.botao(row,'Abrir pedido',self.abrir).pack(side='left',padx=4)
        self.label(self.area,f'Comanda #{self.pedido}' if self.pedido else 'Nenhuma comanda selecionada',20,INK,True).pack(anchor='w',pady=8)
        row=ct.CTkFrame(self.area,fg_color='transparent'); row.pack(fill='x'); self.prod=self.combo(row,[f'{x[0]} - {x[2]}' for x in self.dados.listarCardapio() if x[4]!='ESGOTADO']); self.prod.pack(side='left'); self.q=ct.CTkEntry(row,width=75); self.q.insert(0,'1'); self.q.pack(side='left',padx=8); self.botao(row,'Adicionar',self.adicionar).pack(side='left')
        itens=self.dados.itens(self.pedido) if self.pedido else []; self.tab=self.tabela(self.area,('ID','Produto','Quantidade','Preço unitário'),[(a,b,c,moeda(d)) for a,b,c,d in itens]); total=self.dados.total(self.pedido) if self.pedido else Decimal(0)
        row=ct.CTkFrame(self.area,fg_color=WHITE,corner_radius=14); row.pack(fill='x',pady=8); self.label(row,'Total bruto: '+moeda(total),22,INK,True).pack(side='left',padx=12,pady=14); self.botao(row,'Finalizar pedido',self.finalizar,GREEN).pack(side='right',padx=10); self.botao(row,'Remover item',self.remover).pack(side='right')
    def abrir(self):
        if self.pedido: raise ValueError('Finalize a comanda atual primeiro.')
        self.pedido=self.dados.abrirPedido(ident(self.cliente.get()),ident(self.func.get())); self.mostrar('Novo pedido')
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
        bar=ct.CTkFrame(self.area,fg_color='transparent'); bar.pack(fill='x'); c=ct.CTkComboBox(bar,values=['TODOS','ABERTO','PAGO','CANCELADO'],state='readonly',command=self.status_mudar); c.set(self.status); c.pack(side='left'); self.botao(bar,'Atualizar',lambda:self.mostrar('Pedidos')).pack(side='right')
        dados=self.dados.listarPedidos(self.status); self.tabp=self.tabela(self.area,('ID','Data','Status','Cliente','Atendente','Itens','Bruto','Desc. %','Total'),[(*r[:6],moeda(r[6]),r[7],moeda(r[8])) for r in dados]); self.botao(self.area,'Continuar pedido aberto',self.continuar).pack(anchor='e',pady=5)
    def status_mudar(self,v): self.status=v; self.mostrar('Pedidos')
    def continuar(self):
        s=self.tabp.selection()
        if not s: raise ValueError('Selecione um pedido.')
        r=self.tabp.item(s[0])['values']
        if r[2]!='ABERTO': raise ValueError('O pedido não está aberto.')
        self.pedido=int(r[0]); self.mostrar('Novo pedido')
    def gerencia(self):
        seg=ct.CTkSegmentedButton(self.area,values=['Reposição','Vendas','Preços'],command=self.ger_mudar,selected_color=ACC,selected_hover_color='#765033'); seg.set(self.ger); seg.pack(fill='x',pady=6)
        if self.ger=='Reposição': self.tabela(self.area,('ID','Produto','Categoria','Estoque','Mínimo','Faltam'),self.dados.listarProdutosParaRepor())
        elif self.ger=='Vendas':
            rows=self.dados.listarVendasPorCategoria(); self.tabela(self.area,('Categoria','Unidades','Faturamento'),[(a,b,moeda(c)) for a,b,c in rows]); fig=Figure(figsize=(7,2.6),dpi=100,facecolor=BG); ax=fig.add_subplot(111); ax.bar([r[0] for r in rows],[float(r[2]) for r in rows],color=ACC); ax.set_ylabel('R$'); ax.set_title('Faturamento bruto por categoria'); ax.spines[['top','right']].set_visible(False); ax.tick_params(axis='x',labelsize=8); fig.tight_layout(); canvas=FigureCanvasTkAgg(fig,master=self.area); canvas.draw(); canvas.get_tk_widget().pack(fill='both',expand=True)
        else:
            row=ct.CTkFrame(self.area,fg_color=WHITE); row.pack(fill='x',pady=8); self.catpre=self.combo(row,[f'{a} - {b}' for a,b in self.dados.categorias()]); self.catpre.pack(side='left',padx=8,pady=12); self.per=ct.CTkEntry(row,placeholder_text='Percentual (%)',width=130); self.per.pack(side='left',padx=8); self.botao(row,'Aplicar reajuste',self.reajustar).pack(side='left'); self.tabela(self.area,('ID','Produto ID','Preço antigo','Preço novo','Data','Usuário'),[(a,b,moeda(c),moeda(d),e,f) for a,b,c,d,e,f in self.dados.listarHistoricoPrecos()])
    def ger_mudar(self,v): self.ger=v; self.mostrar('Gerência')
    def reajustar(self):
        v=Decimal(self.per.get().replace(',','.')); c=ident(self.catpre.get())
        if messagebox.askyesno('Confirmar reajuste',f'Aplicar {v}% nesta categoria?',parent=self): self.dados.reajustarPrecos(c,v); self.mostrar('Gerência')

if __name__=='__main__':
    app=App(); app.mainloop()
