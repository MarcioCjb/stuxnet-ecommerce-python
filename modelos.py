# Camada de modelos (Apenas classes Python)

import json
import urllib.request
from abc import ABC, abstractmethod

PAGAMENTOS = ["Pix", "Cartão de crédito", "Boleto"]


class Produto(ABC):
    """Classe abstrata: não dá para criar um Produto "genérico"."""

    categoria = ""        
    garantia_meses = 12 

    def __init__(self, id, nome, preco, quantidade, imagem=""):
        nome = str(nome).strip()
        if not nome or preco < 0 or quantidade < 0:
            raise ValueError("DIGITE O NOME. PREÇO E QUANTIDADE NÃO PODEM SER NEGATIVOS.")
        self.id = id
        self.nome = nome
        self.preco = float(preco)
        self.quantidade = int(quantidade)
        self.imagem = imagem

    @abstractmethod
    def descricao_tecnica(self):
        """Texto explicando o produto. Cada categoria escreve o seu (polimorfismo)."""

    @property
    def esgotado(self):
        return self.quantidade <= 0


class PlacaMae(Produto):
    categoria = "Placas mãe"

    def descricao_tecnica(self):
        return "Base do computador: conecta processador, memória e demais componentes."


class MemoriaRAM(Produto):
    categoria = "Memória RAM"

    def descricao_tecnica(self):
        return "Memória de acesso rápido: quanto mais, mais programas rodam ao mesmo tempo."


class Armazenamento(Produto):
    categoria = "Armazenamento"

    def descricao_tecnica(self):
        return "Guarda o sistema e seus arquivos. SSDs são bem mais rápidos que HDs."


class Refrigeracao(Produto):
    categoria = "Refrigeração"
    garantia_meses = 6

    def descricao_tecnica(self):
        return "Mantém o processador na temperatura certa para não perder desempenho."


class Monitor(Produto):
    categoria = "Monitores"

    def descricao_tecnica(self):
        return "Tela do computador: confira o tamanho, a resolução e a taxa de atualização."


class Periferico(Produto):
    categoria = "Periféricos"
    garantia_meses = 6

    def descricao_tecnica(self):
        return "Itens de entrada e saída: teclado, mouse, headset e afins."


CATEGORIAS = {c.categoria: c for c in (PlacaMae, MemoriaRAM, Armazenamento, Refrigeracao, Monitor, Periferico)}


def criar_produto(categoria, id=None, nome="", preco=0.0, quantidade=0, imagem=""):
    """Devolve a subclasse certa de Produto para a categoria informada."""
    if categoria not in CATEGORIAS:
        raise ValueError(f"CATEGORIA DESCONHECIDA: {categoria}")
    return CATEGORIAS[categoria](id, nome, preco, quantidade, imagem)


class Usuario(ABC):
    tipo = ""
    def __init__(self, nome):
        self.nome = nome

    @abstractmethod
    def rotulo(self):
        """Texto mostrado no cabeçalho."""

    @abstractmethod
    def tela_inicial(self):
        """Qual tela abrir depois do login ("loja" ou "admin")."""


class Cliente(Usuario):
    tipo = "cliente"

    def rotulo(self):
        return self.nome.upper()

    def tela_inicial(self):
        return "loja"


class Administrador(Usuario):
    tipo = "admin"

    def rotulo(self):
        return "ADMIN"

    def tela_inicial(self):
        return "admin"


def criar_usuario(nome, tipo):
    return (Administrador if tipo == "admin" else Cliente)(nome)


class Endereco:
    def __init__(self, cep, rua, numero, bairro, cidade, uf, complemento=""):
        self.cep = "".join(c for c in cep if c.isdigit())
        self.rua = rua.strip()
        self.numero = numero.strip()
        self.bairro = bairro.strip()
        self.cidade = cidade.strip()
        self.uf = uf.strip().upper()
        self.complemento = complemento.strip()

    @property
    def valido(self):
        return (len(self.cep) == 8 and len(self.uf) == 2
                and all([self.rua, self.numero, self.bairro, self.cidade]))

    def __str__(self):
        comp = f" - {self.complemento}" if self.complemento else ""
        return (f"{self.rua}, {self.numero}{comp} - {self.bairro}, "
                f"{self.cidade}/{self.uf} - CEP {self.cep}")

    @staticmethod
    def buscar_cep(cep):
        """Consulta o ViaCEP. Devolve um dict com rua, bairro, cidade e uf."""
        cep = "".join(c for c in cep if c.isdigit())
        if len(cep) != 8:
            raise ValueError("DIGITE O CEP COM 8 NÚMEROS.")
        try:
            with urllib.request.urlopen(f"https://viacep.com.br/ws/{cep}/json/", timeout=5) as r:
                dados = json.load(r)
            if dados.get("erro"):
                raise ValueError
        except Exception:
            raise ValueError("CEP NÃO ENCONTRADO OU SEM INTERNET. PREENCHA À MÃO.")
        return {"rua": dados.get("logradouro", ""), "bairro": dados.get("bairro", ""),
                "cidade": dados.get("localidade", ""), "uf": dados.get("uf", "")}
