// CLIENTE: só cuida da tela. Todos os dados vêm do servidor pela API REST.
const API = window.API_URL.replace(/\/$/, "");
let livros = [];
let carrinho = {}; // livro_id -> quantidade (fica só no navegador)

const $ = (id) => document.getElementById(id);
const reais = (v) => "R$ " + v.toFixed(2).replace(".", ",");
const esc = (t) => String(t).replace(/[&<>"']/g, (c) => `&#${c.charCodeAt(0)};`);

async function api(caminho, opcoes = {}) {
  const resp = await fetch(API + caminho, {
    headers: { "Content-Type": "application/json" },
    ...opcoes,
  });
  const dados = await resp.json();
  if (!resp.ok) throw new Error(dados.erro || "Erro no servidor.");
  return dados;
}

function mostrar(texto, erro = false) {
  const m = $("mensagem");
  m.textContent = texto;
  m.className = erro ? "msg erro" : "msg";
  m.hidden = false;
}

async function carregarLivros() {
  livros = await api("/api/livros");
  $("livros").innerHTML = livros.map((l) => `
    <tr>
      <td>${l.id}</td><td>${esc(l.titulo)}</td><td>${esc(l.autor)}</td>
      <td>${reais(l.preco)}</td><td>${l.estoque}</td>
      <td><button onclick="adicionar(${l.id})" ${l.estoque === 0 ? "disabled" : ""}>+ Carrinho</button></td>
    </tr>`).join("");
}

function adicionar(id) {
  const livro = livros.find((l) => l.id === id);
  if ((carrinho[id] || 0) + 1 > livro.estoque) return mostrar("Não há mais unidades em estoque.", true);
  carrinho[id] = (carrinho[id] || 0) + 1;
  desenharCarrinho();
}

function desenharCarrinho() {
  const itens = Object.entries(carrinho).map(([id, qtd]) => ({ livro: livros.find((l) => l.id == id), qtd }));
  if (!itens.length) return ($("carrinho").innerHTML = "<p>Carrinho vazio.</p>");
  const total = itens.reduce((s, i) => s + i.livro.preco * i.qtd, 0);
  $("carrinho").innerHTML = `
    <table>
      <tr><th>Livro</th><th>Qtd</th><th>Subtotal</th></tr>
      ${itens.map((i) => `<tr><td>${esc(i.livro.titulo)}</td><td>${i.qtd}</td><td>${reais(i.livro.preco * i.qtd)}</td></tr>`).join("")}
    </table>
    <p class="total">Total: ${reais(total)}</p>
    <button type="button" onclick="carrinho = {}; desenharCarrinho()">Esvaziar carrinho</button>`;
}

async function carregarPedidos() {
  const pedidos = await api("/api/pedidos");
  $("pedidos").innerHTML = pedidos.length
    ? `<table><tr><th>#</th><th>Cliente</th><th>Itens</th><th>Pagamento</th><th>Total</th></tr>
       ${pedidos.map((p) => `<tr><td>${p.id}</td><td>${esc(p.cliente)}</td>
         <td>${p.itens.map((i) => `${i.quantidade}× ${esc(i.titulo)}`).join(", ")}</td>
         <td>${p.metodo === "pix" ? "PIX" : "Cartão"}</td><td>${reais(p.total)}</td></tr>`).join("")}</table>`
    : "<p>Nenhum pedido ainda.</p>";
}

$("form-livro").addEventListener("submit", async (e) => {
  e.preventDefault();
  const f = Object.fromEntries(new FormData(e.target));
  try {
    const livro = await api("/api/livros", { method: "POST", body: JSON.stringify(f) });
    mostrar(`Livro “${livro.titulo}” cadastrado.`);
    e.target.reset();
    await carregarLivros();
  } catch (err) { mostrar(err.message, true); }
});

$("form-pedido").addEventListener("submit", async (e) => {
  e.preventDefault();
  const f = Object.fromEntries(new FormData(e.target));
  const itens = Object.entries(carrinho).map(([livro_id, quantidade]) => ({ livro_id: +livro_id, quantidade }));
  try {
    const pedido = await api("/api/pedidos", { method: "POST", body: JSON.stringify({ ...f, itens }) });
    mostrar(`Pedido #${pedido.id} aprovado: ${reais(pedido.total)}` +
      (pedido.codigo_pix ? ` · PIX: ${pedido.codigo_pix}` : ""));
    carrinho = {};
    await Promise.all([carregarLivros(), carregarPedidos()]);
    desenharCarrinho();
  } catch (err) { mostrar(err.message, true); }
});

$("url-servidor").textContent = API;
Promise.all([carregarLivros(), carregarPedidos()])
  .then(desenharCarrinho)
  .catch(() => mostrar("Não foi possível conectar ao servidor em " + API, true));
