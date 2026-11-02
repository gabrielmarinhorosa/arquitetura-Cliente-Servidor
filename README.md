# Livraria — Arquitetura Cliente-Servidor (Exercícios 8.5 e 8.6)

MVP da livraria na arquitetura **cliente-servidor** do Exercício 8.1.
Cliente e servidor são **dois projetos separados**, rodam em endereços diferentes
e só conversam por HTTP/JSON.

```
arquitetura-cliente-servidor/
├── cliente/               # FRONT-END: HTML + JavaScript, sem regra de negócio
│   ├── index.html
│   ├── app.js             # chama a API com fetch()
│   └── config.js          # URL do servidor
└── servidor/              # BACK-END: API REST em Flask, sem tela
    ├── app.py             # rotas (papel do API Gateway / BFF)
    ├── catalogo.py        # serviço de catálogo   (MongoDB no diagrama)
    ├── pedidos.py         # serviço de estoque/pedidos (PostgreSQL no diagrama)
    ├── pagamento.py       # pagamento simulado (nanosserviço + Gateway PIX no diagrama)
    └── test_api.py
```

Os dados ficam em memória no servidor, então voltam ao estado inicial quando ele reinicia.

## API

| Método | Rota | O que faz |
|---|---|---|
| GET | `/api/livros` | lista livros com estoque |
| POST | `/api/livros` | cadastra livro `{titulo, autor, preco, estoque}` |
| GET | `/api/pedidos` | lista pedidos |
| POST | `/api/pedidos` | cria pedido `{cliente, metodo: "pix"\|"cartao", itens: [{livro_id, quantidade}]}` |

## Como rodar localmente

Servidor (terminal 1):
```bash
cd servidor
pip install -r requirements.txt
python app.py              # http://127.0.0.1:5000
```

Cliente (terminal 2):
```bash
cd cliente
python -m http.server 8000 # http://127.0.0.1:8000
```

Testes do servidor: `cd servidor && pip install pytest && pytest`

## Deploy (Exercício 8.6)

**Servidor** — Render › New › Web Service, apontando para este repositório:
- Root Directory: `servidor`
- Build: `pip install -r requirements.txt`
- Start: `gunicorn app:app`

**Cliente** — troque a URL em `cliente/config.js` pela URL do servidor publicado e faça
commit. Depois, Render › New › Static Site:
- Root Directory: `cliente`
- Publish Directory: `.`

(Também funciona no GitHub Pages ou na Vercel, por ser só HTML/JS.)

Opcional: no servidor, defina a variável `CORS_ORIGIN` com a URL do cliente para
aceitar chamadas só dele.
