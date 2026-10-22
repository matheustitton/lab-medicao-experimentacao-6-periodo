"""RQ06: fatores associados ao desempenho DORA (Kruskal-Wallis, ε², Holm, Cliff's delta).

Fatores: linguagem principal, popularidade (quartis de estrelas), contribuidores (quartis) e
idade (quartis). O fator "tipo do projeto" só entra se existir a coluna `tipo_projeto` no CSV
(vem do consenso da validação manual).

Uso: python -m analise.rq06 [--csv ...] [--saida ...]
"""
from itertools import combinations
from typing import Dict, List, Optional

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.multitest import multipletests

from . import comum

METRICAS_RQ06 = ["freq_deploy_semana", "lead_time_a_h", "lead_time_b_h", "cfr_ci", "cfr_entrega",
                 "recuperacao_h"]
MIN_GRUPO_LINGUAGEM = 15


def agrupar_linguagem(serie: pd.Series, minimo: int = MIN_GRUPO_LINGUAGEM) -> pd.Series:
    """Linguagens com menos de `minimo` repositórios viram 'Outras' (evita grupos minúsculos)."""
    contagem = serie.value_counts()
    grandes = set(contagem[contagem >= minimo].index)
    return serie.fillna("Sem linguagem").map(lambda v: v if v in grandes else "Outras")


def fatores(df: pd.DataFrame) -> Dict[str, pd.Series]:
    f = {
        "linguagem": agrupar_linguagem(df["linguagem"]),
        "popularidade (estrelas)": comum.quartis(df["estrelas"]),
        "contribuidores": comum.quartis(df["contribuidores"]),
        "idade do repositório": comum.quartis(df["idade_dias"]),
    }
    if "tipo_projeto" in df.columns and df["tipo_projeto"].notna().any():
        f["tipo do projeto"] = df["tipo_projeto"]
    return f


def anexar_tipo_projeto(df: pd.DataFrame, consenso: pd.DataFrame) -> pd.DataFrame:
    """Junta o `tipo_projeto` de consenso (só existe para a amostra-ouro) ao dataset."""
    c = consenso[(consenso["nivel"] == "repos") & (consenso["dimensao"] == "tipo_projeto")]
    return df.merge(c[["chave", "consenso"]].rename(columns={"chave": "repo", "consenso": "tipo_projeto"}),
                    on="repo", how="left")


def kruskal(df: pd.DataFrame, grupo: pd.Series, metrica: str) -> Optional[Dict[str, float]]:
    d = pd.DataFrame({"g": grupo, "y": df[metrica]}).dropna()
    amostras = [g["y"].to_numpy() for _, g in d.groupby("g") if len(g) >= 2]
    if len(amostras) < 2:
        return None
    if len(amostras) == 2:
        u = stats.mannwhitneyu(amostras[0], amostras[1], alternative="two-sided")
        delta = comum.cliffs_delta(amostras[0], amostras[1])
        return {"teste": "Mann-Whitney", "estatistica": float(u.statistic), "p_valor": float(u.pvalue),
                "efeito": delta, "tipo_efeito": "Cliff δ", "n": len(d), "grupos": 2}
    h = stats.kruskal(*amostras)
    return {"teste": "Kruskal-Wallis", "estatistica": float(h.statistic), "p_valor": float(h.pvalue),
            "efeito": comum.epsilon_quadrado(float(h.statistic), len(d)), "tipo_efeito": "ε²",
            "n": len(d), "grupos": len(amostras)}


def testes_principais(df: pd.DataFrame) -> pd.DataFrame:
    linhas: List[dict] = []
    for fator, grupo in fatores(df).items():
        for m in METRICAS_RQ06:
            r = kruskal(df, grupo, m)
            if r:
                linhas.append({"fator": fator, "metrica": comum.METRICAS[m][0], **r})
    t = pd.DataFrame(linhas)
    t["p_holm"] = multipletests(t["p_valor"], method="holm")[1]
    t["significativo_holm"] = t["p_holm"] < 0.05
    t["magnitude"] = [comum.interpretar_epsilon(e) if te == "ε²" else comum.interpretar_delta(e)
                      for e, te in zip(t["efeito"], t["tipo_efeito"])]
    return t


def extremos(df: pd.DataFrame) -> pd.DataFrame:
    """Pós-teste dos fatores numéricos: Q4 contra Q1 (Mann-Whitney, Cliff's delta, Holm)."""
    linhas: List[dict] = []
    for fator, grupo in fatores(df).items():
        if fator in ("linguagem", "tipo do projeto"):
            continue
        for m in METRICAS_RQ06:
            d = pd.DataFrame({"g": grupo, "y": df[m]}).dropna()
            q1, q4 = d[d.g == "Q1"]["y"], d[d.g == "Q4"]["y"]
            if len(q1) < 2 or len(q4) < 2:
                continue
            u = stats.mannwhitneyu(q4, q1, alternative="two-sided")
            delta = comum.cliffs_delta(q4, q1)
            linhas.append({"fator": fator, "metrica": comum.METRICAS[m][0], "n_Q1": len(q1),
                           "n_Q4": len(q4), "mediana_Q1": float(q1.median()),
                           "mediana_Q4": float(q4.median()), "p_valor": float(u.pvalue),
                           "cliff_delta_Q4_vs_Q1": delta, "magnitude": comum.interpretar_delta(delta)})
    t = pd.DataFrame(linhas)
    t["p_holm"] = multipletests(t["p_valor"], method="holm")[1]
    t["significativo_holm"] = t["p_holm"] < 0.05
    return t


def robustez_idade(df: pd.DataFrame, corte_dias: int = 365) -> pd.DataFrame:
    """A idade limita o lead time de repositórios jovens (um commit não pode ser mais antigo que o
    repositório). Compara o Spearman idade × métrica com todos os repositórios e só com os mais
    velhos que `corte_dias`."""
    linhas = []
    for m in METRICAS_RQ06:
        linha = {"metrica": comum.METRICAS[m][0]}
        for nome, sub in (("todos", df), (f"idade >= {corte_dias} dias", df[df["idade_dias"] >= corte_dias])):
            d = sub[["idade_dias", m]].dropna()
            rho, p = stats.spearmanr(d["idade_dias"], d[m]) if len(d) > 2 else (float("nan"), float("nan"))
            linha[f"n ({nome})"], linha[f"rho ({nome})"], linha[f"p ({nome})"] = len(d), float(rho), float(p)
        linhas.append(linha)
    return pd.DataFrame(linhas)


def medianas_por_grupo(df: pd.DataFrame) -> pd.DataFrame:
    linhas = []
    for fator, grupo in fatores(df).items():
        for g, sub in df.groupby(grupo):
            linha = {"fator": fator, "grupo": g, "n": len(sub)}
            for m in METRICAS_RQ06:
                linha[comum.METRICAS[m][0]] = sub[m].median()
            linhas.append(linha)
    return pd.DataFrame(linhas)


def grafico(df: pd.DataFrame, saida: str) -> None:
    plt, caminho = comum.figura(saida, "rq06_contribuidores_frequencia")
    g = comum.quartis(df["contribuidores"])
    ordem = sorted(g.dropna().unique())
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.boxplot([df.loc[g == q, "freq_deploy_semana"].dropna() for q in ordem], tick_labels=ordem,
               showfliers=False)
    ax.set_yscale("log")
    ax.set_xlabel("quartil de contribuidores")
    ax.set_ylabel("releases/semana (escala log)")
    fig.tight_layout()
    fig.savefig(caminho, dpi=150)
    plt.close(fig)


def main(argv=None) -> None:
    import argparse
    import os
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--csv", default=comum.CSV_PADRAO)
    ap.add_argument("--saida", default=comum.SAIDA_PADRAO)
    ap.add_argument("--consenso", default="rotulos/consenso.csv")
    args = ap.parse_args(argv)
    df = comum.carregar(args.csv)
    if os.path.exists(args.consenso):
        df = anexar_tipo_projeto(df, pd.read_csv(args.consenso, dtype=str))
    t = testes_principais(df)
    comum.salvar(t, args.saida, "rq06_testes", casas=3)
    comum.salvar(extremos(df), args.saida, "rq06_extremos_q4_q1", casas=3)
    comum.salvar(medianas_por_grupo(df), args.saida, "rq06_medianas_por_grupo", casas=2)
    comum.salvar(robustez_idade(df), args.saida, "rq06_robustez_idade", casas=3)
    grafico(df, args.saida)
    print(f"{len(t)} testes; {int(t['significativo_holm'].sum())} significativos após Holm")


if __name__ == "__main__":
    main()
