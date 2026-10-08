import pytest

from metricas.classificacao import (UMA_POR_MES_EM_SEMANAS, classificar_cfr, classificar_frequencia,
                                    classificar_lead_time, classificar_recuperacao, classificar_repositorio)


@pytest.mark.parametrize("valor,esperado", [
    (10, "Elite"), (7, "Elite"), (6.99, "High"), (1, "High"), (0.99, "Medium"),
    (UMA_POR_MES_EM_SEMANAS, "Medium"), (0.2, "Low"), (0, "Low"), (None, None)])
def test_frequencia(valor, esperado):
    assert classificar_frequencia(valor) == esperado


@pytest.mark.parametrize("h,esperado", [
    (23.9, "Elite"), (24, "High"), (167.9, "High"), (168, "Medium"), (719.9, "Medium"), (720, "Low"), (None, None)])
def test_lead_time(h, esperado):
    assert classificar_lead_time(h) == esperado


@pytest.mark.parametrize("taxa,esperado", [
    (0, "Elite"), (0.15, "Elite"), (0.1501, "High"), (0.30, "High"), (0.45, "Medium"), (0.4501, "Low"), (None, None)])
def test_cfr(taxa, esperado):
    assert classificar_cfr(taxa) == esperado


@pytest.mark.parametrize("h,esperado", [
    (0.5, "Elite"), (1, "High"), (23.9, "High"), (24, "Medium"), (167.9, "Medium"), (168, "Low"), (None, None)])
def test_recuperacao(h, esperado):
    assert classificar_recuperacao(h) == esperado


def test_classe_geral_exemplo_do_enunciado():
    # notas (4, 3, 3, 1): mediana 3 -> High
    c = classificar_repositorio(freq=7, lead_h=48, cfr=0.2, recuperacao_h=200)
    assert c.geral == "High" and c.n_metricas == 4


def test_classe_geral_arredonda_para_baixo():
    # notas (4, 3, 2, 1): mediana 2,5 -> 2 = Medium
    assert classificar_repositorio(7, 48, 0.40, 200).geral == "Medium"


def test_classe_geral_com_metrica_ausente():
    c = classificar_repositorio(7, None, 0.1, 0.5)
    assert c.n_metricas == 3 and c.geral == "Elite" and c.por_metrica["lead_time"] is None
    assert classificar_repositorio(None, None, None, None).geral is None
