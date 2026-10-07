"""Metadados extras do repositório (contribuidores). Estrelas/linguagem/idade vêm da busca."""
from typing import Any, Dict

from .github_client import ClienteGitHub, ErroAPI


def coletar_metadados(client: ClienteGitHub, repo: str) -> Dict[str, Any]:
    try:
        n = client.contar(f"/repos/{repo}/contributors", {"anon": "true"})
    except ErroAPI:
        n = None   # lista grande demais para a API (403) - registrar como ausente
    return {"contribuidores": n}
