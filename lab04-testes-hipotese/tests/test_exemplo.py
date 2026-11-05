import pytest

from lab04.exemplo import desfecho, executar_exemplo, formatar_p, interpretar

PARAMETROS = {"mediana_horas": 16.9, "sigma_log": 1.64, "n_por_grupo": 30, "semente": 42}


def test_exemplo_e_reprodutivel():
    assert executar_exemplo(PARAMETROS) == executar_exemplo(PARAMETROS)


def test_exemplo_tem_o_tamanho_dos_parametros_e_os_dois_testes():
    exemplo = executar_exemplo(PARAMETROS)
    assert len(exemplo["grupos"]["sem_bot"]) == 30
    assert len(exemplo["grupos"]["com_bot"]) == 30
    assert "gl" in exemplo["welch"]
    assert "z" in exemplo["mann_whitney"]


@pytest.mark.parametrize("p_valor,fator,esperado", [
    (0.01, 1.0, "erro tipo I"),
    (0.40, 1.0, "acerto"),
    (0.01, 0.5, "acerto"),
    (0.40, 0.5, "erro tipo II"),
])
def test_desfecho_compara_decisao_e_verdade(p_valor, fator, esperado):
    assert desfecho(p_valor, fator) == esperado


def test_interpretacao_usa_os_numeros_do_resultado():
    resultado = {"p_valor": 0.2345, "efeito": -0.42, "nome_efeito": "g de Hedges"}
    texto = interpretar("Welch", resultado, 0.5)
    assert "p = 0,234" in texto or "p = 0,235" in texto
    assert "g de Hedges = -0,42" in texto
    assert "não rejeita H₀" in texto
    assert "erro tipo II" in texto


def test_p_muito_pequeno_nao_vira_zero():
    assert formatar_p(0.00001) == "p < 0,001"
