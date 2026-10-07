"""Coleta de releases e dos commits entre releases consecutivas (RQ01 e RQ02)."""
from typing import Any, Dict, List
from urllib.parse import quote

from .config import Janela
from .github_client import ClienteGitHub, ErroAPI
from metricas.tempo import parse_data


def _reduzir_releases(dados: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [{k: r.get(k) for k in ("tag_name", "draft", "prerelease", "published_at")} for r in dados]


def _reduzir_compare(dados: Dict[str, Any]) -> Dict[str, Any]:
    commits = []
    for c in dados.get("commits", []):
        info = c.get("commit", {})
        autor = info.get("author") or info.get("committer") or {}
        commits.append({
            "sha": c["sha"],
            "data": autor.get("date"),
            "msg": (info.get("message") or "").splitlines()[0][:200] if info.get("message") else "",
            "merge": len(c.get("parents", [])) > 1,
        })
    return {"total_commits": dados.get("total_commits", len(commits)), "commits": commits}


def coletar_releases(client: ClienteGitHub, repo: str, janela: Janela, max_paginas: int = 10) -> List[Dict[str, Any]]:
    """Releases publicadas (draft=false) DENTRO da janela, em ordem cronológica.
    Cada release principal leva `anterior_tag` (a release principal anterior,
    mesmo que fora da janela). Pré-releases ficam marcadas e sem anterior."""
    brutas = client.paginar(f"/repos/{repo}/releases", reduzir=_reduzir_releases, max_paginas=max_paginas)
    todas = [
        {"tag": r["tag_name"], "publicada_em": r["published_at"], "prerelease": bool(r["prerelease"])}
        for r in brutas if not r.get("draft") and r.get("published_at")
    ]
    todas.sort(key=lambda r: parse_data(r["publicada_em"]))
    anterior = None
    for r in todas:
        if r["prerelease"]:
            r["anterior_tag"] = None
        else:
            r["anterior_tag"] = anterior
            anterior = r["tag"]
    return [r for r in todas if janela.contem(parse_data(r["publicada_em"]))]


def coletar_commits(client: ClienteGitHub, repo: str, release: Dict[str, Any], max_paginas: int = 30) -> Dict[str, Any]:
    """Commits de `anterior...release` com paginação (o compare corta em 250 sem ela)."""
    vazio = {"total_commits": 0, "commits": []}
    if release["prerelease"]:
        return {"status_compare": "nao_coletado", **vazio}
    if not release["anterior_tag"]:
        return {"status_compare": "sem_anterior", **vazio}
    base, topo = quote(release["anterior_tag"], safe="/"), quote(release["tag"], safe="/")
    caminho = f"/repos/{repo}/compare/{base}...{topo}"
    commits: List[Dict[str, Any]] = []
    total = 0
    pagina = 0
    try:
        while pagina < max_paginas:
            pagina += 1
            resp = client.get(caminho, {"per_page": 100, "page": pagina}, reduzir=_reduzir_compare)
            if resp.status != 200:
                if pagina == 1:
                    return {"status_compare": "indisponivel", **vazio}
                break
            total = resp.dados["total_commits"]
            commits += resp.dados["commits"]
            if len(commits) >= total or not resp.dados["commits"]:
                break
    except ErroAPI as e:
        if e.status == 422:       # tag reescrita / sem ancestral comum
            return {"status_compare": "indisponivel", **vazio}
        raise
    status = "ok" if len(commits) >= total else "truncado"
    return {"status_compare": status, "total_commits": total, "commits": commits}


def coletar_releases_com_commits(client: ClienteGitHub, repo: str, janela: Janela,
                                 max_paginas_releases: int = 10, max_paginas_compare: int = 30):
    releases = coletar_releases(client, repo, janela, max_paginas_releases)
    for r in releases:
        r.update(coletar_commits(client, repo, r, max_paginas_compare))
    return releases
