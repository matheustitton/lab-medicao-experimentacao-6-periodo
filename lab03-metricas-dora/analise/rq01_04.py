"""RQ01 a RQ04: estatística descritiva (mediana e IQR), classificação DORA e comparação das variantes.

Uso: python -m analise.rq01_04 [--csv data/saida/dataset_dora.csv] [--saida data/saida/analise]
"""
from typing import Dict

import numpy as np
import pandas as pd
from scipy import stats

from metricas.classificacao import (
    classificar_cfr, classificar_frequencia, classificar_lead_time, classificar_recuperacao)

from . import comum

RQ_DA_METRICA = {"freq_deploy_semana": "RQ01", "lead_time_a_h": "RQ02", "lead_time_b_h": "RQ02",
                 "cfr_ci": "RQ03", "cfr_entrega": "RQ03", "recuperacao_h": "RQ04"}


def descritivas(df: pd.DataFrame) -> pd.DataFrame:
    linhas = []
    for col, (nome, unidade) in comum.METRICAS.items():
        r = comum.resumo(df[col])
        linhas.append({"RQ": RQ_DA_METRICA[col], "metrica": nome, "unidade": unidade, "n": r["n"],
                       "mediana": r["mediana"], "Q1": r["q1"], "Q3": r["q3"], "IQR": r["iqr"]})
    return pd.DataFrame(linhas)


def classes_por_metrica(df: pd.DataFrame) -> pd.DataFrame:
    """Distribuição Elite/High/Medium/Low de cada métrica e da classe geral (C1)."""
    colunas = {
        "Frequência de deploy": df["freq_deploy_semana"].map(classificar_frequencia),
        "Lead time (a)": df["lead_time_a_h"].map(classificar_lead_time),
        "Lead time (b)": df["lead_time_b_h"].map(classificar_lead_time),
        "CFR (a) CI": df["cfr_ci"].map(classificar_cfr),
        "CFR (b) entrega": df["cfr_entrega"].map(classificar_cfr),
        "Recuperação": df["recuperacao_h"].map(classificar_recuperacao),
        "Classe geral (C1)": df["classe_dora_c1"],
    }
    linhas = []
    for nome, serie in colunas.items():
        valid = serie.dropna()
        linha = {"metrica": nome, "n": int(len(valid))}
        for c in comum.ORDEM[::-1]:
            n = int((valid == c).sum())
            linha[c] = n
            linha[c + " %"] = 100 * n / len(valid) if len(valid) else np.nan
        linhas.append(linha)
    return pd.DataFrame(linhas)


def comparar_variantes(df: pd.DataFrame) -> Dict[str, float]:
    """RQ02 (a vs b) e RQ03 (a vs b): por que as duas variantes divergem."""
    out: Dict[str, float] = {}
    lt = df[["lead_time_a_h", "lead_time_b_h"]].dropna()
    out["lead_n"] = len(lt)
    out["lead_prop_a_maior_b"] = float((lt["lead_time_a_h"] > lt["lead_time_b_h"]).mean())
    out["lead_razao_mediana_a_sobre_b"] = float((lt["lead_time_a_h"] / lt["lead_time_b_h"]).median())
    out["lead_wilcoxon_p"] = float(stats.wilcoxon(lt["lead_time_a_h"], lt["lead_time_b_h"]).pvalue)
    rho, p = stats.spearmanr(lt["lead_time_a_h"], lt["lead_time_b_h"])
    out["lead_spearman_rho"], out["lead_spearman_p"] = float(rho), float(p)
    for v in ("a", "b"):
        d = df[["freq_deploy_semana", f"lead_time_{v}_h"]].dropna()
        rho, p = stats.spearmanr(d["freq_deploy_semana"], d[f"lead_time_{v}_h"])
        out[f"lead_{v}_vs_freq_rho"], out[f"lead_{v}_vs_freq_p"] = float(rho), float(p)
    cf = df[["cfr_ci", "cfr_entrega"]].dropna()
    out["cfr_n"] = len(cf)
    out["cfr_prop_ci_maior_entrega"] = float((cf["cfr_ci"] > cf["cfr_entrega"]).mean())
    out["cfr_entrega_zero_prop"] = float((cf["cfr_entrega"] == 0).mean())
    out["cfr_ci_zero_prop"] = float((cf["cfr_ci"] == 0).mean())
    rho, p = stats.spearmanr(cf["cfr_ci"], cf["cfr_entrega"])
    out["cfr_spearman_rho"], out["cfr_spearman_p"] = float(rho), float(p)
    return out


def censura(df: pd.DataFrame) -> Dict[str, float]:
    """RQ04: repositórios sem episódio e episódios censurados; contadores de exclusão."""
    total_ep = int(df["n_episodios"].sum())
    total_cens = int(df["n_episodios_censurados"].sum())
    return {
        "repos": len(df),
        "repos_sem_episodio": int((df["n_episodios"] == 0).sum()),
        "episodios": total_ep,
        "episodios_censurados": total_cens,
        "prop_episodios_censurados": total_cens / total_ep if total_ep else float("nan"),
        "repos_com_censura": int((df["n_episodios_censurados"] > 0).sum()),
        "repos_com_10pct_ou_mais_censurados": int((df["prop_episodios_censurados"] >= 0.1).sum()),
        "releases_censuradas_total": int(df["n_releases_censuradas"].sum()),
        "repos_lead_negativo": int((df["n_lead_negativos"] > 0).sum()),
        "repos_teto_runs": int(df["teto_runs_atingido"].sum()),
    }


def graficos(df: pd.DataFrame, saida: str) -> None:
    plt, caminho = comum.figura(saida, "rq01_04_distribuicoes")
    painel = [("freq_deploy_semana", "RQ01 releases/semana", True),
              ("lead_time_a_h", "RQ02 (a) lead time, horas", True),
              ("lead_time_b_h", "RQ02 (b) lead time, horas", True),
              ("cfr_ci", "RQ03 (a) CFR de CI", False),
              ("cfr_entrega", "RQ03 (b) CFR de entrega", False),
              ("recuperacao_h", "RQ04 recuperação, horas", True)]
    fig, eixos = plt.subplots(2, 3, figsize=(12, 6.5))
    for ax, (col, titulo, log) in zip(eixos.ravel(), painel):
        s = df[col].dropna()
        if log:
            s = s[s > 0]
            ax.hist(np.log10(s), bins=24, color="#4c78a8")
            ax.set_xlabel("log10 (escala logarítmica)")
        else:
            ax.hist(s, bins=24, color="#4c78a8")
            ax.set_xlabel("proporção")
        ax.axvline(np.log10(s.median()) if log else s.median(), color="#e45756", lw=1.5)
        ax.set_title(f"{titulo} (n={len(s)})", fontsize=10)
        ax.set_ylabel("repositórios")
    fig.tight_layout()
    fig.savefig(caminho, dpi=150)
    plt.close(fig)

    plt, caminho = comum.figura(saida, "rq01_04_classe_dora")
    classes = classes_por_metrica(df)
    fig, ax = plt.subplots(figsize=(8, 4))
    base = np.zeros(len(classes))
    cores = {"Elite": "#2a9d8f", "High": "#8ab17d", "Medium": "#e9c46a", "Low": "#e76f51"}
    for c in comum.ORDEM[::-1]:
        ax.barh(classes["metrica"], classes[c + " %"], left=base, color=cores[c], label=c)
        base += classes[c + " %"].fillna(0).to_numpy()
    ax.invert_yaxis()
    ax.set_xlabel("% dos repositórios")
    ax.legend(ncol=4, loc="upper center", bbox_to_anchor=(0.5, 1.15), frameon=False)
    fig.tight_layout()
    fig.savefig(caminho, dpi=150)
    plt.close(fig)


def main(argv=None) -> None:
    args = comum.argumentos(__doc__, argv)
    df = comum.carregar(args.csv)
    comum.salvar(descritivas(df), args.saida, "rq01_04_descritivas", casas=2)
    comum.salvar(classes_por_metrica(df), args.saida, "rq01_04_classificacao", casas=1)
    comum.salvar(pd.DataFrame([comparar_variantes(df)]).T.reset_index().rename(
        columns={"index": "indicador", 0: "valor"}), args.saida, "rq02_rq03_variantes", casas=3)
    comum.salvar(pd.DataFrame([censura(df)]).T.reset_index().rename(
        columns={"index": "indicador", 0: "valor"}), args.saida, "rq04_censura", casas=3)
    graficos(df, args.saida)
    print(comum.tabela_md(descritivas(df)))


if __name__ == "__main__":
    main()
