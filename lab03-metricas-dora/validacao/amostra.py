"""Sorteio da amostra-ouro (60 repositórios, semente fixa) e geração das planilhas de rótulos.

Uso: python -m validacao.amostra --config config.yaml
A amostra final é lida do estado da coleta (data/estado.sqlite).
As planilhas NÃO trazem a saída da heurística (cada avaliador rotula às cegas).
"""
import argparse
import os
import random
from typing import Any, Dict, List

import pandas as pd

from pipeline.config import carregar_config
from pipeline.estado import RepoStore

TIPOS = "biblioteca_framework | aplicacao_servico | cli | outro"
ENTREGAS = "sim | nao | incerto"
CORRETIVA = "sim | nao"


def sortear_repos(dataset: pd.DataFrame, n: int, semente: int) -> List[str]:
    return sorted(dataset.sample(n=n, random_state=semente)["repo"].tolist())


def sortear_releases(coleta: Dict[str, Any], k: int, semente: int, repo: str) -> List[Dict[str, Any]]:
    """k releases principais (com anterior) sorteadas de forma reproduzível."""
    elegiveis = [r for r in coleta["releases"] if not r["prerelease"] and r.get("anterior_tag")]
    rng = random.Random(f"{semente}:{repo}")
    escolhidas = rng.sample(elegiveis, min(k, len(elegiveis)))
    return sorted(escolhidas, key=lambda r: r["publicada_em"])


def gerar_planilhas(store: RepoStore, dataset: pd.DataFrame, avaliadores: List[str],
                    n: int, k: int, semente: int, destino: str) -> None:
    os.makedirs(destino, exist_ok=True)
    repos, linhas_rel = sortear_repos(dataset, n, semente), []
    for repo in repos:
        coleta = store.coleta_de(repo)
        for r in sortear_releases(coleta, k, semente, repo):
            linhas_rel.append({
                "repo": repo, "tag": r["tag"],
                "url_release": f"https://github.com/{repo}/releases/tag/{r['tag']}",
                "url_comparacao": f"https://github.com/{repo}/compare/{r['anterior_tag']}...{r['tag']}",
            })
    base_repos = pd.DataFrame({"repo": repos, "url_repo": [f"https://github.com/{r}" for r in repos]})
    base_rel = pd.DataFrame(linhas_rel)
    base_repos.to_csv(os.path.join(destino, "amostra_ouro_repos.csv"), index=False)
    base_rel.to_csv(os.path.join(destino, "amostra_ouro_releases.csv"), index=False)
    for nome in avaliadores:
        a = base_repos.assign(tipo_projeto="", releases_entregas_reais="")
        b = base_rel.assign(corretiva="")
        a.to_csv(os.path.join(destino, f"rotulos_{nome}_repos.csv"), index=False)
        b.to_csv(os.path.join(destino, f"rotulos_{nome}_releases.csv"), index=False)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config.yaml")
    args = ap.parse_args()
    cfg = carregar_config(args.config)
    store = RepoStore(cfg.caminho_estado)
    repos = [r for r, _ in store.incluidos()]          # a amostra final = repositórios incluídos na coleta
    if len(repos) < cfg.amostra_ouro_n:
        raise SystemExit(f"Só {len(repos)} repositórios coletados; a amostra-ouro precisa de {cfg.amostra_ouro_n}.")
    gerar_planilhas(store, pd.DataFrame({"repo": repos}), cfg.avaliadores,
                    cfg.amostra_ouro_n, cfg.releases_por_repo_ouro, cfg.semente, cfg.rotulos_dir)
    print(f"Planilhas geradas em {cfg.rotulos_dir}/. Valores aceitos:\n"
          f"  tipo_projeto: {TIPOS}\n  releases_entregas_reais: {ENTREGAS}\n  corretiva: {CORRETIVA}")


if __name__ == "__main__":
    main()
