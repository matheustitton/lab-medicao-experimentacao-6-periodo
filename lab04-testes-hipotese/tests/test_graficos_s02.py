import pytest

from lab04 import cores
from lab04.graficos_s02 import grafico_g3, grafico_g4
from lab04.simulacoes import executar_simulacoes

PARAMETROS = {"mediana_horas": 16.9, "sigma_log": 1.64, "sigma_log_amostral": 2.77, "n_por_grupo": 30, "semente": 42}


@pytest.fixture(scope="module")
def simulacoes():
    return executar_simulacoes(PARAMETROS, repeticoes=200)


def test_g3_tem_titulo_eixos_legenda_e_linha_em_alfa(simulacoes):
    fig = grafico_g3(simulacoes)
    assert fig.layout.title.text and fig.layout.xaxis.title.text and fig.layout.yaxis.title.text
    assert {t.name for t in fig.data} == {"t de Welch", "Mann-Whitney"}
    assert any(forma.type == "line" and forma.y0 == 0.05 for forma in fig.layout.shapes)


def test_g3_mostra_um_par_de_barras_por_alfa(simulacoes):
    fig = grafico_g3(simulacoes)
    assert len(fig.data) == 2 * len(simulacoes["alfas"])
    assert sum(t.visible for t in fig.data) == 2
    botoes = fig.layout.updatemenus[0].buttons
    assert len(botoes) == len(simulacoes["alfas"])


def test_g4_tem_um_painel_por_situacao_com_os_dois_testes(simulacoes):
    fig = grafico_g4(simulacoes)
    assert fig.layout.title.text
    visiveis = [t for t in fig.data if t.visible]
    assert len(visiveis) == 2 * len(simulacoes["situacoes"])
    assert {t.name for t in visiveis} == {"t de Welch", "Mann-Whitney"}
    assert sum(1 for t in fig.data if t.showlegend) == 2


def test_cada_teste_tem_a_mesma_cor_do_g2(simulacoes):
    for fig in (grafico_g3(simulacoes), grafico_g4(simulacoes)):
        for traco in fig.data:
            cor = traco.marker.color if traco.type == "bar" else traco.line.color
            esperado = cores.COR_WELCH if traco.name == "t de Welch" else cores.COR_MANN_WHITNEY
            assert cor == esperado
