import numpy as np
import pytest

from lab04.situacoes import (
    MULTIPLICADOR_OUTLIER, N_PEQUENO, PROPORCAO_OUTLIERS, contaminar_com_outliers, gerar, montar_situacoes,
)

PARAMETROS = {"mediana_horas": 16.9, "sigma_log": 1.64, "sigma_log_amostral": 2.77, "n_por_grupo": 30, "semente": 42}


@pytest.fixture
def situacoes():
    return {s.chave: s for s in montar_situacoes(PARAMETROS)}


def test_tem_base_tres_violacoes_e_um_contraste(situacoes):
    assert list(situacoes) == ["base", "cauda_pesada", "outliers", "amostra_pequena", "quase_simetrico"]
    assert sum(s.viola_pressupostos for s in situacoes.values()) == 3


def test_parametros_vem_dos_dados_reais(situacoes):
    assert situacoes["base"].sigma == 1.64 and situacoes["base"].n == 30
    assert situacoes["cauda_pesada"].sigma == 2.77
    assert situacoes["amostra_pequena"].n == N_PEQUENO
    assert situacoes["outliers"].proporcao_outliers == PROPORCAO_OUTLIERS


def test_outliers_multiplicam_so_a_fracao_sorteada():
    horas = np.ones((1000, 100))
    contaminado = contaminar_com_outliers(np.random.default_rng(42), horas, 0.05)
    assert set(np.unique(contaminado)) == {1.0, MULTIPLICADOR_OUTLIER}
    assert np.mean(contaminado > 1) == pytest.approx(0.05, abs=0.005)


def test_sem_outliers_nao_muda_nada():
    horas = np.arange(5.0)
    assert contaminar_com_outliers(np.random.default_rng(42), horas, 0.0) is horas


def test_recusa_proporcao_invalida():
    with pytest.raises(ValueError):
        contaminar_com_outliers(np.random.default_rng(42), np.ones(3), 1.0)


@pytest.mark.parametrize("chave", ["base", "cauda_pesada", "outliers", "amostra_pequena", "quase_simetrico"])
def test_gerar_devolve_matrizes_do_tamanho_da_situacao(situacoes, chave):
    a, b = gerar(np.random.default_rng(42), PARAMETROS, situacoes[chave], 1.0, repeticoes=7)
    assert a.shape == b.shape == (7, situacoes[chave].n)


def test_fator_preserva_a_razao_das_medianas_mesmo_com_outliers(situacoes):
    a, b = gerar(np.random.default_rng(42), PARAMETROS, situacoes["outliers"], 0.5, repeticoes=3000)
    assert np.median(b) / np.median(a) == pytest.approx(0.5, rel=0.05)
