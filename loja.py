# Código Principal (somente interfce)

import os
import shutil
from tkinter import filedialog, messagebox
import customtkinter as ctk
from PIL import Image
from banco import Banco
from modelos import CATEGORIAS, PAGAMENTOS, Endereco, criar_produto

PRETO, BRANCO, LINHA, VERDE = "#0D0D0D", "#F4F4F0", "#262626", "#C8FF00"
VERDE_ESCURO, CINZA, FUNDO_IMG = "#516800", "#8A8A85", "#161616"
SANS, MONO = "Syne", "DejaVu Sans Mono"
LISTA_CATEGORIAS = list(CATEGORIAS)
REFS = []

ctk.set_appearance_mode("dark")
os.makedirs("imagens", exist_ok=True)


def moeda(valor):
    return "R$ " + f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def botao(pai, texto, comando, primario=True, largura=140, altura=42):
    if primario:
        cores = dict(fg_color=VERDE, hover_color=VERDE_ESCURO, text_color=PRETO)
    else:
        cores = dict(fg_color="transparent", hover_color=LINHA, text_color=BRANCO, border_width=1, border_color=BRANCO)

    return ctk.CTkButton(pai, text=texto.upper(), command=comando, width=largura, height=altura, corner_radius=0, font=(MONO, 13, "bold"), **cores)


def legenda(pai, texto):
    ctk.CTkLabel(pai, text=texto.upper(), font=(MONO, 11), text_color=CINZA, anchor="w").pack(fill="x", padx=4, pady=(10, 0))


def campo(pai, rotulo, dica="", lado="top", **kw):
    f = ctk.CTkFrame(pai, fg_color="transparent")
    f.pack(side=lado, fill="x", expand=lado != "top", padx=4, pady=4)

    legenda(f, rotulo)

    e = ctk.CTkEntry(f, placeholder_text=dica, height=40, corner_radius=0, fg_color=PRETO, border_width=1, border_color=LINHA, text_color=BRANCO, placeholder_text_color="#55554F", font=(MONO, 13), **kw)
    e.pack(fill="x")

    return e


def menu(pai, valores):
    return ctk.CTkOptionMenu(pai, values=valores, height=40, corner_radius=0, fg_color=PRETO, button_color=VERDE,  button_hover_color=VERDE_ESCURO, dropdown_fg_color=PRETO, text_color=BRANCO, font=(MONO, 13))


def imagem(pai, caminho, tamanho):
    if caminho and os.path.exists(caminho):
        pil = Image.open(caminho)
        pil.thumbnail((tamanho, tamanho))
        REFS.append(ctk.CTkImage(light_image=pil, size=pil.size))
        return ctk.CTkLabel(pai, image=REFS[-1], text="")

    return ctk.CTkLabel(pai, text="SEM IMAGEM", font=(MONO, 11), text_color="#55554F")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("STUXNET")
        self.geometry("1200x800")
        self.minsize(1000, 700)
        self.configure(fg_color=PRETO)
        self.banco = Banco()
        self.usuario = None
        self.tela_login()

    def limpar(self):
        for w in self.winfo_children():
            w.destroy()

    def cabecalho(self):
        topo = ctk.CTkFrame(self, fg_color=PRETO, corner_radius=0, height=64)
        topo.pack(fill="x")
        topo.pack_propagate(False)
        ctk.CTkLabel(topo, text="STUXNET", font=(SANS, 24, "bold"), text_color=BRANCO).pack(side="left", padx=28)
        if self.usuario:
            botao(topo, "Sair", self.tela_login, primario=False, largura=90, altura=36).pack(side="right", padx=28)
            ctk.CTkLabel(topo, text=f"USUÁRIO: {self.usuario.rotulo()}", font=(MONO, 11), text_color=CINZA).pack(side="right")
        ctk.CTkFrame(self, height=1, corner_radius=0, fg_color=LINHA).pack(fill="x")

    def tela_login(self):
        self.limpar()
        self.usuario = None
        self.cabecalho()

        caixa = ctk.CTkFrame(self, fg_color=PRETO, corner_radius=0, border_width=1, border_color=LINHA)
        caixa.place(relx=0.5, rely=0.5, anchor="center")

        f = ctk.CTkFrame(caixa, fg_color="transparent")
        f.pack(padx=40, pady=30)

        ctk.CTkLabel(f, text="LOGIN", font=(SANS, 22, "bold"), text_color=BRANCO).pack(anchor="w", pady=(0, 6))

        self.e_user = campo(f, "Usuário", width=300)
        self.e_senha = campo(f, "Senha", show="*", width=300)
        self.msg = ctk.CTkLabel(f, text="", text_color=VERDE, font=(MONO, 12))
        self.msg.pack(anchor="w", pady=4)

        botao(f, "Entrar", self.fazer_login, largura=300).pack(fill="x", padx=4, pady=(4, 6))
        botao(f, "Criar conta", self.fazer_cadastro, primario=False, largura=300).pack(fill="x", padx=4)

    def fazer_login(self):
        usuario = self.banco.autenticar(self.e_user.get(), self.e_senha.get())
        if usuario is None:
            self.msg.configure(text="USUÁRIO OU SENHA INCORRETOS.")
            return

        self.usuario = usuario
        getattr(self, f"tela_{usuario.tela_inicial()}")()

    def fazer_cadastro(self):
        try:
            self.banco.cadastrar_usuario(self.e_user.get(), self.e_senha.get())
        except ValueError as erro:
            self.msg.configure(text=str(erro), text_color=VERDE)
            return

        self.msg.configure(text="CONTA CRIADA. CLIQUE EM ENTRAR.", text_color=BRANCO)

    def tela_loja(self):
        self.limpar()
        self.cabecalho()
        self.var_cat = ctk.StringVar(value="Todas")

        corpo = ctk.CTkFrame(self, fg_color=PRETO, corner_radius=0)
        corpo.pack(fill="both", expand=True)

        self.corpo = corpo

        lateral = ctk.CTkFrame(corpo, fg_color=PRETO, corner_radius=0, width=240)
        lateral.pack(side="left", fill="y")
        lateral.pack_propagate(False)

        filtros = ctk.CTkFrame(lateral, fg_color="transparent")
        filtros.pack(fill="both", padx=16, pady=20)

        self.busca = campo(filtros, "Buscar", "nome do produto")
        self.busca.bind("<KeyRelease>", lambda e: self.mostrar_produtos())

        legenda(filtros, "Categorias")

        for cat in ["Todas"] + LISTA_CATEGORIAS:
            ctk.CTkRadioButton(filtros, text=cat.upper(), variable=self.var_cat, value=cat, command=self.mostrar_produtos, font=(MONO, 12), text_color=BRANCO, fg_color=VERDE, hover_color=VERDE_ESCURO, border_color=CINZA, corner_radius=0).pack(anchor="w", pady=5)

        self.area = ctk.CTkScrollableFrame(corpo, fg_color=PRETO, corner_radius=0)
        self.area.pack(side="left", fill="both", expand=True)
        self.mostrar_produtos()

    def mostrar_produtos(self):
        self.area.destroy()
        self.area = ctk.CTkScrollableFrame(self.corpo, fg_color=PRETO, corner_radius=0)
        self.area.pack(side="left", fill="both", expand=True)

        produtos = self.banco.listar_produtos(self.busca.get(), self.var_cat.get())

        if not produtos:
            ctk.CTkLabel(self.area, text="NENHUM PRODUTO ENCONTRADO.", font=(MONO, 13), text_color=CINZA).pack(pady=60)
        for i, p in enumerate(produtos):
            self.card(p, i)

    def card(self, p, i):
        c = ctk.CTkFrame(self.area, fg_color=PRETO, corner_radius=0, border_width=1, border_color=LINHA, width=300, height=375)
        c.grid(row=i // 3, column=i % 3, sticky="nsew")
        c.pack_propagate(False)

        moldura = ctk.CTkFrame(c, fg_color=FUNDO_IMG, corner_radius=0, width=300, height=240)
        moldura.pack(fill="x")
        moldura.pack_propagate(False)

        imagem(moldura, p.imagem, 220).pack(expand=True)

        info = ctk.CTkFrame(c, fg_color="transparent")
        info.pack(fill="both", expand=True, padx=14, pady=10)

        ctk.CTkLabel(info, text=f"{i + 1:02d} / {p.categoria.upper()}", font=(MONO, 10), text_color=CINZA, anchor="w").pack(fill="x")
        ctk.CTkLabel(info, text=p.nome.upper(), font=(SANS, 13, "bold"), text_color=BRANCO, anchor="w", justify="left", wraplength=270).pack(fill="x")

        linha = ctk.CTkFrame(info, fg_color="transparent")
        linha.pack(fill="x", pady=(4, 0))

        ctk.CTkLabel(linha, text=moeda(p.preco), font=(SANS, 20, "bold"), text_color=BRANCO).pack(side="left")
        ctk.CTkLabel(linha, text="ESGOTADO" if p.esgotado else f"{p.quantidade} UN", font=(MONO, 10), text_color=VERDE if p.quantidade <= 3 else CINZA).pack(side="right", anchor="s")

        b = botao(info, "Comprar" if not p.esgotado else "Esgotado", lambda: self.tela_compra(p), primario=not p.esgotado, largura=280, altura=34)
        b.pack(fill="x", pady=(8, 0))
        if p.esgotado:
            b.configure(state="disabled")

    def tela_compra(self, p):
        self.limpar()
        self.cabecalho()

        ctk.CTkButton(self, text="← VOLTAR À LOJA", command=self.tela_loja, fg_color="transparent", hover_color=LINHA, text_color=BRANCO, corner_radius=0, anchor="w", font=(MONO, 12, "bold"), width=200).pack(anchor="w", padx=28, pady=12)

        corpo = ctk.CTkFrame(self, fg_color=PRETO, corner_radius=0)
        corpo.pack(fill="both", expand=True)

        esquerda = ctk.CTkFrame(corpo, fg_color=PRETO, corner_radius=0, width=440)
        esquerda.pack(side="left", fill="y")
        esquerda.pack_propagate(False)

        moldura = ctk.CTkFrame(esquerda, fg_color=FUNDO_IMG, corner_radius=0, width=380, height=340)
        moldura.pack(padx=28, pady=20)
        moldura.pack_propagate(False)

        imagem(moldura, p.imagem, 340).pack(expand=True)

        ctk.CTkLabel(esquerda, text=p.categoria.upper(), font=(MONO, 11), text_color=CINZA, anchor="w").pack(fill="x", padx=28)
        ctk.CTkLabel(esquerda, text=p.nome.upper(), font=(SANS, 24, "bold"), text_color=BRANCO, anchor="w", justify="left", wraplength=380).pack(fill="x", padx=28)
        ctk.CTkLabel(esquerda, text=moeda(p.preco), font=(SANS, 34, "bold"), text_color=BRANCO, anchor="w").pack(fill="x", padx=28, pady=(6, 0))
        ctk.CTkLabel(esquerda, text=f"ESTOQUE: {p.quantidade} UN  ·  GARANTIA: {p.garantia_meses} MESES", font=(MONO, 11), text_color=CINZA, anchor="w").pack(fill="x", padx=28)
        ctk.CTkLabel(esquerda, text=p.descricao_tecnica(), font=(MONO, 11), text_color=BRANCO, anchor="w", justify="left", wraplength=380).pack(fill="x", padx=28, pady=(10, 0))

        form = ctk.CTkFrame(corpo, fg_color="transparent")
        form.pack(side="left", fill="both", expand=True, padx=40, pady=20)

        ctk.CTkLabel(form, text="FINALIZAR COMPRA", font=(SANS, 30, "bold"), text_color=BRANCO, anchor="w").pack(fill="x")

        legenda(form, "Forma de pagamento")

        self.pagamento = menu(form, PAGAMENTOS)
        self.pagamento.pack(fill="x", padx=4)

        legenda(form, "Endereço de entrega")

        linha_cep = ctk.CTkFrame(form, fg_color="transparent")
        linha_cep.pack(fill="x")

        botao(linha_cep, "Buscar CEP", self.buscar_cep, primario=False, largura=130).pack(side="right", anchor="s", padx=4, pady=4)

        self.e_cep = campo(linha_cep, "CEP", "00000-000", lado="left")
        self.e_rua = campo(form, "Rua", "Ex: Av. Paulista")

        linha_n = ctk.CTkFrame(form, fg_color="transparent")
        linha_n.pack(fill="x")

        self.e_num = campo(linha_n, "Número", "123", lado="left")
        self.e_bairro = campo(linha_n, "Bairro", "Ex: Centro", lado="left")
        self.e_comp = campo(form, "Complemento (opcional)", "Apto, bloco, casa...")

        linha_c = ctk.CTkFrame(form, fg_color="transparent")
        linha_c.pack(fill="x")

        self.e_cidade = campo(linha_c, "Cidade", "Ex: São Paulo", lado="left")
        self.e_uf = campo(linha_c, "UF", "SP", lado="left")

        self.msg = ctk.CTkLabel(form, text="", text_color=VERDE, font=(MONO, 12), anchor="w", justify="left", wraplength=400)
        self.msg.pack(fill="x", pady=(10, 0))

        total = ctk.CTkFrame(form, fg_color="transparent", corner_radius=0, border_width=1, border_color=LINHA)
        total.pack(fill="x", pady=(8, 0))

        ctk.CTkLabel(total, text="TOTAL", font=(MONO, 12), text_color=CINZA).pack(side="left", padx=16, pady=12)
        ctk.CTkLabel(total, text=moeda(p.preco), font=(SANS, 22, "bold"), text_color=VERDE).pack(side="right", padx=16)

        botao(form, "Confirmar pedido", lambda: self.finalizar(p)).pack(fill="x", pady=(12, 0))

    def buscar_cep(self):
        try:
            dados = Endereco.buscar_cep(self.e_cep.get())
        except ValueError as erro:
            self.msg.configure(text=str(erro), text_color=VERDE)
            return
        for entrada, chave in [(self.e_rua, "rua"), (self.e_bairro, "bairro"),(self.e_cidade, "cidade"), (self.e_uf, "uf")]:
            entrada.delete(0, "end")
            entrada.insert(0, dados[chave])
        self.msg.configure(text="ENDEREÇO ENCONTRADO. CONFIRA E DIGITE O NÚMERO.", text_color=BRANCO)

    def finalizar(self, p):
        endereco = Endereco(self.e_cep.get(), self.e_rua.get(), self.e_num.get(), self.e_bairro.get(), self.e_cidade.get(), self.e_uf.get(), self.e_comp.get())
        if not endereco.valido:
            self.msg.configure(text="PREENCHA CEP (8 NÚMEROS), RUA, NÚMERO, BAIRRO, CIDADE E UF (2 LETRAS).", text_color=VERDE)
            return

        try:
            self.banco.registrar_compra(self.usuario, p, self.pagamento.get(), endereco)
        except ValueError as erro:
            self.msg.configure(text=str(erro), text_color=VERDE)
            return

        messagebox.showinfo("Compra feita", f"{p.nome}\nPagamento: {self.pagamento.get()}\nEntrega: {endereco}")
        self.tela_loja()

    def tela_admin(self):
        self.limpar()
        self.cabecalho()
        self.caminho = None
        corpo = ctk.CTkFrame(self, fg_color=PRETO, corner_radius=0)
        corpo.pack(fill="both", expand=True)

        form = ctk.CTkFrame(corpo, fg_color=PRETO, corner_radius=0, width=380)
        form.pack(side="left", fill="y")
        form.pack_propagate(False)
        f = ctk.CTkFrame(form, fg_color="transparent")
        f.pack(fill="both", expand=True, padx=28, pady=28)
        ctk.CTkLabel(f, text="NOVO PRODUTO", font=(SANS, 26, "bold"), text_color=BRANCO, anchor="w").pack(fill="x")
        self.e_nome = campo(f, "Nome", "Ex: Placa-mãe B550")
        legenda(f, "Categoria")
        self.e_cat = menu(f, LISTA_CATEGORIAS)
        self.e_cat.pack(fill="x", padx=4)
        self.e_preco = campo(f, "Preço", "0.00")
        self.e_qtd = campo(f, "Quantidade", "0")
        self.lbl_img = ctk.CTkLabel(f, text="NENHUMA IMAGEM", font=(MONO, 11), text_color=CINZA, anchor="w")
        self.lbl_img.pack(fill="x", padx=4, pady=(10, 0))
        botao(f, "Escolher imagem", self.escolher_imagem, primario=False).pack(fill="x", pady=(6, 0))
        botao(f, "Salvar produto", self.salvar).pack(fill="x", pady=(10, 0))
        self.msg = ctk.CTkLabel(f, text="", text_color=VERDE, font=(MONO, 12), anchor="w", wraplength=300, justify="left")
        self.msg.pack(fill="x", pady=(10, 0))

        lista = ctk.CTkFrame(corpo, fg_color=PRETO, corner_radius=0)
        lista.pack(side="left", fill="both", expand=True, padx=28, pady=28)
        ctk.CTkLabel(lista, text="PRODUTOS CADASTRADOS", font=(SANS, 26, "bold"), text_color=BRANCO, anchor="w").pack(fill="x", pady=(0, 10))
        self.quadro_lista = lista
        self.atualizar_lista()

    def escolher_imagem(self):
        self.caminho = filedialog.askopenfilename(
            filetypes=[("Imagens", "*.png *.jpg *.jpeg *.gif *.bmp *.webp")]) or None
        if self.caminho:
            self.lbl_img.configure(text=os.path.basename(self.caminho).upper(), text_color=BRANCO)

    def salvar(self):
        try:
            preco = float(self.e_preco.get().replace(",", "."))
            qtd = int(self.e_qtd.get())
        except ValueError:
            self.msg.configure(text="PREÇO E QUANTIDADE PRECISAM SER NÚMEROS.")
            return

        try:
            produto = criar_produto(self.e_cat.get(), nome=self.e_nome.get(), preco=preco, quantidade=qtd)
        except ValueError as erro:
            self.msg.configure(text=str(erro))
            return

        if self.caminho:
            destino = os.path.join("imagens", os.path.basename(self.caminho))
            if os.path.abspath(self.caminho) != os.path.abspath(destino):
                shutil.copy(self.caminho, destino)
            produto.imagem = destino
        self.banco.cadastrar_produto(produto)
        messagebox.showinfo("Pronto", "Produto salvo!")
        self.tela_admin()

    def atualizar_lista(self):
        if hasattr(self, "rolagem"):
            self.rolagem.destroy()
        self.rolagem = ctk.CTkScrollableFrame(self.quadro_lista, fg_color=PRETO, corner_radius=0)
        self.rolagem.pack(fill="both", expand=True)
        for p in self.banco.listar_produtos(ordem="categoria"):
            linha = ctk.CTkFrame(self.rolagem, fg_color=PRETO, corner_radius=0, border_width=1, border_color=LINHA)
            linha.pack(fill="x")

            mini = ctk.CTkFrame(linha, fg_color=FUNDO_IMG, corner_radius=0, width=64, height=64)
            mini.pack(side="left", padx=12, pady=12)
            mini.pack_propagate(False)

            imagem(mini, p.imagem, 60).pack(expand=True)

            ctk.CTkLabel(linha, text=f"{p.categoria.upper()}\n{p.nome.upper()}\n{moeda(p.preco)}  ·  {p.quantidade} UN", font=(MONO, 12), text_color=BRANCO, justify="left", anchor="w").pack(side="left", padx=8, fill="x", expand=True)

            botao(linha, "Remover", lambda i=p.id, n=p.nome: self.remover(i, n), primario=False, largura=100, altura=36).pack(side="right", padx=12)

    def remover(self, id_, nome):
        if messagebox.askyesno("Remover", f"Remover {nome}?"):
            self.banco.remover_produto(id_)
            self.atualizar_lista()


if __name__ == "__main__":
    App().mainloop()
