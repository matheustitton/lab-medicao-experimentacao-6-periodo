import numpy as np
import pandas as pd
import pytest

from lab04.parametros import PISO_HORAS, estimar_parametros, sigma_log_amostral, sigma_por_media_mediana


def test_sigma_log_amostral_conhecido():
    horas = np.exp(np.array([0.0, 1.0, 2.0]))
    assert sigma_log_amostral(horas) == pytest.approx(1.0)


def test_sigma_log_amostral_aplica_piso_em_tempo_zero():
    assert np.isfinite(sigma_log_amostral(np.array([0.0, 1.0])))
    assert sigma_log_amostral(np.array([0.0, 1.0])) == pytest.approx(
        sigma_log_amostral(np.array([PISO_HORAS, 1.0]))
    )


def test_sigma_por_media_mediana_recupera_a_lognormal():
    amostra = np.random.default_rng(42).lognormal(np.log(10), 1.5, 2_000_000)
    assert sigma_por_media_mediana(amostra) == pytest.approx(1.5, abs=0.02)


def test_sigma_por_media_mediana_recusa_amostra_sem_cauda_direita():
    with pytest.raises(ValueError):
        sigma_por_media_mediana(np.array([1.0, 5.0, 5.0]))


def test_parametros_usam_o_grupo_sem_bot():
    tabela = pd.DataFrame({
        "grupo": ["sem_bot"] * 3 + ["com_bot"] * 2,
        "horas_ate_merge": [1.0, 2.0, 6.0, 100.0, 200.0],
    })
    parametros = estimar_parametros(tabela)
    assert parametros["mediana_horas"] == 2.0
    assert parametros["sigma_log"] == pytest.approx(np.sqrt(2 * np.log(3 / 2)), abs=1e-4)
    assert parametros["n_por_grupo"] == 2
    assert parametros["semente"] == 42
