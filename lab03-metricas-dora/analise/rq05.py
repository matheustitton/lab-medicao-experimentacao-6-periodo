"""RQ05: correlação de Spearman entre frequência de deploy e CFR (variantes a e b).

Uso: python -m analise.rq05 [--csv ...] [--saida ...]
"""
import argparse
import os

import pandas as pd
from scipy import stats

from . import comum

PARES = [("freq_deploy_semana", "cfr_ci", "CFR (a) CI"),
         ("freq_deploy_semana", "cfr_entrega", "CFR (b) entrega")]


def correlacoes(df: pd.DataFrame) -> pd.DataFrame:
    linhas = []
    for x, y, nome in PARES:
        d = df[[x, y]].dropna()
        rho, p = stats.spearmanr(d[x], d[y])
        linhas.append({"variante": nome, "n": len(d), "rho": float(rho), "p_valor": float(p),
                       "forca": comum.interpretar_rho(rho),
                       "sentido": "positiva" if rho > 0 else "negativa"})
    return pd.DataFrame(linhas)


def correlacoes_heuristicas(sens: pd.DataFrame) -> pd.DataFrame:
    """Spearman entre frequência e CFR (b) para cada versão da heurística (dataset_sensibilidade.csv)."""
    linhas = []
    versoes = sorted(c[len("cfr_b_"):] for c in sens.columns
                     if c.startswith("cfr_b_") and not c.startswith("cfr_b_pre_"))
    for v in versoes:
        d = sens[["freq_release", f"cfr_b_{v}"]].dropna()
        rho, p = stats.spearmanr(d["freq_release"], d[f"cfr_b_{v}"])
        linhas.append({"heuristica": v, "n": len(d), "mediana_cfr_b": float(d[f"cfr_b_{v}"].median()),
                       "rho": float(rho), "p_valor": float(p), "forca": comum.interpretar_rho(rho)})
    return pd.DataFrame(linhas)


def dispersao(df: pd.DataFrame, saida: str) -> None:
    plt, caminho = comum.figura(saida, "rq05_dispersao")
    fig, eixos = plt.subplots(1, 2, figsize=(11, 4.2))
    for ax, (x, y, nome) in zip(eixos, PARES):
        d = df[[x, y]].dropna()
        d = d[d[x] > 0]
        ax.scatter(d[x], d[y], s=14, alpha=0.6, color="#4c78a8")
        ax.set_xscale("log")
        rho, _ = stats.spearmanr(d[x], d[y])
        ax.set_title(f"{nome}: ρ = {rho:.2f} (n={len(d)})", fontsize=10)
        ax.set_xlabel("frequência de deploy (releases/semana, escala log)")
        ax.set_ylabel(nome)
    fig.tight_layout()
    fig.savefig(caminho, dpi=150)
    plt.close(fig)


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--csv", default=comum.CSV_PADRAO)
    ap.add_argument("--saida", default=comum.SAIDA_PADRAO)
    ap.add_argument("--sens", default="data/saida/dataset_sensibilidade.csv")
    args = ap.parse_args(argv)
    df = comum.carregar(args.csv)
    tabela = correlacoes(df)
    comum.salvar(tabela, args.saida, "rq05_spearman", casas=3)
    dispersao(df, args.saida)
    if os.path.exists(args.sens):
        comum.salvar(correlacoes_heuristicas(pd.read_csv(args.sens)), args.saida,
                     "rq05_spearman_heuristicas", casas=3)
    print(comum.tabela_md(tabela, 3))


if __name__ == "__main__":
    main()
