"""Consolida as coletas em dados/saida/dataset_dora.csv (uma linha por repositório)."""
import os
from typing import Any, Dict

import pandas as pd

from metricas.cfr import cfr_ci
from metricas.cfr_entrega import cfr_entrega
from metricas.classificacao import classificar_repositorio
from metricas.frequencia import frequencia_deploys
from metricas.heuristica import obter_heuristica
from metricas.lead_time import lead_time_repo
from metricas.recuperacao import tempo_recuperacao
from metricas.tempo import parse_data

from .adaptadores import execucoes_de_coleta, releases_de_coleta
from .config import Config, Janela
from .dicionario import COLUNAS, DICIONARIO
from .estado import RepoStore, funil_markdown


def linha_dataset(coleta: Dict[str, Any], janela: Janela, heuristica: str = "v1",
                  dias_corretiva: int = 7) -> Dict[str, Any]:
    meta = coleta["meta"]
    releases = releases_de_coleta(coleta)
    execs = execucoes_de_coleta(coleta)
    freq = frequencia_deploys(releases, janela.inicio, janela.fim)
    lt = lead_time_repo(releases)
    ci = cfr_ci(execs)
    ce = cfr_entrega(releases, janela.fim, obter_heuristica(heuristica), dias_corretiva)
    rc = tempo_recuperacao(execs, janela.fim)
    cls = classificar_repositorio(freq, lt.a_mediana_h, ci.taxa, rc.mediana_h)
    return {
        "repo": meta["repo"], "estrelas": meta["estrelas"], "linguagem": meta.get("linguagem"),
        "criado_em": meta["criado_em"],
        "idade_dias": (janela.fim - parse_data(meta["criado_em"])).days,
        "contribuidores": meta.get("contribuidores"), "default_branch": meta["default_branch"],
        "n_releases": sum(1 for r in releases if not r.prerelease),
        "freq_deploy_semana": freq,
        "n_releases_lead": lt.n_releases_usadas, "n_releases_sem_anterior": lt.n_sem_anterior,
        "n_releases_indisponiveis": lt.n_indisponiveis, "n_releases_sem_commits": lt.n_sem_commits,
        "n_commits_lead": lt.n_commits, "n_lead_negativos": lt.n_negativos,
        "lead_time_a_h": lt.a_mediana_h, "lead_time_b_h": lt.b_mediana_h,
        "n_runs_sucesso": ci.sucessos, "n_runs_falha": ci.falhas,
        "n_runs_ignorados": coleta.get("runs_ignorados", 0),
        "teto_runs_atingido": coleta.get("teto_runs_atingido", False),
        "cfr_ci": ci.taxa,
        "n_releases_avaliadas": ce.avaliadas, "n_releases_falha": ce.falhas,
        "n_releases_censuradas": ce.censuradas, "heuristica_versao": heuristica,
        "cfr_entrega": ce.taxa,
        "n_episodios": rc.n_episodios, "n_episodios_censurados": rc.n_censurados,
        "prop_episodios_censurados": rc.prop_censurados,
        "recuperacao_h": rc.mediana_h, "recuperacao_h_c_censura": rc.mediana_h_com_censura,
        "cls_freq": cls.por_metrica["frequencia"], "cls_lead_a": cls.por_metrica["lead_time"],
        "cls_cfr_ci": cls.por_metrica["cfr"], "cls_recuperacao": cls.por_metrica["recuperacao"],
        "classe_dora_c1": cls.geral,
    }


def gerar_dataset(store: RepoStore, cfg: Config) -> pd.DataFrame:
    linhas = [linha_dataset(c, cfg.janela, cfg.heuristica, cfg.janela_corretiva_dias)
              for _, c in store.incluidos()]
    df = pd.DataFrame(linhas, columns=COLUNAS)
    os.makedirs(cfg.saida_dir, exist_ok=True)
    df.to_csv(os.path.join(cfg.saida_dir, "dataset_dora.csv"), index=False)
    pd.DataFrame(DICIONARIO, columns=["coluna", "tipo", "unidade", "origem_formula", "rq"]).to_csv(
        os.path.join(cfg.saida_dir, "dicionario_dados.csv"), index=False)
    with open(os.path.join(cfg.saida_dir, "funil_selecao.md"), "w", encoding="utf-8") as f:
        f.write(funil_markdown(store) + "\n")
    return df
