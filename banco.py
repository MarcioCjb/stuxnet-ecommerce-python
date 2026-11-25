# Camada de dados (SQL)

import hashlib
import sqlite3

from modelos import criar_produto, criar_usuario


def criptografar(texto):
    return hashlib.sha256(texto.encode()).hexdigest()


class Banco:
    def __init__(self, caminho="loja.db"):
        self.con = sqlite3.connect(caminho)
        self.criar_tabelas()

    def criar_tabelas(self):
        con = self.con
        con.execute("CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY, usuario TEXT UNIQUE, senha TEXT, tipo TEXT)")
        con.execute("CREATE TABLE IF NOT EXISTS produtos (id INTEGER PRIMARY KEY, nome TEXT, categoria TEXT, preco REAL, quantidade INTEGER, imagem TEXT)")
        con.execute("CREATE TABLE IF NOT EXISTS compras (id INTEGER PRIMARY KEY, usuario TEXT, produto TEXT, preco REAL, pagamento TEXT, endereco TEXT)")
        for coluna in ["cep", "rua", "numero", "bairro", "complemento", "cidade", "uf"]:
            try:
                con.execute(f"ALTER TABLE compras ADD COLUMN {coluna} TEXT")
            except sqlite3.OperationalError:
                pass
        con.execute("INSERT OR IGNORE INTO usuarios (usuario, senha, tipo) VALUES ('admin', ?, 'admin')",
                    (criptografar("admin"),))
        con.commit()

    def autenticar(self, usuario, senha):
        """Devolve um Cliente/Administrador, ou None se usuário ou senha estiverem errados."""
        linha = self.con.execute("SELECT usuario, tipo FROM usuarios WHERE usuario=? AND senha=?",
                                 (usuario.strip(), criptografar(senha))).fetchone()
        return criar_usuario(linha[0], linha[1]) if linha else None

    def cadastrar_usuario(self, usuario, senha):
        usuario = usuario.strip()
        if not usuario or not senha:
            raise ValueError("PREENCHA USUÁRIO E SENHA.")
        try:
            self.con.execute("INSERT INTO usuarios (usuario, senha, tipo) VALUES (?, ?, 'cliente')",
                             (usuario, criptografar(senha)))
            self.con.commit()
        except sqlite3.IntegrityError:
            raise ValueError("ESSE USUÁRIO JÁ EXISTE.")

    @staticmethod
    def _para_objeto(linha):
        id_, nome, categoria, preco, quantidade, imagem = linha
        return criar_produto(categoria, id_, nome, preco, quantidade, imagem or "")

    def listar_produtos(self, busca="", categoria="Todas", ordem="nome"):
        sql = "SELECT id, nome, categoria, preco, quantidade, imagem FROM produtos WHERE LOWER(nome) LIKE ?"
        params = [f"%{busca.strip().lower()}%"]
        if categoria != "Todas":
            sql += " AND categoria = ?"
            params.append(categoria)
        sql += " ORDER BY " + {"nome": "nome", "categoria": "categoria, nome"}.get(ordem, "nome")
        return [self._para_objeto(l) for l in self.con.execute(sql, params).fetchall()]

    def cadastrar_produto(self, produto):
        self.con.execute("INSERT INTO produtos (nome, categoria, preco, quantidade, imagem) VALUES (?, ?, ?, ?, ?)",
                         (produto.nome, produto.categoria, produto.preco, produto.quantidade, produto.imagem))
        self.con.commit()

    def remover_produto(self, produto_id):
        self.con.execute("DELETE FROM produtos WHERE id=?", (produto_id,))
        self.con.commit()

    def registrar_compra(self, usuario, produto, pagamento, endereco):
        """Baixa 1 unidade do estoque e grava a compra, tudo ou nada."""
        with self.con:
            baixa = self.con.execute(
                "UPDATE produtos SET quantidade = quantidade - 1 WHERE id=? AND quantidade > 0",
                (produto.id,))
            if baixa.rowcount == 0:
                raise ValueError("PRODUTO ESGOTADO.")
            preco = self.con.execute("SELECT preco FROM produtos WHERE id=?", (produto.id,)).fetchone()[0]
            self.con.execute(
                """INSERT INTO compras (usuario, produto, preco, pagamento, endereco,
                   cep, rua, numero, bairro, complemento, cidade, uf)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (usuario.nome, produto.nome, preco, pagamento, str(endereco),
                 endereco.cep, endereco.rua, endereco.numero, endereco.bairro,
                 endereco.complemento, endereco.cidade, endereco.uf))
