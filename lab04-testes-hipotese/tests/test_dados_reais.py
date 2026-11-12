import numpy as np
import pandas as pd
import pytest

from lab04.dados_reais import LIMIARES_G, LIMIARES_RANK, analisar, ic_bootstrap, magnitude


@pytest.fixture
def tabela():
    rng = np.random.default_rng(0)
    return pd.DataFrame({
        "grupo": ["sem_bot"] * 30 + ["com_bot"] * 30,
        "horas_ate_merge": np.concatenate([rng.lognormal(3, 1, 30), rng.lognormal(3, 1, 30)]),
    })


@pytest.mark.parametrize("efeito,limiares,esperado", [
    (0.1, LIMIARES_G, "desprezível"), (-0.6, LIMIARES_G, "médio"), (1.2, LIMIARES_G, "grande"),
    (0.07, LIMIARES_RANK, "desprezível"), (0.35, LIMIARES_RANK, "médio"),
])
def test_magnitude(efeito, limiares, esperado):
    assert magnitude(efeito, limiares) == esperado


def test_ic_bootstrap_contem_a_diferenca_verdadeira():
    rng = np.random.default_rng(1)
    a, b = rng.normal(10, 1, 200), rng.normal(12, 1, 200)
    baixo, alto = ic_bootstrap(a, b, np.mean, np.random.default_rng(2), repeticoes=2000)
    assert baixo < 2 < alto


def test_analise_tem_os_dois_testes_e_e_reprodutivel(tabela):
    resultado = analisar(tabela, 42)
    assert resultado == analisar(tabela, 42)
    for teste in ("welch", "mann_whitney"):
        assert {"estatistica", "p_valor", "efeito", "magnitude", "rejeita"} <= set(resultado[teste])
    assert resultado["n"] == {"sem_bot": 30, "com_bot": 30}
