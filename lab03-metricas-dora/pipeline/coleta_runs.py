"""Coleta de workflow runs do default branch (event=push), fatiando a janela por mês."""
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Tuple

from .config import Janela
from .github_client import ClienteGitHub
from metricas.cfr import classificar_conclusao

FMT = "%Y-%m-%dT%H:%M:%SZ"
TETO_API = 1000       # a API não devolve mais que 1.000 runs por consulta com filtros


def _reduzir_runs(dados: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "total_count": dados.get("total_count", 0),
        "workflow_runs": [
            {"workflow_id": r["workflow_id"], "conclusao": r.get("conclusion"),
             "iniciada_em": r.get("run_started_at") or r["created_at"],
             "atualizada_em": r["updated_at"]}
            for r in dados.get("workflow_runs", [])
        ],
    }


def _intervalo(ini: datetime, fim: datetime) -> str:
    return f"{ini.strftime(FMT)}..{fim.strftime(FMT)}"


def fatiar_mensal(janela: Janela) -> List[Tuple[datetime, datetime]]:
    """[(início, fim)] por mês-calendário, sem sobreposição, cobrindo a janela inteira."""
    fatias, ini = [], janela.inicio
    while ini <= janela.fim:
        prox = (ini.replace(day=28) + timedelta(days=4)).replace(day=1, hour=0, minute=0, second=0)
        fim = min(prox - timedelta(seconds=1), janela.fim)
        fatias.append((ini, fim))
        ini = prox
    return fatias


def _params(branch: str, ini: datetime, fim: datetime) -> Dict[str, Any]:
    return {"branch": branch, "event": "push", "created": _intervalo(ini, fim)}


def contar_runs_janela(client: ClienteGitHub, repo: str, branch: str, janela: Janela) -> int:
    """Limite superior barato (1 chamada): total de runs, incluindo os que serão ignorados."""
    r = client.get(f"/repos/{repo}/actions/runs", {**_params(branch, janela.inicio, janela.fim), "per_page": 1})
    return (r.dados or {}).get("total_count", 0) if r.status == 200 else 0


def _coletar_intervalo(client, repo, branch, ini, fim, acc: Dict[str, Any]) -> None:
    caminho = f"/repos/{repo}/actions/runs"
    params = {**_params(branch, ini, fim), "per_page": 100}
    primeira = client.get(caminho, params, reduzir=_reduzir_runs)
    if primeira.status != 200:
        return
    total = primeira.dados["total_count"]
    if total >= TETO_API and (fim - ini) > timedelta(hours=1):
        meio = (ini + (fim - ini) / 2).replace(microsecond=0)
        _coletar_intervalo(client, repo, branch, ini, meio - timedelta(seconds=1), acc)
        _coletar_intervalo(client, repo, branch, meio, fim, acc)
        return
    if total >= TETO_API:
        acc["teto"] = True
    for run in client.paginar(caminho, params, chave="workflow_runs", reduzir=_reduzir_runs):
        if classificar_conclusao(run["conclusao"]) is None:
            acc["ignorados"] += 1
        else:
            acc["runs"].append(run)


def coletar_runs(client: ClienteGitHub, repo: str, branch: str, janela: Janela):
    """Retorna (runs válidos, nº de runs ignorados, teto_da_api_atingido)."""
    acc: Dict[str, Any] = {"runs": [], "ignorados": 0, "teto": False}
    for ini, fim in fatiar_mensal(janela):
        _coletar_intervalo(client, repo, branch, ini, fim, acc)
    return acc["runs"], acc["ignorados"], acc["teto"]
