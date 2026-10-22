"""RQ07: sensibilidade da classificação DORA à definição operacional.

Para cada par de combinações: % de repositórios que mudam de categoria e kappa de Cohen
ponderado linear. Também mede a sensibilidade à versão da heurística de release corretiva.

Uso: python -m analise.rq07 [--csv data/saida/dataset_sensibilidade.csv] [--saida ...]
"""
from itertools import combinations
from typing import List

import pandas as pd
from sklearn.metrics import cohen_kappa_score

from . import comum

CSV_SENSIBILIDADE = "data/saida/dataset_sensibilidade.csv"
COMBINACOES = {
    "C1": "release | lead (a) | CFR (a) [referência]",
    "C2": "release + pré-release | lead (b) | CFR (b)",
    "C3": "release | lead (b) | CFR (a)",
    "C4": "release | lead (a) | CFR (b)",
}


def pontos(serie: pd.Series) -> pd.Series:
    return serie.map(comum.PONTOS)


def comparar_pares(df: pd.DataFrame, colunas: List[str], prefixo: str = "classe_") -> pd.DataFrame:
    linhas = []
    for a, b in combinations(colunas, 2):
        d = df[[prefixo + a, prefixo + b]].dropna()
        pa, pb = pontos(d[prefixo + a]), pontos(d[prefixo + b])
        muda = (pa != pb).mean()
        kappa = cohen_kappa_score(pa, pb, weights="linear", labels=[1, 2, 3, 4]) if len(d) else float("nan")
        linhas.append({"par": f"{a} × {b}", "n": len(d), "mudaram_n": int((pa != pb).sum()),
                       "mudaram_%": 100 * muda, "kappa_ponderado": float(kappa),
                       "interpretacao": interpretar_kappa(kappa)})
    return pd.DataFrame(linhas)


def interpretar_kappa(k: float) -> str:
    """Landis & Koch (1977)."""
    if k != k:
        return "—"
    if k < 0:
        return "pobre"
    if k <= 0.20:
        return "leve"
    if k <= 0.40:
        return "razoável"
    if k <= 0.60:
        return "moderada"
    if k <= 0.80:
        return "substancial"
    return "quase perfeita"


def distribuicao(df: pd.DataFrame, colunas: List[str], prefixo: str = "classe_") -> pd.DataFrame:
    linhas = []
    for c in colunas:
        s = df[prefixo + c].dropna()
        linha = {"combinacao": c, "n": len(s)}
        for k in comum.ORDEM[::-1]:
            linha[k] = int((s == k).sum())
        linhas.append(linha)
    return pd.DataFrame(linhas)


def correlacao_por_combinacao(df: pd.DataFrame) -> pd.DataFrame:
    """A ordem relativa dos repositórios é robusta? Spearman entre as pontuações das combinações."""
    from scipy import stats
    linhas = []
    for a, b in combinations(COMBINACOES, 2):
        d = df[["classe_" + a, "classe_" + b]].dropna()
        rho, _ = stats.spearmanr(pontos(d["classe_" + a]), pontos(d["classe_" + b]))
        linhas.append({"par": f"{a} × {b}", "n": len(d), "spearman_rho": float(rho)})
    return pd.DataFrame(linhas)


def tabela_cruzada(df: pd.DataFrame, a: str, b: str) -> pd.DataFrame:
    t = pd.crosstab(df["classe_" + a], df["classe_" + b]).reindex(index=comum.ORDEM[::-1],
                                                                 columns=comum.ORDEM[::-1], fill_value=0)
    t.insert(0, f"{a} \\ {b}", t.index)
    return t.reset_index(drop=True)


def sensibilidade_frequencia(df: pd.DataFrame) -> pd.DataFrame:
    """RQ01 sob duas unidades de deploy: só releases ou releases + pré-releases."""
    from metricas.classificacao import classificar_frequencia
    a, b = df["freq_release"], df["freq_release_pre"]
    ca, cb = a.map(classificar_frequencia), b.map(classificar_frequencia)
    ra, rb = comum.resumo(a), comum.resumo(b)
    return pd.DataFrame([{
        "n": len(df), "mediana_release": ra["mediana"], "q1_release": ra["q1"], "q3_release": ra["q3"],
        "mediana_release_pre": rb["mediana"], "q1_release_pre": rb["q1"], "q3_release_pre": rb["q3"],
        "mudaram_classe_n": int((ca != cb).sum()), "mudaram_classe_%": 100 * float((ca != cb).mean())}])


def main(argv=None) -> None:
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--csv", default=CSV_SENSIBILIDADE)
    ap.add_argument("--saida", default=comum.SAIDA_PADRAO)
    args = ap.parse_args(argv)
    df = pd.read_csv(args.csv)
    combos = list(COMBINACOES)
    comum.salvar(distribuicao(df, combos), args.saida, "rq07_distribuicao_combinacoes")
    comum.salvar(comparar_pares(df, combos), args.saida, "rq07_pares", casas=3)
    comum.salvar(correlacao_por_combinacao(df), args.saida, "rq07_ordem_relativa", casas=3)
    comum.salvar(tabela_cruzada(df, "C1", "C2"), args.saida, "rq07_cruzada_c1_c2")
    comum.salvar(sensibilidade_frequencia(df), args.saida, "rq07_frequencia_com_prerelease", casas=3)
    heur = [c[len("classe_C4_"):] for c in df.columns if c.startswith("classe_C4_")]
    comum.salvar(distribuicao(df, [f"C4_{h}" for h in heur]), args.saida, "rq07_heuristicas_distribuicao")
    comum.salvar(comparar_pares(df, [f"C4_{h}" for h in heur]), args.saida, "rq07_heuristicas_pares", casas=3)
    print(comum.tabela_md(comparar_pares(df, combos), 3))


if __name__ == "__main__":
    main()
