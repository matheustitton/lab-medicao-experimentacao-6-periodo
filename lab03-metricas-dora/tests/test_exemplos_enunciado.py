"""Exemplos numéricos da seção 5 do enunciado (RQ02, RQ04 e classificação), com fixtures do pytest."""
import pytest

from metricas.classificacao import classificar_repositorio
from metricas.lead_time import lead_time_release_horas, lead_times_commits_horas
from metricas.recuperacao import tempo_recuperacao


def test_rq02_lead_time_a_e_b(release_v11):
    assert lead_time_release_horas(release_v11) == 13 * 24
    assert lead_times_commits_horas(release_v11) == [13 * 24, 5 * 24, 24]


def test_rq04_um_episodio_de_1h20(runs_episodio, janela_fim):
    r = tempo_recuperacao(runs_episodio, janela_fim)
    assert r.n_episodios == 1 and r.mediana_h == pytest.approx(80 / 60)


def test_rq04_episodio_censurado(runs_censurado, janela_fim):
    r = tempo_recuperacao(runs_censurado, janela_fim)
    assert (r.n_censurados, r.prop_censurados) == (1, 1.0)


def test_classe_dora_4_3_3_1_e_high():
    assert classificar_repositorio(freq=7, lead_h=48, cfr=0.2, recuperacao_h=200).geral == "High"
