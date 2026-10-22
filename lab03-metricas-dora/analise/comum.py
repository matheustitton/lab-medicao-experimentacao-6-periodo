"""Funções compartilhadas pelas análises: resumo (mediana/IQR), tamanhos de efeito, tabelas e figuras."""
import argparse
import os
from typing import Dict, Iterable, List, Optional, Sequence

import numpy as np
import pandas as pd
from scipy import stats

CSV_PADRAO = "data/saida/dataset_dora.csv"
SAIDA_PADRAO = "data/saida/analise"
ORDEM = ["Low", "Medium", "High", "Elite"]
PONTOS = {c: i + 1 for i, c in enumerate(ORDEM)}

# nome no CSV -> (rótulo para tabelas, unidade)
METRICAS = {
    "freq_deploy_semana": ("Frequência de deploy", "releases/semana"),
    "lead_time_a_h": ("Lead time (a) por release", "horas"),
    "lead_time_b_h": ("Lead time (b) por commit", "horas"),
    "cfr_ci": ("CFR (a) CI", "proporção"),
    "cfr_entrega": ("CFR (b) entrega", "proporção"),
    "recuperacao_h": ("Tempo de recuperação", "horas"),
}


def argumentos(descricao: str, argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description=descricao)
    ap.add_argument("--csv", default=CSV_PADRAO)
    ap.add_argument("--saida", default=SAIDA_PADRAO)
    return ap.parse_args(argv)


def carregar(caminho: str = CSV_PADRAO) -> pd.DataFrame:
    return pd.read_csv(caminho)


def resumo(serie: pd.Series) -> Dict[str, float]:
    """n, mediana, Q1, Q3 e IQR ignorando valores ausentes."""
    s = pd.to_numeric(serie, errors="coerce").dropna()
    if s.empty:
        return {"n": 0, "mediana": np.nan, "q1": np.nan, "q3": np.nan, "iqr": np.nan}
    q1, med, q3 = s.quantile([0.25, 0.5, 0.75])
    return {"n": int(len(s)), "mediana": float(med), "q1": float(q1), "q3": float(q3),
            "iqr": float(q3 - q1)}


def epsilon_quadrado(h: float, n: int) -> float:
    """Tamanho de efeito do Kruskal-Wallis: ε² = H / (n - 1)."""
    return float(h / (n - 1)) if n > 1 else float("nan")


def cliffs_delta(x: Iterable[float], y: Iterable[float]) -> float:
    """δ = 2·U1/(n1·n2) − 1, com U1 de mannwhitneyu(x, y)."""
    x, y = list(x), list(y)
    u1 = stats.mannwhitneyu(x, y, alternative="two-sided").statistic
    return float(2 * u1 / (len(x) * len(y)) - 1)


def interpretar_delta(delta: float) -> str:
    """Romano et al. (2006)."""
    d = abs(delta)
    if d < 0.147:
        return "desprezível"
    if d < 0.33:
        return "pequeno"
    if d < 0.474:
        return "médio"
    return "grande"


def interpretar_epsilon(e: float) -> str:
    """Referências de Cohen (1988) para η²/ε²: 0,01 pequeno; 0,06 médio; 0,14 grande."""
    if e < 0.01:
        return "desprezível"
    if e < 0.06:
        return "pequeno"
    if e < 0.14:
        return "médio"
    return "grande"


def interpretar_rho(rho: float) -> str:
    r = abs(rho)
    if r < 0.1:
        return "desprezível"
    if r < 0.3:
        return "fraca"
    if r < 0.5:
        return "moderada"
    return "forte"


def quartis(serie: pd.Series, prefixo: str = "Q") -> pd.Series:
    """Converte uma coluna numérica em grupos Q1..Q4 pelos quartis (empates colapsam grupos)."""
    r = pd.qcut(serie, 4, duplicates="drop")
    categorias = list(r.cat.categories)
    nomes = {c: f"{prefixo}{i + 1}" for i, c in enumerate(categorias)}
    return r.map(nomes).astype(object)


def formatar(v, casas: int = 2) -> str:
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "—"
    if isinstance(v, (int, np.integer)):
        return str(int(v))
    if isinstance(v, float):
        a = abs(v)
        if a != 0 and (a < 0.001):
            return f"{v:.1e}"
        return f"{v:.{casas}f}"
    return str(v)


def tabela_md(df: pd.DataFrame, casas: int = 2) -> str:
    cab = "| " + " | ".join(map(str, df.columns)) + " |"
    sep = "|" + "|".join("---" for _ in df.columns) + "|"
    linhas = ["| " + " | ".join(formatar(v, casas) for v in row) + " |" for row in df.itertuples(index=False)]
    return "\n".join([cab, sep] + linhas)


def salvar(df: pd.DataFrame, saida: str, nome: str, casas: int = 2) -> None:
    os.makedirs(saida, exist_ok=True)
    df.to_csv(os.path.join(saida, nome + ".csv"), index=False)
    with open(os.path.join(saida, nome + ".md"), "w", encoding="utf-8") as f:
        f.write(tabela_md(df, casas) + "\n")


def figura(saida: str, nome: str):
    """Devolve (plt, caminho) com backend sem tela."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    os.makedirs(saida, exist_ok=True)
    return plt, os.path.join(saida, nome + ".png")


def distribuicao_classes(serie: pd.Series) -> pd.DataFrame:
    contagem = serie.value_counts()
    total = int(contagem.sum())
    linhas = [{"classe": c, "repositorios": int(contagem.get(c, 0)),
               "percentual": 100 * contagem.get(c, 0) / total if total else np.nan} for c in ORDEM[::-1]]
    return pd.DataFrame(linhas)
