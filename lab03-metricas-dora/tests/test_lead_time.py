import pytest

from metricas.lead_time import lead_time_release_horas, lead_time_repo, lead_times_commits_horas
from tests.helpers import commit, release


def exemplo_enunciado():
    # v1.1 em 15/03 com commits de 02/03, 10/03 e 14/03 (exemplo da seção 5)
    return release("v1.1", "2025-03-15", "v1.0",
                   [commit("2025-03-02"), commit("2025-03-10"), commit("2025-03-14")])


def test_lead_time_exemplo_do_enunciado():
    r = exemplo_enunciado()
    assert lead_time_release_horas(r) == 13 * 24                       # variante (a): 13 dias
    assert lead_times_commits_horas(r) == [13 * 24, 5 * 24, 1 * 24]    # variante (b): 13, 5 e 1 dias


def test_lead_time_repo_medianas_a_e_b():
    v12 = release("v1.2", "2025-03-20", "v1.1", [commit("2025-03-19")])
    res = lead_time_repo([exemplo_enunciado(), v12])
    assert res.a_mediana_h == (13 * 24 + 24) / 2        # mediana de [312, 24]
    assert res.b_mediana_h == (24 + 120) / 2            # mediana de [312, 120, 24, 24]
    assert (res.n_releases_usadas, res.n_commits) == (2, 4)


def test_variantes_divergem_com_commit_esquecido():
    # um commit muito antigo "esquecido" explode (a) mas pouco afeta (b)
    commits = [commit("2025-01-01")] + [commit("2025-03-14") for _ in range(9)]
    r = release("v2", "2025-03-15", "v1", commits)
    res = lead_time_repo([r])
    assert res.a_mediana_h > 1000 and res.b_mediana_h == 24


def test_lead_time_casos_de_borda():
    rels = [
        release("v1", "2025-01-01", None, status="sem_anterior"),
        release("v2", "2025-02-01", "v1", status="indisponivel"),
        release("v3", "2025-03-01", "v2", []),                       # sem commits novos
        release("v4", "2025-04-01", "v3", [commit("2025-04-02")]),   # commit "do futuro"
        release("rc", "2025-04-02", None, status="nao_coletado", pre=True),
        release("v5", "2025-05-01", "v4", [commit("2025-04-30")], status="truncado"),
    ]
    res = lead_time_repo(rels)
    assert (res.n_sem_anterior, res.n_indisponiveis, res.n_sem_commits) == (1, 1, 1)
    assert res.n_negativos == 1 and res.n_truncadas == 1 and res.n_releases_usadas == 2


def test_lead_time_repo_sem_dados():
    res = lead_time_repo([])
    assert res.a_mediana_h is None and res.b_mediana_h is None
    assert lead_time_release_horas(release("v1", "2025-01-01")) is None
