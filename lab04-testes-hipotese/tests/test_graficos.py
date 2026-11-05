import numpy as np
import pandas as pd
import pytest
from scipy.integrate import simpson

from lab04 import cores
from lab04.exemplo import executar_exemplo
from lab04.graficos import BORDAS_LOG10, contar_em_bins, grafico_g1, grafico_g2, simular_estatisticas_h0

PARAMETROS = {"mediana_horas": 16.9, "sigma_log": 1.64, "n_por_grupo": 30, "semente": 42}


@pytest.fixture(scope="module")
def exemplo():
    return executar_exemplo(PARAMETROS)


@pytest.fixture(scope="module")
def simulados():
    return simular_estatisticas_h0(PARAMETROS, repeticoes=200)


@pytest.fixture
def tabela():
    return pd.DataFrame({
        "grupo": ["sem_bot"] * 3 + ["com_bot"] * 3,
        "horas_ate_merge": [0.5, 10.0, 200.0, 1.0, 20.0, 400.0],
    })


def area_sombreada(figura, grupo):
    return sum(
        simpson(np.array(traco.y), x=np.array(traco.x))
        for traco in figura.data
        if traco.meta == grupo
    )


def test_area_sombreada_do_g2_e_o_p_valor(exemplo, simulados):
    welch, mann_whitney = grafico_g2(exemplo, simulados)
    assert area_sombreada(welch, "p_valor") == pytest.approx(exemplo["welch"]["p_valor"], abs=1e-6)
    assert area_sombreada(mann_whitney, "p_valor") == pytest.approx(exemplo["mann_whitney"]["p_valor"], abs=1e-6)


def test_regiao_de_rejeicao_do_g2_tem_area_alfa(exemplo, simulados):
    for figura in grafico_g2(exemplo, simulados):
        assert area_sombreada(figura, "rejeicao") == pytest.approx(exemplo["alfa"], abs=1e-6)


def test_cada_teste_usa_sempre_a_sua_cor(exemplo, simulados):
    welch, mann_whitney = grafico_g2(exemplo, simulados)
    assert any(traco.line.color == cores.COR_WELCH for traco in welch.data if traco.type == "scatter")
    assert any(traco.line.color == cores.COR_MANN_WHITNEY for traco in mann_whitney.data if traco.type == "scatter")


def test_todo_grafico_tem_titulo_eixos_e_legenda(tabela, exemplo, simulados):
    for figura in grafico_g1(tabela, exemplo) + grafico_g2(exemplo, simulados):
        assert figura.layout.title.text
        assert figura.layout.xaxis.title.text
        assert figura.layout.yaxis.title.text
        assert sum(1 for traco in figura.data if traco.showlegend is not False) >= 2


def test_g1_compara_real_e_simulado_nos_mesmos_bins(tabela, exemplo):
    for figura in grafico_g1(tabela, exemplo):
        real, simulado = figura.data
        assert real.name == "Dados reais" and simulado.name == "Dados simulados"
        assert np.array_equal(real.x, simulado.x)
        assert sum(real.y) == 3
        assert sum(simulado.y) == 30


def test_contar_em_bins_nao_perde_valores_extremos():
    assert contar_em_bins(np.array([0.0, 1e-6, 1.0, 1e9])).sum() == 4
    assert len(contar_em_bins(np.array([1.0]))) == len(BORDAS_LOG10) - 1


def test_simulacao_sob_h0_tem_centro_perto_de_zero():
    simulados = simular_estatisticas_h0(PARAMETROS, repeticoes=2000)
    assert abs(np.median(simulados["welch"])) < 0.1
    assert abs(np.mean(simulados["mann_whitney"])) < 0.1
    assert np.std(simulados["mann_whitney"]) == pytest.approx(1.0, abs=0.05)
