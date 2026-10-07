"""Precisão, recall e F1 de cada versão da heurística de release corretiva vs. o consenso.

Uso: python -m validacao.avaliacao_heuristica --config config.yaml
Se F1 < 0,70, refine a heurística (metricas/heuristica.py), rode de novo e registre
cada versão e seu F1 em docs/HISTORICO_HEURISTICA.md (exigência do enunciado).
"""
import argparse
import os
from typing import Callable, Dict

import pandas as pd
from sklearn.metrics import precision_recall_fscore_support

from metricas.heuristica import HEURISTICAS
from metricas.modelos import Release
from pipeline.adaptadores import releases_de_coleta
from pipeline.config import carregar_config
from pipeline.estado import RepoStore

META_F1 = 0.70


def metricas_classificacao(y_true, y_pred) -> Dict[str, float]:
    p, r, f1, _ = precision_recall_fscore_support(
        y_true, y_pred, average="binary", pos_label=1, zero_division=0)
    return {"precisao": float(p), "recall": float(r), "f1": float(f1)}


def avaliar(consenso_releases: pd.DataFrame, store: RepoStore,
            heuristicas: Dict[str, Callable[[Release], bool]] = HEURISTICAS) -> pd.DataFrame:
    """consenso_releases: linhas de consenso.csv com nivel=releases, dimensao=corretiva."""
    cache: Dict[str, Dict[str, Release]] = {}
    y_true, itens = [], []
    for _, linha in consenso_releases.iterrows():
        repo, tag = linha["chave"].split("@", 1)
        if repo not in cache:
            cache[repo] = {r.tag: r for r in releases_de_coleta(store.coleta_de(repo))}
        release = cache[repo].get(tag)
        if release is None:
            continue
        itens.append(release)
        y_true.append(1 if linha["consenso"] == "sim" else 0)
    saida = []
    for nome, fn in heuristicas.items():
        y_pred = [1 if fn(r) else 0 for r in itens]
        m = metricas_classificacao(y_true, y_pred)
        saida.append({"versao": nome, "n": len(itens), "positivos_consenso": sum(y_true),
                      "marcadas_heuristica": sum(y_pred), **{k: round(v, 4) for k, v in m.items()},
                      "meta_f1_ok": m["f1"] >= META_F1})
    return pd.DataFrame(saida)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config.yaml")
    args = ap.parse_args()
    cfg = carregar_config(args.config)
    consenso = pd.read_csv(os.path.join(cfg.rotulos_dir, "consenso.csv"), dtype=str)
    consenso = consenso[(consenso.nivel == "releases") & (consenso.dimensao == "corretiva")]
    tabela = avaliar(consenso, RepoStore(cfg.caminho_estado))
    os.makedirs(cfg.saida_dir, exist_ok=True)
    tabela.to_csv(os.path.join(cfg.saida_dir, "avaliacao_heuristica.csv"), index=False)
    print(tabela.to_string(index=False))


if __name__ == "__main__":
    main()
