"""Funcoes estatisticas genericas, compartilhadas por RQ1/RQ2 e RQ3.

Implementa o "Plano de analise estatistica" tal como escrito em
`docs/desenho-experimento.md` (Passo 1, ja commitado pelo Pedro na Sprint 01):

1. Teste principal: Wilcoxon signed-rank **pareado por kata** (a kata e o bloco).
2. Teste secundario: Mann-Whitney U sobre os 18 trials individuais.
3. Estatistica descritiva: sempre mediana/Q1/Q3, nunca media/desvio-padrao.
4. Tamanho de efeito junto de todo p-valor.
5. Analise de sensibilidade excluindo os trials de quem escreveu as katas (ameaca #5).

Desvio descoberto na limpeza dos dados (documentado tambem no relatorio final): o
desenho planejado (quadrado latino, ver tabela em docs/desenho-experimento.md) previa
que cada kata fosse resolvida nos dois tratamentos ao longo do grupo. Na execucao
real, `p2` seguiu a mesma linha do quadrado planejada para `p1` em vez da sua propria
(todas as 6 katas com tratamento identico a p1) - por isso `kata-01-faixas` acabou
100% IA e `kata-06-delimitadores` 100% MANUAL nos 18 trials reais, sem nenhum trial no
tratamento oposto. O Wilcoxon por kata so pode ser calculado nas 4 katas onde os dois
tratamentos de fato aparecem (n=4, nao os n=6 planejados) - a funcao abaixo reporta
isso explicitamente, nunca em silencio.
"""

from __future__ import annotations

import pandas as pd
from scipy import stats


def resumo(series: pd.Series) -> dict[str, float]:
    """Mediana, Q1, Q3, min, max - nunca media/desvio (N pequeno, sensivel a outlier)."""
    return {
        "n": int(series.count()),
        "median": round(float(series.median()), 2),
        "q1": round(float(series.quantile(0.25)), 2),
        "q3": round(float(series.quantile(0.75)), 2),
        "min": float(series.min()),
        "max": float(series.max()),
    }


def wilcoxon_por_kata(df: pd.DataFrame, value_col: str) -> dict:
    """Teste principal do plano: Wilcoxon pareado por kata (mediana IA x mediana MANUAL).

    So entram katas com os dois tratamentos representados nos dados reais. As demais
    ficam listadas em `katas_excluidas`, com o motivo.
    """
    por_kata = df.groupby(["kata", "tratamento"])[value_col].median().unstack()
    completas = por_kata.dropna(subset=["IA", "MANUAL"])
    excluidas = por_kata[por_kata.isna().any(axis=1)]

    resultado = {
        "n_katas_planejado": 6,
        "n_katas_valido": len(completas),
        "katas_usadas": list(completas.index),
        "katas_excluidas": {
            kata: ("so IA" if pd.isna(row["MANUAL"]) else "so MANUAL")
            for kata, row in excluidas.iterrows()
        },
    }

    if len(completas) < 2:
        resultado["statistic"] = None
        resultado["p"] = None
        resultado["effect_size_r"] = None
        return resultado

    stat, p = stats.wilcoxon(completas["IA"], completas["MANUAL"])
    resultado["statistic"] = float(stat)
    resultado["p"] = float(p)
    resultado["effect_size_r"] = _rank_biserial_pareado(completas["IA"] - completas["MANUAL"])
    return resultado


def mann_whitney(df: pd.DataFrame, value_col: str) -> dict:
    """Teste secundario do plano: Mann-Whitney U, 9 trials IA x 9 trials MANUAL."""
    ia = df[df.tratamento == "IA"][value_col]
    manual = df[df.tratamento == "MANUAL"][value_col]
    stat, p = stats.mannwhitneyu(ia, manual, alternative="two-sided")
    n1, n2 = len(ia), len(manual)
    effect_r = 1 - (2 * stat) / (n1 * n2)  # rank-biserial
    return {"n_ia": n1, "n_manual": n2, "statistic": float(stat), "p": float(p), "effect_size_r": round(effect_r, 3)}


def sensibilidade_excluindo(df: pd.DataFrame, value_col: str, integrante: str) -> dict:
    """Repete Wilcoxon-por-kata e Mann-Whitney sem os trials de um integrante
    (ameaca #5: quem escreveu as katas conhece os casos de borda de antemao)."""
    sem = df[df.integrante != integrante]
    return {
        "excluido": integrante,
        "n_trials_restantes": len(sem),
        "wilcoxon_por_kata": wilcoxon_por_kata(sem, value_col),
        "mann_whitney": mann_whitney(sem, value_col),
    }


def _rank_biserial_pareado(diffs: pd.Series) -> float | None:
    """Effect size para Wilcoxon pareado: proporcao de sinal positivo menos negativo."""
    diffs = diffs[diffs != 0]
    if diffs.empty:
        return None
    positivos = (diffs > 0).sum()
    return round((positivos - (len(diffs) - positivos)) / len(diffs), 3)