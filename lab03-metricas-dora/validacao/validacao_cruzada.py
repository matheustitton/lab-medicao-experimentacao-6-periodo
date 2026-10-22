"""Quanto do F1 da v4/v5 é ajuste aos 300 rótulos? Validação cruzada por repositório (5 dobras).

Em cada dobra, os limiares (releases pequenas, fração de commits de correção, intervalo em dias)
são escolhidos só nos repositórios de treino e aplicados aos repositórios de teste.
Os repositórios nunca aparecem em treino e teste ao mesmo tempo.

Uso: python -m validacao.validacao_cruzada --config config.yaml
"""
import argparse
import itertools
import os
from typing import Dict, List

import numpy as np
import pandas as pd
from sklearn.metrics import precision_recall_fscore_support
from sklearn.model_selection import GroupKFold

from metricas.heuristica import _commits_uteis, eh_patch_bump, n_correcao_util
from pipeline.adaptadores import releases_de_coleta
from pipeline.config import carregar_config
from pipeline.estado import RepoStore

GRADE = list(itertools.product([0, 2, 5], [0.2, 0.3, 0.4, 0.5], [0, 2, 3, 5]))   # pequena, fração, gap (dias)


def atributos(consenso: pd.DataFrame, store: RepoStore) -> pd.DataFrame:
    cache: Dict[str, dict] = {}
    linhas: List[dict] = []
    for _, l in consenso.iterrows():
        repo, tag = l["chave"].split("@", 1)
        if repo not in cache:
            cache[repo] = {r.tag: r for r in releases_de_coleta(store.coleta_de(repo))}
        r = cache[repo].get(tag)
        if r is None:
            continue
        n, corr = len(_commits_uteis(r)), n_correcao_util(r)
        gap = ((r.publicada_em - r.anterior_publicada_em).total_seconds() / 86400
               if r.anterior_publicada_em else np.inf)
        linhas.append({"repo": repo, "y": int(l["consenso"] == "sim"), "patch": int(eh_patch_bump(r)),
                       "n": n, "ncorr": corr, "frac": corr / n if n else 0.0, "gap": gap})
    return pd.DataFrame(linhas)


def regra(x: pd.DataFrame, pequena: int, fracao: float, gap: float) -> np.ndarray:
    base = ((x.patch == 1) & ((x.ncorr >= 1) | (x.n <= pequena))) | ((x.n >= 1) & (x.frac >= fracao))
    return (base | ((x.gap <= gap) & (x.ncorr >= 1))).astype(int).to_numpy()


def f1(y, p) -> float:
    return float(precision_recall_fscore_support(y, p, average="binary", zero_division=0)[2])


def validar(x: pd.DataFrame, dobras: int = 5) -> Dict[str, float]:
    y = x["y"].to_numpy()
    melhor = max(GRADE, key=lambda g: f1(y, regra(x, *g)))
    pred = np.zeros(len(x), dtype=int)
    for tr, te in GroupKFold(n_splits=dobras).split(x, y, x["repo"]):
        g = max(GRADE, key=lambda g: f1(y[tr], regra(x.iloc[tr], *g)))
        pred[te] = regra(x.iloc[te], *g)
    p, r, f, _ = precision_recall_fscore_support(y, pred, average="binary", zero_division=0)
    return {"n": len(x), "f1_no_ajuste": f1(y, regra(x, *melhor)), "pequena": melhor[0],
            "fracao": melhor[1], "gap_dias": melhor[2],
            "cv_precisao": float(p), "cv_recall": float(r), "cv_f1": float(f), "dobras": dobras}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config.yaml")
    args = ap.parse_args()
    cfg = carregar_config(args.config)
    c = pd.read_csv(os.path.join(cfg.rotulos_dir, "consenso.csv"), dtype=str)
    c = c[(c.nivel == "releases") & (c.dimensao == "corretiva")]
    res = validar(atributos(c, RepoStore(cfg.caminho_estado)))
    os.makedirs(cfg.saida_dir, exist_ok=True)
    pd.DataFrame([res]).to_csv(os.path.join(cfg.saida_dir, "validacao_cruzada_heuristica.csv"), index=False)
    print(pd.DataFrame([res]).round(4).to_string(index=False))


if __name__ == "__main__":
    main()
