"""Seleção de repositórios candidatos (Search API fatiada por estrelas)."""
from typing import Any, Dict, List

from .github_client import ClienteGitHub


def extrair_meta(item: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "repo": item["full_name"],
        "estrelas": item["stargazers_count"],
        "linguagem": item.get("language"),
        "criado_em": item["created_at"],
        "default_branch": item["default_branch"],
    }


def _reduzir_busca(dados: Dict[str, Any]) -> Dict[str, Any]:
    campos = ("full_name", "stargazers_count", "language", "created_at", "default_branch")
    return {"total_count": dados.get("total_count", 0),
            "items": [{k: i.get(k) for k in campos} for i in dados.get("items", [])]}


def montar_consulta(faixa: str) -> str:
    return f"stars:{faixa} fork:false archived:false"


def buscar_candidatos(client: ClienteGitHub, faixas: List[str], max_paginas: int = 10) -> List[Dict[str, Any]]:
    """Uma consulta por faixa de estrelas (cada uma limitada a 1.000 resultados)."""
    vistos: Dict[str, Dict[str, Any]] = {}
    for faixa in faixas:
        itens = client.paginar(
            "/search/repositories",
            {"q": montar_consulta(faixa), "sort": "stars", "order": "desc"},
            chave="items", reduzir=_reduzir_busca, max_paginas=max_paginas,
        )
        for item in itens:
            vistos.setdefault(item["full_name"], extrair_meta(item))
    return list(vistos.values())


def tem_actions(client: ClienteGitHub, repo: str) -> bool:
    r = client.get(f"/repos/{repo}/actions/workflows", {"per_page": 1})
    return r.status == 200 and (r.dados or {}).get("total_count", 0) > 0
