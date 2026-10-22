"""Gera data/saida/dataset_sensibilidade.csv: métricas de cada repositório sob várias definições.

Combinações (RQ07):
  C1  release            | lead time (a) | CFR (a) CI        <- referência
  C2  release+pré-release| lead time (b) | CFR (b) entrega
  C3  release            | lead time (b) | CFR (a) CI        <- substitui a combinação com tags, ver nota
  C4  release            | lead time (a) | CFR (b) entrega

Nota: a coleta não baixou as tags do GitHub, então a combinação "tag" do exemplo do enunciado não
pode ser calculada com estes dados. As pré-releases não têm commits coletados, então só entram
na frequência e na sequência usada pelo CFR (b).

Também calcula o "rework rate" (RQ08) para cada versão de heurística.

Uso: python -m analise.sensibilidade_dataset [--estado data/estado.sqlite] [--config config.yaml]
"""
import argparse
import os
from dataclasses import replace
from typing import Dict, List

import pandas as pd

from metricas.cfr import cfr_ci
from metricas.cfr_entrega import cfr_entrega
from metricas.classificacao import classificar_repositorio
from metricas.frequencia import frequencia_deploys
from metricas.heuristica import HEURISTICAS
from metricas.lead_time import lead_time_repo
from metricas.recuperacao import tempo_recuperacao
from pipeline.adaptadores import execucoes_de_coleta, releases_de_coleta
from pipeline.config import Config, carregar_config
from pipeline.estado import RepoStore


def rework_rate(releases, eh_corretiva) -> Dict[str, float]:
    """RQ08: releases corretivas ÷ releases publicadas (não pré) na janela."""
    principais = [r for r in releases if not r.prerelease]
    n = len(principais)
    corretivas = sum(1 for r in principais if eh_corretiva(r))
    return {"n": n, "corretivas": corretivas, "taxa": corretivas / n if n else None}


def linha_sensibilidade(coleta: dict, cfg: Config) -> Dict[str, object]:
    j = cfg.janela
    releases = releases_de_coleta(coleta)
    execs = execucoes_de_coleta(coleta)
    com_pre = [replace(r, prerelease=False) for r in releases]   # pré-releases passam a contar
    lt = lead_time_repo(releases)
    ci = cfr_ci(execs)
    rc = tempo_recuperacao(execs, j.fim)
    dias = cfg.janela_corretiva_dias
    freq = frequencia_deploys(releases, j.inicio, j.fim)
    freq_pre = frequencia_deploys(com_pre, j.inicio, j.fim)
    linha: Dict[str, object] = {
        "repo": coleta["meta"]["repo"],
        "n_prereleases": sum(1 for r in releases if r.prerelease),
        "freq_release": freq, "freq_release_pre": freq_pre,
        "lead_a_h": lt.a_mediana_h, "lead_b_h": lt.b_mediana_h,
        "cfr_a": ci.taxa, "recuperacao_h": rc.mediana_h,
    }
    cfr_b = {}
    for nome, h in HEURISTICAS.items():
        cfr_b[nome] = cfr_entrega(releases, j.fim, h, dias).taxa
        linha[f"cfr_b_{nome}"] = cfr_b[nome]
        linha[f"cfr_b_pre_{nome}"] = cfr_entrega(com_pre, j.fim, h, dias).taxa
        rw = rework_rate(releases, h)
        linha[f"rework_{nome}"] = rw["taxa"]
        linha[f"n_corretivas_{nome}"] = rw["corretivas"]
    v = cfg.heuristica
    combos = {
        "C1": (freq, lt.a_mediana_h, ci.taxa),
        "C2": (freq_pre, lt.b_mediana_h, linha[f"cfr_b_pre_{v}"]),
        "C3": (freq, lt.b_mediana_h, ci.taxa),
        "C4": (freq, lt.a_mediana_h, cfr_b[v]),
    }
    for nome, (f, lead, cfr) in combos.items():
        linha[f"classe_{nome}"] = classificar_repositorio(f, lead, cfr, rc.mediana_h).geral
    # sensibilidade à heurística, mantendo a combinação C4
    for nome in HEURISTICAS:
        linha[f"classe_C4_{nome}"] = classificar_repositorio(
            freq, lt.a_mediana_h, cfr_b[nome], rc.mediana_h).geral
    return linha


def gerar(store: RepoStore, cfg: Config) -> pd.DataFrame:
    linhas: List[dict] = [linha_sensibilidade(c, cfg) for _, c in store.incluidos()]
    df = pd.DataFrame(linhas)
    os.makedirs(cfg.saida_dir, exist_ok=True)
    df.to_csv(os.path.join(cfg.saida_dir, "dataset_sensibilidade.csv"), index=False)
    return df


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", default="config.yaml")
    args = ap.parse_args(argv)
    cfg = carregar_config(args.config)
    df = gerar(RepoStore(cfg.caminho_estado), cfg)
    print(f"{len(df)} repositórios -> {cfg.saida_dir}/dataset_sensibilidade.csv")


if __name__ == "__main__":
    main()
