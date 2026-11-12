import numpy as np
import pytest

from lab04.simulacoes import ALFAS, REDUCOES, executar_simulacoes, margem_monte_carlo, p_valores

PARAMETROS = {"mediana_horas": 16.9, "sigma_log": 1.64, "sigma_log_amostral": 2.77, "n_por_grupo": 30, "semente": 42}


@pytest.fixture(scope="module")
def resultado():
    return executar_simulacoes(PARAMETROS, repeticoes=2000)


def test_margem_de_10_mil_repeticoes_e_cerca_de_0_4_ponto():
    assert margem_monte_carlo(0.05, 10_000) == pytest.approx(0.0043, abs=0.0001)


def test_p_valores_um_por_conjunto():
    rng = np.random.default_rng(42)
    p = p_valores(rng.lognormal(size=(5, 30)), rng.lognormal(size=(5, 30)))
    assert p["welch"].shape == p["mann_whitney"].shape == (5,)


def test_reducoes_comecam_em_zero_e_tem_pelo_menos_cinco_valores():
    assert REDUCOES[0] == 0 and len(REDUCOES) >= 5 and list(REDUCOES) == sorted(REDUCOES)


def test_estrutura_do_resultado(resultado):
    assert resultado["alfas"] == list(ALFAS)
    for situacao in resultado["situacoes"]:
        for teste in ("welch", "mann_whitney"):
            for alfa in ALFAS:
                curva = situacao["poder"][teste][str(alfa)]
                assert len(curva) == len(REDUCOES)
                assert situacao["erro_tipo1"][teste][str(alfa)] == curva[0]


def test_mann_whitney_fica_perto_de_5_por_cento_no_cenario_base(resultado):
    base = resultado["situacoes"][0]
    assert base["erro_tipo1"]["mann_whitney"]["0.05"] == pytest.approx(0.05, abs=0.015)


def test_poder_cresce_com_o_efeito(resultado):
    base = resultado["situacoes"][0]
    curva = base["poder"]["mann_whitney"]["0.05"]
    assert curva[-1] > curva[0] + 0.3


def test_alfa_menor_rejeita_menos(resultado):
    for situacao in resultado["situacoes"]:
        for teste in ("welch", "mann_whitney"):
            assert all(r01 <= r05 for r01, r05 in zip(situacao["poder"][teste]["0.01"], situacao["poder"][teste]["0.05"]))


def test_reprodutivel_com_a_mesma_semente():
    assert executar_simulacoes(PARAMETROS, repeticoes=300) == executar_simulacoes(PARAMETROS, repeticoes=300)
