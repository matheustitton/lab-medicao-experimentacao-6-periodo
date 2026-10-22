"""RQ08 (bônus): rework rate, a proporção de releases corretivas sobre o total de releases.

Compara com o CFR (b): o CFR (b) conta a release que FALHOU (a anterior à correção),
o rework rate conta a release CORRETIVA em si.

Uso: python -m analise.rq08 [--csv data/saida/dataset_sensibilidade.csv] [--saida ...]
"""
import argparse

import pandas as pd
from scipy import stats

from . import comum

CSV_SENSIBILIDADE = "data/saida/dataset_sensibilidade.csv"


def versoes(df: pd.DataFrame):
    return sorted(c[len("rework_"):] for c in df.columns if c.startswith("rework_"))


def resumo_rework(df: pd.DataFrame) -> pd.DataFrame:
    linhas = []
    for v in versoes(df):
        r = comum.resumo(df[f"rework_{v}"])
        d = df[[f"rework_{v}", f"cfr_b_{v}"]].dropna()
        rho, p = stats.spearmanr(d[f"rework_{v}"], d[f"cfr_b_{v}"])
        linhas.append({"heuristica": v, "n": r["n"], "mediana": r["mediana"], "Q1": r["q1"],
                       "Q3": r["q3"], "IQR": r["iqr"],
                       "mediana_cfr_b": float(d[f"cfr_b_{v}"].median()),
                       "spearman_rework_vs_cfr_b": float(rho), "p_valor": float(p)})
    return pd.DataFrame(linhas)


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--csv", default=CSV_SENSIBILIDADE)
    ap.add_argument("--saida", default=comum.SAIDA_PADRAO)
    args = ap.parse_args(argv)
    df = pd.read_csv(args.csv)
    t = resumo_rework(df)
    comum.salvar(t, args.saida, "rq08_rework", casas=3)
    print(comum.tabela_md(t, 3))


if __name__ == "__main__":
    main()
