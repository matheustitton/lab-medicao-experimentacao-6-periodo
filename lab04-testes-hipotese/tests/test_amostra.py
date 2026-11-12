from lab04.amostra import estudar, primeiro_n_com_poder

PARAMETROS = {"mediana_horas": 16.9, "sigma_log": 1.64, "n_por_grupo": 30, "semente": 42}


def test_primeiro_n_com_poder():
    assert primeiro_n_com_poder((10, 20, 30), [0.5, 0.81, 0.9]) == 20
    assert primeiro_n_com_poder((10, 20), [0.1, 0.2]) is None


def test_poder_cresce_com_n_e_usa_o_efeito_observado():
    resultado = estudar(PARAMETROS, {"razao_medianas": 0.5}, tamanhos=(30, 300), repeticoes=500)
    assert resultado["reducao_observada"] == 0.5
    for curva in resultado["poder"].values():
        assert curva[1] > curva[0]
    assert resultado["poder_com_n_real"]["mann_whitney"] == resultado["poder"]["mann_whitney"][0]
