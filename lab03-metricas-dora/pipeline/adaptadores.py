"""Contrato do JSON de coleta -> objetos de domínio (metricas.modelos).

Formato salvo por repositório em RepoStore.coleta:
{
  "meta": {repo, estrelas, linguagem, criado_em, default_branch, contribuidores},
  "releases": [{tag, publicada_em, prerelease, anterior_tag, status_compare,
                total_commits, commits: [{sha, data, msg, merge}]}],
  "runs": [{workflow_id, conclusao, iniciada_em, atualizada_em}],   # só success/failure
  "runs_ignorados": int,
  "teto_runs_atingido": bool
}
"""
from typing import Any, Dict, List

from metricas.modelos import Commit, Execucao, Release
from metricas.tempo import parse_data


def releases_de_coleta(coleta: Dict[str, Any]) -> List[Release]:
    saida = []
    for r in coleta["releases"]:
        commits = tuple(
            Commit(c["sha"], parse_data(c["data"]), c.get("msg", ""))
            for c in r.get("commits", []) if c.get("data")
        )
        saida.append(Release(
            tag=r["tag"], publicada_em=parse_data(r["publicada_em"]),
            anterior_tag=r.get("anterior_tag"), commits=commits,
            status_compare=r.get("status_compare", "ok"), prerelease=r.get("prerelease", False),
        ))
    return saida


def execucoes_de_coleta(coleta: Dict[str, Any]) -> List[Execucao]:
    return [
        Execucao(r["workflow_id"], r["conclusao"], parse_data(r["iniciada_em"]),
                 parse_data(r["atualizada_em"]))
        for r in coleta["runs"]
    ]
