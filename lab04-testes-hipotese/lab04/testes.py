"""Os dois testes do par P1, bicaudais, com tamanho de efeito.

Em todos os resultados, estatística e efeito positivos indicam valores maiores no grupo A.
"""
from __future__ import annotations

import numpy as np
from scipy import stats


def g_de_hedges(a: np.ndarray, b: np.ndarray) -> float:
    """Diferença de médias em desvios-padrão, com correção para amostra pequena."""
    n_a, n_b = len(a), len(b)
    graus = n_a + n_b - 2
    variancia = ((n_a - 1) * np.var(a, ddof=1) + (n_b - 1) * np.var(b, ddof=1)) / graus
    correcao = 1 - 3 / (4 * graus - 1)
    return float(correcao * (np.mean(a) - np.mean(b)) / np.sqrt(variancia))


def rank_bisserial(u_a: float, n_a: int, n_b: int) -> float:
    """P(A > B) - P(B > A), de -1 a 1, a partir do U do grupo A."""
    return float(2 * u_a / (n_a * n_b) - 1)


def z_mann_whitney(a: np.ndarray, b: np.ndarray, u_a: float) -> float:
    """U padronizado, com correção de continuidade e de empates, como no SciPy assintótico."""
    n_a, n_b = len(a), len(b)
    n = n_a + n_b
    _, contagens = np.unique(np.concatenate([a, b]), return_counts=True)
    empates = float(np.sum(contagens**3 - contagens))
    desvio = np.sqrt(n_a * n_b / 12 * ((n + 1) - empates / (n * (n - 1))))
    diferenca = u_a - n_a * n_b / 2
    return float((diferenca - 0.5 * np.sign(diferenca)) / desvio)


def aplicar_welch(a: np.ndarray, b: np.ndarray) -> dict:
    resultado = stats.ttest_ind(a, b, equal_var=False)
    return {
        "estatistica": float(resultado.statistic),
        "p_valor": float(resultado.pvalue),
        "efeito": g_de_hedges(a, b),
        "nome_efeito": "g de Hedges",
        "gl": float(resultado.df),
    }


def aplicar_mann_whitney(a: np.ndarray, b: np.ndarray) -> dict:
    resultado = stats.mannwhitneyu(a, b, alternative="two-sided")
    u_a = float(resultado.statistic)
    return {
        "estatistica": u_a,
        "p_valor": float(resultado.pvalue),
        "efeito": rank_bisserial(u_a, len(a), len(b)),
        "nome_efeito": "correlação rank-bisserial",
        "z": z_mann_whitney(a, b, u_a),
    }
