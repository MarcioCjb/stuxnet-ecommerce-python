# STUXNET

E-commerce de hardware em Python (POO) com CustomTkinter e SQLite.

## Como rodar

```bash
pip install customtkinter pillow
python estoque_ex.py   # (opcional) produtos de exemplo
python loja.py
```

Login de administrador: `admin` / `admin`. Clientes se cadastram pela tela de login.

## Arquitetura (3 camadas)

| Arquivo | Camada | O que tem |
|---|---|---|
| `modelos.py` | Modelos / negócio | Classes de domínio. Sem tkinter e sem SQL. |
| `banco.py` | Dados (SQLite) | Classe `Banco`: todo o SQL do projeto. |
| `loja.py` | Interface | Telas em CustomTkinter. Sem SQL. |

## Onde está cada conceito de POO

- **Classe abstrata:** `Produto` e `Usuario` (`modelos.py`). Não dá para instanciar diretamente.
- **Herança:** `PlacaMae`, `MemoriaRAM`, `Armazenamento`, `Refrigeracao`, `Monitor` e `Periferico` herdam de `Produto`. `Cliente` e `Administrador` herdam de `Usuario`.
- **Polimorfismo:**
  - `produto.descricao_tecnica()` devolve um texto diferente em cada categoria.
  - `usuario.rotulo()` e `usuario.tela_inicial()` mudam conforme o tipo de usuário (o login abre a tela certa sem `if`).
  - `garantia_meses` é sobrescrito em `Refrigeracao` e `Periferico`.
- **Encapsulamento / validação:** o próprio `Produto` valida nome, preço e quantidade. `Endereco` valida o endereço.
- **Relacionamentos:** `Banco` cria objetos `Produto` e `Usuario` a partir das linhas do banco. A compra liga `Usuario`, `Produto` e `Endereco`.
