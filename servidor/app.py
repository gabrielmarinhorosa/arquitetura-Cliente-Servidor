"""SERVIDOR — API REST da livraria (o "API Gateway / BFF" do diagrama 8.1).

Não tem nenhuma tela: só recebe requisições HTTP do cliente e responde JSON.
"""
import os

from flask import Flask, jsonify, request

import catalogo
import pedidos
from catalogo import ErroValidacao


def criar_app():
    app = Flask(__name__)
    app.json.ensure_ascii = False
    catalogo.carregar_iniciais()
    pedidos.carregar_iniciais()

    # CORS: o cliente roda em outro endereço (outro domínio/porta), então o
    # servidor precisa autorizar o navegador a chamá-lo.
    origem_permitida = os.environ.get("CORS_ORIGIN", "*")

    @app.after_request
    def cors(resposta):
        resposta.headers["Access-Control-Allow-Origin"] = origem_permitida
        resposta.headers["Access-Control-Allow-Headers"] = "Content-Type"
        resposta.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        return resposta

    @app.errorhandler(ErroValidacao)
    def erro(e):
        return jsonify(erro=str(e)), e.status

    @app.get("/")
    def saude():
        return jsonify(servico="livraria-servidor", status="ok")

    @app.get("/api/livros")
    def listar_livros():
        return jsonify([{**l, "estoque": pedidos.consultar_estoque(l["id"])}
                        for l in catalogo.listar()])

    @app.post("/api/livros")
    def cadastrar_livro():
        d = request.get_json(silent=True) or {}
        livro = catalogo.cadastrar(d.get("titulo"), d.get("autor"), d.get("preco"))
        pedidos.definir_estoque(livro["id"], d.get("estoque", 0))
        return jsonify({**livro, "estoque": pedidos.consultar_estoque(livro["id"])}), 201

    @app.get("/api/pedidos")
    def listar_pedidos():
        return jsonify(pedidos.listar_pedidos())

    @app.post("/api/pedidos")
    def criar_pedido():
        d = request.get_json(silent=True) or {}
        return jsonify(pedidos.criar_pedido(d.get("cliente"), d.get("itens"), d.get("metodo"))), 201

    return app


app = criar_app()

if __name__ == "__main__":
    app.run(debug=True, port=int(os.environ.get("PORT", 5000)))
