import pytest

from app import criar_app


@pytest.fixture
def api():
    app = criar_app()  # recarrega os dados iniciais
    app.testing = True
    return app.test_client()


def test_lista_livros_com_estoque(api):
    livros = api.get("/api/livros").get_json()
    assert len(livros) == 4 and livros[0]["estoque"] == 5


def test_cadastra_livro(api):
    r = api.post("/api/livros", json={"titulo": "Iracema", "autor": "José de Alencar", "preco": 19.9, "estoque": 3})
    assert r.status_code == 201 and r.get_json()["estoque"] == 3
    assert api.post("/api/livros", json={"titulo": "", "autor": "X", "preco": 1}).status_code == 400


def test_pedido_baixa_estoque(api):
    r = api.post("/api/pedidos", json={"cliente": "Ana", "metodo": "pix",
                                       "itens": [{"livro_id": 1, "quantidade": 2}]})
    assert r.status_code == 201
    assert r.get_json()["total"] == 59.80 and r.get_json()["codigo_pix"]
    assert api.get("/api/livros").get_json()[0]["estoque"] == 3
    assert len(api.get("/api/pedidos").get_json()) == 1


def test_pedido_sem_estoque_nao_baixa_nada(api):
    r = api.post("/api/pedidos", json={"cliente": "Ana", "metodo": "cartao",
                                       "itens": [{"livro_id": 1, "quantidade": 1}, {"livro_id": 4, "quantidade": 99}]})
    assert r.status_code == 409
    assert api.get("/api/livros").get_json()[0]["estoque"] == 5


def test_cors(api):
    assert api.get("/api/livros").headers["Access-Control-Allow-Origin"] == "*"
