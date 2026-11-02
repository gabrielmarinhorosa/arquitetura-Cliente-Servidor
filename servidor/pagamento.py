"""SERVIÇO DE PAGAMENTO — simula o nanosserviço que fala com o Gateway PIX.

Num sistema real, aqui seria feita a chamada HTTPS ao provedor de pagamento.
Nesta versão toda cobrança é aprovada.
"""
import uuid


def cobrar(valor, metodo):
    transacao = uuid.uuid4().hex[:10].upper()
    codigo_pix = f"PIX-SIMULADO-{transacao}-{valor:.2f}" if metodo == "pix" else None
    return {"aprovado": True, "transacao_id": transacao, "codigo_pix": codigo_pix}
