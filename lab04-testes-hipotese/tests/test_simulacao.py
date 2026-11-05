import numpy as np
import pytest

from lab04.simulacao import gerar_grupos


def test_mesma_semente_gera_os_mesmos_dados():
    a1, b1 = gerar_grupos(np.random.default_rng(42), 10, 1.5, 30, 30, fator=0.5)
    a2, b2 = gerar_grupos(np.random.default_rng(42), 10, 1.5, 30, 30, fator=0.5)
    assert np.array_equal(a1, a2) and np.array_equal(b1, b2)


def test_recupera_mediana_sigma_e_fator_em_amostra_grande():
    a, b = gerar_grupos(np.random.default_rng(42), 10, 1.5, 500_000, 500_000, fator=0.5)
    assert np.median(a) == pytest.approx(10, rel=0.02)
    assert np.median(b) == pytest.approx(5, rel=0.02)
    assert np.std(np.log(a)) == pytest.approx(1.5, rel=0.02)
    assert np.std(np.log(b)) == pytest.approx(1.5, rel=0.02)


def test_repeticoes_geram_uma_matriz_por_grupo():
    a, b = gerar_grupos(np.random.default_rng(42), 10, 1.5, 30, 20, repeticoes=5)
    assert a.shape == (5, 30)
    assert b.shape == (5, 20)


@pytest.mark.parametrize("mediana,sigma,fator", [(0, 1, 1), (1, 0, 1), (1, 1, 0)])
def test_recusa_parametros_invalidos(mediana, sigma, fator):
    with pytest.raises(ValueError):
        gerar_grupos(np.random.default_rng(42), mediana, sigma, 5, 5, fator)
