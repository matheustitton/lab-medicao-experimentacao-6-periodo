import pytest

from metricas.cfr import cfr_ci, classificar_conclusao
from metricas.recuperacao import episodios, tempo_recuperacao
from tests.helpers import d, execucao

FIM = d("2025-12-31")


def test_classificar_conclusao():
    for c in ("failure", "timed_out", "startup_failure"):
        assert classificar_conclusao(c) == "falha"
    assert classificar_conclusao("success") == "sucesso"
    for c in ("cancelled", "skipped", "neutral", "action_required", "stale", None, ""):
        assert classificar_conclusao(c) is None


def test_cfr_ci_ignora_cancelled_e_em_andamento():
    runs = [execucao(1, c, "2025-01-01") for c in
            ["success", "success", "success", "failure", "cancelled", None, "timed_out"]]
    r = cfr_ci(runs)
    assert (r.sucessos, r.falhas, r.ignoradas) == (3, 2, 2)
    assert r.taxa == pytest.approx(2 / 5)


def test_cfr_ci_sem_runs_validos():
    assert cfr_ci([execucao(1, "cancelled", "2025-01-01")]).taxa is None
    assert cfr_ci([]).taxa is None


def test_recuperacao_exemplo_do_enunciado():
    runs = [
        execucao(1, "success", "2025-05-01T09:00", "2025-05-01T09:05"),
        execucao(1, "failure", "2025-05-01T10:00", "2025-05-01T10:05"),   # início do episódio
        execucao(1, "failure", "2025-05-01T10:30", "2025-05-01T10:35"),   # mesmo episódio
        execucao(1, "success", "2025-05-01T11:15", "2025-05-01T11:20"),   # fim do episódio
    ]
    r = tempo_recuperacao(runs, FIM)
    assert r.n_episodios == 1 and r.n_censurados == 0
    assert r.mediana_h == pytest.approx(80 / 60)       # 1h20


def test_recuperacao_censurada():
    runs = [execucao(1, "success", "2025-12-01"), execucao(1, "failure", "2025-12-30")]
    r = tempo_recuperacao(runs, FIM)
    assert (r.n_episodios, r.n_censurados, r.prop_censurados) == (1, 1, 1.0)
    assert r.mediana_h is None
    assert r.mediana_h_com_censura == pytest.approx(24.0)   # 30/12 -> 31/12 (fim da janela)


def test_recuperacao_cancelled_nao_quebra_episodio():
    runs = [execucao(1, "success", "2025-05-01T09:00"), execucao(1, "failure", "2025-05-01T10:00"),
            execucao(1, "cancelled", "2025-05-01T10:30"),
            execucao(1, "success", "2025-05-01T12:00", "2025-05-01T12:10")]
    assert tempo_recuperacao(runs, FIM).mediana_h == pytest.approx(130 / 60)


def test_recuperacao_calculada_dentro_de_cada_workflow():
    runs = [
        execucao(1, "success", "2025-05-01T08:00"), execucao(1, "failure", "2025-05-01T09:00"),
        execucao(2, "success", "2025-05-01T10:00", "2025-05-01T10:10"),   # outro workflow: não recupera o 1
        execucao(1, "success", "2025-05-01T13:00", "2025-05-01T13:00"),
    ]
    eps = episodios(runs)
    assert len(eps) == 1 and eps[0].workflow_id == 1
    assert tempo_recuperacao(runs, FIM).mediana_h == 4.0


def test_recuperacao_falha_sem_sucesso_anterior_nao_abre_episodio():
    runs = [execucao(1, "failure", "2025-05-01T09:00"), execucao(1, "success", "2025-05-01T10:00")]
    r = tempo_recuperacao(runs, FIM)
    assert r.n_episodios == 0 and r.prop_censurados is None and r.mediana_h is None


def test_recuperacao_ordena_cronologicamente():
    runs = [execucao(1, "success", "2025-05-01T11:00"), execucao(1, "failure", "2025-05-01T10:00"),
            execucao(1, "success", "2025-05-01T09:00")]
    assert tempo_recuperacao(runs, FIM).mediana_h == 1.0
