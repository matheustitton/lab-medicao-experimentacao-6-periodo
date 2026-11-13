"""Simulações da Sprint 2: erro tipo I (Q1), poder (Q2) e violações de pressuposto (Q3).

Para cada situação e cada tamanho de efeito, gera 10.000 conjuntos de dados, aplica os dois
testes e conta a proporção de p-valores abaixo de α. Com redução 0 (H0 verdadeira), essa
proporção é o erro tipo I; com redução > 0, é o poder.

Uso: python -m lab04.simulacoes
"""
from __future__ import annotations

import json

import numpy as np
from scipy import stats

from lab04.caminhos import JSON_PARAMETROS, JSON_SIMULACOES
from lab04.situacoes import Situacao, gerar, montar_situacoes

REPETICOES = 10_000
ALFAS = (0.05, 0.01)
# Redução da mediana do tempo até o merge causada pelo bot: 0 é H0, 0,5 é "metade do tempo".
REDUCOES = (0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7)
TESTES = ("welch", "mann_whitney")


def p_valores(a: np.ndarray, b: np.ndarray) -> dict[str, np.ndarray]:
    """p-valor bicaudal dos dois testes, um por linha das matrizes (repeticoes, n)."""
    return {
        "welch": stats.ttest_ind(a, b, axis=1, equal_var=False).pvalue,
        "mann_whitney": stats.mannwhitneyu(a, b, axis=1, alternative="two-sided").pvalue,
    }


def margem_monte_carlo(proporcao: float, repeticoes: int = REPETICOES) -> float:
    """Meia largura do intervalo de 95% de uma proporção estimada por simulação."""
    return float(1.96 * np.sqrt(proporcao * (1 - proporcao) / repeticoes))


def taxas_de_rejeicao(
    rng: np.random.Generator, parametros: dict, situacao: Situacao, fator: float, repeticoes: int = REPETICOES
) -> dict[str, dict[str, float]]:
    """Proporção de rejeições de cada teste, para cada α."""
    a, b = gerar(rng, parametros, situacao, fator, repeticoes)
    return {
        teste: {str(alfa): float(np.mean(p < alfa)) for alfa in ALFAS}
        for teste, p in p_valores(a, b).items()
    }


def simular_situacao(
    parametros: dict, situacao: Situacao, indice: int, repeticoes: int = REPETICOES,
    reducoes: tuple[float, ...] = REDUCOES,
) -> dict:
    """Curva de poder completa de uma situação. O primeiro ponto (redução 0) é o erro tipo I."""
    poder: dict[str, dict[str, list[float]]] = {t: {str(a): [] for a in ALFAS} for t in TESTES}
    for j, reducao in enumerate(reducoes):
        # Semente própria por (situação, efeito): mudar uma situação não altera as outras.
        rng = np.random.default_rng([parametros["semente"], 100 + indice, j])
        taxas = taxas_de_rejeicao(rng, parametros, situacao, 1 - reducao, repeticoes)
        for teste in TESTES:
            for alfa in ALFAS:
                poder[teste][str(alfa)].append(taxas[teste][str(alfa)])
    return {
        "chave": situacao.chave,
        "rotulo": situacao.rotulo,
        "descricao": situacao.descricao,
        "sigma": situacao.sigma,
        "n": situacao.n,
        "proporcao_outliers": situacao.proporcao_outliers,
        "erro_tipo1": {t: {a: valores[0] for a, valores in poder[t].items()} for t in TESTES},
        "poder": poder,
    }


def executar_simulacoes(parametros: dict, repeticoes: int = REPETICOES) -> dict:
    return {
        "repeticoes": repeticoes,
        "alfas": list(ALFAS),
        "reducoes": list(REDUCOES),
        "situacoes": [
            simular_situacao(parametros, situacao, i, repeticoes)
            for i, situacao in enumerate(montar_situacoes(parametros))
        ],
    }


def main() -> dict:
    parametros = json.loads(JSON_PARAMETROS.read_text(encoding="utf-8"))
    resultado = executar_simulacoes(parametros)
    JSON_SIMULACOES.parent.mkdir(parents=True, exist_ok=True)
    JSON_SIMULACOES.write_text(
        json.dumps(resultado, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n"
    )
    print(f"Simulações em {JSON_SIMULACOES}")
    for s in resultado["situacoes"]:
        print(f"  {s['rotulo']}: erro tipo I Welch = {s['erro_tipo1']['welch']['0.05']:.3f}, "
              f"Mann-Whitney = {s['erro_tipo1']['mann_whitney']['0.05']:.3f}")
    return resultado


if __name__ == "__main__":
    main()
