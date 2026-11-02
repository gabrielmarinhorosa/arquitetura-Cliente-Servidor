"""SERVIÇO DE ESTOQUE / PEDIDOS (no diagrama: PostgreSQL; aqui, em memória).

Usa o catálogo para pegar o preço oficial e o pagamento para cobrar.
"""
import catalogo
import pagamento
from catalogo import ErroValidacao

ESTOQUE_INICIAL = {1: 5, 2: 3, 3: 8, 4: 2}
METODOS = ("pix", "cartao")

_estoque = {}   # livro_id -> quantidade
_pedidos = []


def carregar_iniciais():
    _estoque.clear()
    _estoque.update(ESTOQUE_INICIAL)
    _pedidos.clear()


def consultar_estoque(livro_id):
    return _estoque.get(livro_id, 0)


def definir_estoque(livro_id, quantidade):
    try:
        quantidade = int(quantidade)
    except (TypeError, ValueError):
        raise ErroValidacao("Estoque inválido.")
    if quantidade < 0:
        raise ErroValidacao("Estoque não pode ser negativo.")
    _estoque[livro_id] = quantidade


def listar_pedidos():
    return list(reversed(_pedidos))


def criar_pedido(cliente, itens, metodo):
    cliente = (cliente or "").strip()
    if not cliente:
        raise ErroValidacao("Informe o nome do cliente.")
    if metodo not in METODOS:
        raise ErroValidacao("Forma de pagamento inválida (use 'pix' ou 'cartao').")
    if not itens:
        raise ErroValidacao("Carrinho vazio.")

    # Junta itens repetidos e confere catálogo e estoque antes de mexer em qualquer coisa.
    quantidades = {}
    try:
        for item in itens:
            livro_id = int(item["livro_id"])
            quantidades[livro_id] = quantidades.get(livro_id, 0) + int(item["quantidade"])
    except (TypeError, KeyError, ValueError):
        raise ErroValidacao("Itens inválidos.")

    linhas = []
    for livro_id, qtd in quantidades.items():
        livro = catalogo.obter(livro_id)
        if livro is None:
            raise ErroValidacao(f"Livro {livro_id} não encontrado.", 404)
        if qtd <= 0:
            raise ErroValidacao("Quantidade deve ser maior que zero.")
        if consultar_estoque(livro_id) < qtd:
            raise ErroValidacao(f"Estoque insuficiente para “{livro['titulo']}”.", 409)
        linhas.append({"livro_id": livro_id, "titulo": livro["titulo"],
                       "preco": livro["preco"], "quantidade": qtd})
    total = round(sum(l["preco"] * l["quantidade"] for l in linhas), 2)

    cobranca = pagamento.cobrar(total, metodo)
    if not cobranca["aprovado"]:
        raise ErroValidacao("Pagamento recusado.", 402)

    for l in linhas:
        _estoque[l["livro_id"]] -= l["quantidade"]

    pedido = {"id": len(_pedidos) + 1, "cliente": cliente, "itens": linhas, "total": total,
              "metodo": metodo, "transacao_id": cobranca["transacao_id"],
              "codigo_pix": cobranca["codigo_pix"]}
    _pedidos.append(pedido)
    return pedido
