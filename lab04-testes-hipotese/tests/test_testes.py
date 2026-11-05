import numpy as np
import pytest
from scipy import stats

from lab04.testes import aplicar_mann_whitney, aplicar_welch, g_de_hedges, rank_bisserial


@pytest.fixture
def amostras():
    rng = np.random.default_rng(42)
    return rng.lognormal(3, 1.5, 30), rng.lognormal(2, 1.5, 30)


def test_welch_bate_com_o_scipy(amostras):
    a, b = amostras
    esperado = stats.ttest_ind(a, b, equal_var=False)
    resultado = aplicar_welch(a, b)
    assert resultado["estatistica"] == pytest.approx(esperado.statistic)
    assert resultado["p_valor"] == pytest.approx(esperado.pvalue)
    assert resultado["gl"] == pytest.approx(esperado.df)


def test_mann_whitney_bate_com_o_scipy(amostras):
    a, b = amostras
    esperado = stats.mannwhitneyu(a, b, alternative="two-sided")
    resultado = aplicar_mann_whitney(a, b)
    assert resultado["estatistica"] == pytest.approx(esperado.statistic)
    assert resultado["p_valor"] == pytest.approx(esperado.pvalue)


def test_z_do_mann_whitney_reproduz_o_p_valor(amostras):
    resultado = aplicar_mann_whitney(*amostras)
    assert 2 * stats.norm.sf(abs(resultado["z"])) == pytest.approx(resultado["p_valor"])


def test_z_do_mann_whitney_reproduz_o_p_valor_com_empates():
    a = np.array([1.0, 2, 2, 3, 4, 5, 6, 7, 8, 9, 9, 10])
    b = np.array([2.0, 3, 3, 4, 5, 5, 6, 6, 7, 7, 8, 8])
    resultado = aplicar_mann_whitney(a, b)
    assert 2 * stats.norm.sf(abs(resultado["z"])) == pytest.approx(resultado["p_valor"])


def test_g_de_hedges_em_caso_conhecido():
    # diferença de médias -1, desvio combinado 1, correção 1 - 3/15 = 0,8
    assert g_de_hedges(np.array([1.0, 2, 3]), np.array([2.0, 3, 4])) == pytest.approx(-0.8)


@pytest.mark.parametrize("u_a,esperado", [(4, 1.0), (2, 0.0), (0, -1.0)])
def test_rank_bisserial_em_casos_conhecidos(u_a, esperado):
    assert rank_bisserial(u_a, 2, 2) == pytest.approx(esperado)


def test_sinal_do_efeito_segue_o_grupo_a(amostras):
    a, b = amostras
    maior, menor = a + 1000, b
    assert aplicar_welch(maior, menor)["efeito"] > 0
    assert aplicar_mann_whitney(maior, menor)["efeito"] == pytest.approx(1.0)
