"""SERVIÇO DE CATÁLOGO — livros (no diagrama: MongoDB; aqui, em memória)."""
_livros = {}

LIVROS_INICIAIS = [
    ("Dom Casmurro", "Machado de Assis", 29.90),
    ("O Cortiço", "Aluísio Azevedo", 24.50),
    ("Vidas Secas", "Graciliano Ramos", 34.90),
    ("A Hora da Estrela", "Clarice Lispector", 27.00),
]


class ErroValidacao(Exception):
    def __init__(self, mensagem, status=400):
        super().__init__(mensagem)
        self.status = status


def carregar_iniciais():
    _livros.clear()
    for titulo, autor, preco in LIVROS_INICIAIS:
        cadastrar(titulo, autor, preco)


def listar():
    return [dict(l) for l in _livros.values()]


def obter(livro_id):
    livro = _livros.get(livro_id)
    return dict(livro) if livro else None


def cadastrar(titulo, autor, preco):
    titulo, autor = (titulo or "").strip(), (autor or "").strip()
    if not titulo or not autor:
        raise ErroValidacao("Título e autor são obrigatórios.")
    try:
        preco = round(float(preco), 2)
    except (TypeError, ValueError):
        raise ErroValidacao("Preço inválido.")
    if preco < 0:
        raise ErroValidacao("Preço não pode ser negativo.")
    novo_id = max(_livros, default=0) + 1
    _livros[novo_id] = {"id": novo_id, "titulo": titulo, "autor": autor, "preco": preco}
    return dict(_livros[novo_id])
