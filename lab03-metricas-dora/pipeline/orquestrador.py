"""Orquestra o pipeline: seleção -> filtros por etapa -> coleta -> dataset.

Idempotente: o estado de cada repositório (RepoStore) e o cache HTTP permitem
interromper (Ctrl+C, rate limit, queda de rede) e rodar de novo do ponto onde parou.
"""
import logging
from typing import Any, Dict, Optional

from .coleta_releases import coletar_releases, coletar_commits
from .coleta_runs import coletar_runs, contar_runs_janela
from .config import Config
from .estado import RepoStore, funil_markdown
from .github_client import ClienteGitHub, ErroAPI
from .metadados import coletar_metadados
from .selecao import buscar_candidatos, tem_actions

log = logging.getLogger("pipeline")


def processar_repo(cfg: Config, client: ClienteGitHub, store: RepoStore, meta: Dict[str, Any]) -> str:
    """Devolve 'incluido' ou o motivo do descarte."""
    repo, branch = meta["repo"], meta["default_branch"]

    def descartar(motivo: str) -> str:
        store.descartar(repo, motivo)
        return motivo

    if not tem_actions(client, repo):
        return descartar("sem_actions")
    store.avancar(repo, 1)

    releases = coletar_releases(client, repo, cfg.janela, cfg.max_paginas_releases)
    if sum(1 for r in releases if not r["prerelease"]) < cfg.min_releases:
        return descartar("releases_insuficientes")
    store.avancar(repo, 2)

    if contar_runs_janela(client, repo, branch, cfg.janela) < cfg.min_runs:
        return descartar("runs_insuficientes")
    runs, ignorados, teto = coletar_runs(client, repo, branch, cfg.janela)
    if len(runs) < cfg.min_runs:
        return descartar("runs_insuficientes")
    store.avancar(repo, 3)

    for r in releases:
        r.update(coletar_commits(client, repo, r, cfg.max_paginas_compare))
    store.salvar_coleta(repo, {
        "meta": {**meta, **coletar_metadados(client, repo)},
        "releases": releases, "runs": runs,
        "runs_ignorados": ignorados, "teto_runs_atingido": teto,
    })
    return "incluido"


def executar(cfg: Config, client: ClienteGitHub, store: RepoStore,
             etapa: str = "todas", limite: Optional[int] = None) -> None:
    alvo = limite or cfg.alvo_amostra
    if etapa in ("todas", "selecao") and store.total() == 0:
        log.info("buscando candidatos (%d faixas de estrelas)...", len(cfg.faixas_estrelas))
        novos = store.adicionar_candidatos(
            buscar_candidatos(client, cfg.faixas_estrelas, cfg.max_paginas_busca))
        log.info("%d candidatos", novos)
    if etapa in ("todas", "coleta"):
        for meta in store.pendentes(cfg.semente):
            if store.contar_incluidos() >= alvo:
                break
            try:
                resultado = processar_repo(cfg, client, store, meta)
            except ErroAPI as e:      # falha persistente: fica pendente para a próxima execução
                log.error("%s: %s", meta["repo"], e)
                continue
            log.info("%s -> %s (%d/%d)", meta["repo"], resultado, store.contar_incluidos(), alvo)
        if store.contar_incluidos() < alvo:
            log.warning("amostra incompleta: %d/%d. Amplie faixas_estrelas ou rode de novo.",
                        store.contar_incluidos(), alvo)
    if etapa in ("todas", "dataset"):
        from .dataset import gerar_dataset      # import tardio: o dataset é entregue na Sprint 02
        df = gerar_dataset(store, cfg)
        log.info("dataset: %d repositórios\n%s", len(df), funil_markdown(store))
