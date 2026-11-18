# Código Principal

import os
import json
import shutil
import sqlite3
import hashlib
import urllib.request
from tkinter import filedialog, messagebox
import customtkinter as ctk
from PIL import Image

PRETO, BRANCO, LINHA, VERDE = "#0D0D0D", "#F4F4F0", "#262626", "#C8FF00"
VERDE_ESCURO, CINZA, FUNDO_IMG = "#516800", "#8A8A85", "#161616"
SANS, MONO = "Syne", "DejaVu Sans Mono"
CATEGORIAS = ["Placas mãe", "Memória RAM", "Armazenamento", "Refrigeração", "Monitores", "Periféricos"]
PAGAMENTOS = ["Pix", "Cartão de crédito", "Boleto"]
REFS = []

ctk.set_appearance_mode("dark")
os.makedirs("imagens", exist_ok=True)


def criptografar(texto):
    return hashlib.sha256(texto.encode()).hexdigest()


def moeda(valor):
    return "R$ " + f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

 
con = sqlite3.connect("loja.db")
con.execute("CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY, usuario TEXT UNIQUE, senha TEXT, tipo TEXT)")
con.execute("CREATE TABLE IF NOT EXISTS produtos (id INTEGER PRIMARY KEY, nome TEXT, categoria TEXT, preco REAL, quantidade INTEGER, imagem TEXT)")
con.execute("CREATE TABLE IF NOT EXISTS compras (id INTEGER PRIMARY KEY, usuario TEXT, produto TEXT, preco REAL, pagamento TEXT, endereco TEXT)")

for coluna in ["cep", "rua", "numero", "bairro", "complemento", "cidade", "uf"]:
    try:
        con.execute(f"ALTER TABLE compras ADD COLUMN {coluna} TEXT")
    except sqlite3.OperationalError:
        pass

con.execute("INSERT OR IGNORE INTO usuarios (usuario, senha, tipo) VALUES ('admin', ?, 'admin')", (criptografar("admin"),))
con.commit() 


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
            quem = "ADMIN" if self.usuario["tipo"] == "admin" else self.usuario["usuario"].upper()
            ctk.CTkLabel(topo, text=f"USUÁRIO: {quem}", font=(MONO, 11), text_color=CINZA).pack(side="right")
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
        linha = con.execute("SELECT usuario, tipo FROM usuarios WHERE usuario=? AND senha=?", (self.e_user.get().strip(), criptografar(self.e_senha.get()))).fetchone()
        if not linha:
            self.msg.configure(text="USUÁRIO OU SENHA INCORRETOS.")
            return
        
        self.usuario = {"usuario": linha[0], "tipo": linha[1]}
        self.tela_admin() if linha[1] == "admin" else self.tela_loja()

    def fazer_cadastro(self):
        user, senha = self.e_user.get().strip(), self.e_senha.get()
        if not user or not senha:
            self.msg.configure(text="PREENCHA USUÁRIO E SENHA.")
            return
        try:
            con.execute("INSERT INTO usuarios (usuario, senha, tipo) VALUES (?, ?, 'cliente')", (user, criptografar(senha)))
            con.commit()
        except sqlite3.IntegrityError:
            self.msg.configure(text="ESSE USUÁRIO JÁ EXISTE.")
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

        for cat in ["Todas"] + CATEGORIAS:
            ctk.CTkRadioButton(filtros, text=cat.upper(), variable=self.var_cat, value=cat, command=self.mostrar_produtos, font=(MONO, 12), text_color=BRANCO, fg_color=VERDE, hover_color=VERDE_ESCURO, border_color=CINZA, corner_radius=0).pack(anchor="w", pady=5)

        self.area = ctk.CTkScrollableFrame(corpo, fg_color=PRETO, corner_radius=0)
        self.area.pack(side="left", fill="both", expand=True)
        self.mostrar_produtos()

    def mostrar_produtos(self):
        self.area.destroy()
        self.area = ctk.CTkScrollableFrame(self.corpo, fg_color=PRETO, corner_radius=0)
        self.area.pack(side="left", fill="both", expand=True)
        
        sql = "SELECT id, nome, categoria, preco, quantidade, imagem FROM produtos WHERE LOWER(nome) LIKE ?"
        params = [f"%{self.busca.get().strip().lower()}%"]
        
        if self.var_cat.get() != "Todas":
            sql += " AND categoria = ?"
            params.append(self.var_cat.get())
        produtos = con.execute(sql + " ORDER BY nome", params).fetchall()

        if not produtos:
            ctk.CTkLabel(self.area, text="NENHUM PRODUTO ENCONTRADO.", font=(MONO, 13), text_color=CINZA).pack(pady=60)
        for i, p in enumerate(produtos):
            self.card(p, i)

    def card(self, p, i):
        id_, nome, cat, preco, qtd, img = p
        c = ctk.CTkFrame(self.area, fg_color=PRETO, corner_radius=0, border_width=1, border_color=LINHA, width=300, height=375)
        c.grid(row=i // 3, column=i % 3, sticky="nsew")
        c.pack_propagate(False)

        moldura = ctk.CTkFrame(c, fg_color=FUNDO_IMG, corner_radius=0, width=300, height=240)
        moldura.pack(fill="x")
        moldura.pack_propagate(False)

        imagem(moldura, img, 220).pack(expand=True)

        info = ctk.CTkFrame(c, fg_color="transparent")
        info.pack(fill="both", expand=True, padx=14, pady=10)
        
        ctk.CTkLabel(info, text=f"{i + 1:02d} / {cat.upper()}", font=(MONO, 10), text_color=CINZA, anchor="w").pack(fill="x")
        ctk.CTkLabel(info, text=nome.upper(), font=(SANS, 13, "bold"), text_color=BRANCO, anchor="w", justify="left", wraplength=270).pack(fill="x")

        linha = ctk.CTkFrame(info, fg_color="transparent")
        linha.pack(fill="x", pady=(4, 0))

        ctk.CTkLabel(linha, text=moeda(preco), font=(SANS, 20, "bold"), text_color=BRANCO).pack(side="left")
        ctk.CTkLabel(linha, text="ESGOTADO" if qtd <= 0 else f"{qtd} UN", font=(MONO, 10), text_color=VERDE if qtd <= 3 else CINZA).pack(side="right", anchor="s")

        b = botao(info, "Comprar" if qtd > 0 else "Esgotado", lambda: self.tela_compra(p), primario=qtd > 0, largura=280, altura=34)
        b.pack(fill="x", pady=(8, 0))
        if qtd <= 0:
            b.configure(state="disabled")

    def tela_compra(self, p):
        id_, nome, cat, preco, qtd, img = p
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

        imagem(moldura, img, 340).pack(expand=True)

        ctk.CTkLabel(esquerda, text=cat.upper(), font=(MONO, 11), text_color=CINZA, anchor="w").pack(fill="x", padx=28)
        ctk.CTkLabel(esquerda, text=nome.upper(), font=(SANS, 24, "bold"), text_color=BRANCO, anchor="w", justify="left", wraplength=380).pack(fill="x", padx=28)
        ctk.CTkLabel(esquerda, text=moeda(preco), font=(SANS, 34, "bold"), text_color=BRANCO, anchor="w").pack(fill="x", padx=28, pady=(6, 0))
        ctk.CTkLabel(esquerda, text=f"ESTOQUE: {qtd} UN", font=(MONO, 11), text_color=CINZA, anchor="w").pack(fill="x", padx=28)

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
        ctk.CTkLabel(total, text=moeda(preco), font=(SANS, 22, "bold"), text_color=VERDE).pack(side="right", padx=16)
        
        botao(form, "Confirmar pedido", lambda: self.finalizar(p)).pack(fill="x", pady=(12, 0))

    def buscar_cep(self):
        cep = "".join(c for c in self.e_cep.get() if c.isdigit())
        if len(cep) != 8:
            self.msg.configure(text="DIGITE O CEP COM 8 NÚMEROS.")
            return
        try:
            with urllib.request.urlopen(f"https://viacep.com.br/ws/{cep}/json/", timeout=5) as r:
                dados = json.load(r)
            if dados.get("erro"):
                raise ValueError
        except Exception:
            self.msg.configure(text="CEP NÃO ENCONTRADO OU SEM INTERNET. PREENCHA À MÃO.")
            return
        for entrada, chave in [(self.e_rua, "logradouro"), (self.e_bairro, "bairro"),
                               (self.e_cidade, "localidade"), (self.e_uf, "uf")]:
            entrada.delete(0, "end")
            entrada.insert(0, dados.get(chave, ""))
        self.msg.configure(text="ENDEREÇO ENCONTRADO. CONFIRA E DIGITE O NÚMERO.", text_color=BRANCO)

    def finalizar(self, p):
        id_, nome, cat, preco, qtd, img = p
        cep = "".join(c for c in self.e_cep.get() if c.isdigit())
        rua, numero, bairro, comp, cidade = (e.get().strip() for e in
                                             (self.e_rua, self.e_num, self.e_bairro, self.e_comp, self.e_cidade))
        uf = self.e_uf.get().strip().upper()
        if len(cep) != 8 or not all([rua, numero, bairro, cidade]) or len(uf) != 2:
            self.msg.configure(text="PREENCHA CEP (8 NÚMEROS), RUA, NÚMERO, BAIRRO, CIDADE E UF (2 LETRAS).")
            return
        atual = con.execute("SELECT quantidade FROM produtos WHERE id=?", (id_,)).fetchone()
        if not atual or atual[0] <= 0:
            self.msg.configure(text="PRODUTO ESGOTADO.")
            return

        endereco = f"{rua}, {numero}" + (f" - {comp}" if comp else "") + f" - {bairro}, {cidade}/{uf} - CEP {cep}"
        con.execute("UPDATE produtos SET quantidade = quantidade - 1 WHERE id=?", (id_,))
        con.execute("""INSERT INTO compras (usuario, produto, preco, pagamento, endereco,
                       cep, rua, numero, bairro, complemento, cidade, uf)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (self.usuario["usuario"], nome, preco, self.pagamento.get(), endereco,
                     cep, rua, numero, bairro, comp, cidade, uf))
        con.commit()
        messagebox.showinfo("Compra feita", f"{nome}\nPagamento: {self.pagamento.get()}\nEntrega: {endereco}")
        self.tela_loja()

    # ---------- painel do admin ----------
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
        ctk.CTkLabel(f, text="NOVO PRODUTO", font=(SANS, 26, "bold"), text_color=BRANCO,
                     anchor="w").pack(fill="x")
        self.e_nome = campo(f, "Nome", "Ex: Placa-mãe B550")
        legenda(f, "Categoria")
        self.e_cat = menu(f, CATEGORIAS)
        self.e_cat.pack(fill="x", padx=4)
        self.e_preco = campo(f, "Preço", "0.00")
        self.e_qtd = campo(f, "Quantidade", "0")
        self.lbl_img = ctk.CTkLabel(f, text="NENHUMA IMAGEM", font=(MONO, 11), text_color=CINZA, anchor="w")
        self.lbl_img.pack(fill="x", padx=4, pady=(10, 0))
        botao(f, "Escolher imagem", self.escolher_imagem, primario=False).pack(fill="x", pady=(6, 0))
        botao(f, "Salvar produto", self.salvar).pack(fill="x", pady=(10, 0))
        self.msg = ctk.CTkLabel(f, text="", text_color=VERDE, font=(MONO, 12), anchor="w",
                                wraplength=300, justify="left")
        self.msg.pack(fill="x", pady=(10, 0))

        lista = ctk.CTkFrame(corpo, fg_color=PRETO, corner_radius=0)
        lista.pack(side="left", fill="both", expand=True, padx=28, pady=28)
        ctk.CTkLabel(lista, text="PRODUTOS CADASTRADOS", font=(SANS, 26, "bold"), text_color=BRANCO,
                     anchor="w").pack(fill="x", pady=(0, 10))
        self.quadro_lista = lista
        self.atualizar_lista()

    def escolher_imagem(self):
        self.caminho = filedialog.askopenfilename(
            filetypes=[("Imagens", "*.png *.jpg *.jpeg *.gif *.bmp *.webp")]) or None
        if self.caminho:
            self.lbl_img.configure(text=os.path.basename(self.caminho).upper(), text_color=BRANCO)

    def salvar(self):
        nome = self.e_nome.get().strip()
        try:
            preco = float(self.e_preco.get().replace(",", "."))
            qtd = int(self.e_qtd.get())
        except ValueError:
            self.msg.configure(text="PREÇO E QUANTIDADE PRECISAM SER NÚMEROS.")
            return
        if not nome or preco < 0 or qtd < 0:
            self.msg.configure(text="DIGITE O NOME. PREÇO E QUANTIDADE NÃO PODEM SER NEGATIVOS.")
            return

        destino = ""
        if self.caminho:
            destino = os.path.join("imagens", os.path.basename(self.caminho))
            if os.path.abspath(self.caminho) != os.path.abspath(destino):
                shutil.copy(self.caminho, destino)
        con.execute("INSERT INTO produtos (nome, categoria, preco, quantidade, imagem) VALUES (?, ?, ?, ?, ?)",
                    (nome, self.e_cat.get(), preco, qtd, destino))
        con.commit()
        messagebox.showinfo("Pronto", "Produto salvo!")
        self.tela_admin()

    def atualizar_lista(self):
        if hasattr(self, "rolagem"):
            self.rolagem.destroy()
        self.rolagem = ctk.CTkScrollableFrame(self.quadro_lista, fg_color=PRETO, corner_radius=0)
        self.rolagem.pack(fill="both", expand=True)
        produtos = con.execute("SELECT id, nome, categoria, preco, quantidade, imagem FROM produtos "
                               "ORDER BY categoria, nome").fetchall()
        for id_, nome, cat, preco, qtd, img in produtos:
            linha = ctk.CTkFrame(self.rolagem, fg_color=PRETO, corner_radius=0, border_width=1, border_color=LINHA)
            linha.pack(fill="x")

            mini = ctk.CTkFrame(linha, fg_color=FUNDO_IMG, corner_radius=0, width=64, height=64)
            mini.pack(side="left", padx=12, pady=12)
            mini.pack_propagate(False)

            imagem(mini, img, 60).pack(expand=True)

            ctk.CTkLabel(linha, text=f"{cat.upper()}\n{nome.upper()}\n{moeda(preco)}  ·  {qtd} UN",
                         font=(MONO, 12), text_color=BRANCO, justify="left", anchor="w").pack(side="left", padx=8, fill="x", expand=True)

            botao(linha, "Remover", lambda i=id_, n=nome: self.remover(i, n), primario=False, largura=100, altura=36).pack(side="right", padx=12)

    def remover(self, id_, nome):
        if messagebox.askyesno("Remover", f"Remover {nome}?"):
            con.execute("DELETE FROM produtos WHERE id=?", (id_,))
            con.commit()
            self.atualizar_lista()


if __name__ == "__main__":
    App().mainloop()