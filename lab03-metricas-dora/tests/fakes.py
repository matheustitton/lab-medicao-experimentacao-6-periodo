"""Dublê do cliente da API (sem rede)."""
from pipeline.github_client import ClienteGitHub, Resposta, normalizar


class ClienteFalso(ClienteGitHub):
    """Cliente cujo `get` é respondido por uma função handler(caminho, params) ->
    (status, dados) ou (status, dados, links). `paginar`/`contar` reais são reaproveitados."""

    def __init__(self, handler):
        self.handler = handler
        self.chamadas = []

    def get(self, caminho, params=None, reduzir=None):
        caminho, params = normalizar(caminho, params)
        self.chamadas.append((caminho, params))
        status, dados, *resto = self.handler(caminho, params)
        if reduzir is not None and status == 200:
            dados = reduzir(dados)
        return Resposta(status, dados, resto[0] if resto else {})
