from metricas.cfr_entrega import cfr_entrega
from metricas.heuristica import v1
from tests.helpers import commit, d, release


def _historia():
    return [
        release("v2.3.0", "2025-05-10", None, [commit("2025-05-01", "feat: x")]),
        release("v2.3.1", "2025-05-12", "v2.3.0", [commit("2025-05-11", "fix: crash ao abrir arquivo")]),
        release("v2.4.0", "2025-06-01", "v2.3.1", [commit("2025-05-20", "feat: y")]),
        release("v2.5.0", "2025-06-20", "v2.4.0", [commit("2025-06-10", "feat: z")]),
    ]


def test_cfr_entrega_exemplo_do_enunciado():
    r = cfr_entrega(_historia(), d("2025-12-31"), v1, dias=7)
    assert (r.avaliadas, r.falhas, r.censuradas) == (4, 1, 0)   # só v2.3.0 falhou
    assert r.taxa == 0.25


def test_cfr_entrega_censura_ultimos_7_dias_da_janela():
    rels = _historia() + [release("v2.5.1", "2025-12-28", "v2.5.0", [commit("2025-12-27", "fix: a")])]
    r = cfr_entrega(rels, d("2025-12-31"), v1)
    assert r.censuradas == 1 and r.avaliadas == 4
    assert r.falhas == 1      # v2.5.0 não é marcada: v2.5.1 saiu 8 dias depois, fora dos 7 dias


def test_cfr_entrega_uma_release_e_pre_release():
    r = cfr_entrega([release("v1.0.0", "2025-01-01"), release("rc", "2025-01-02", pre=True)],
                    d("2025-12-31"), v1)
    assert (r.avaliadas, r.falhas, r.taxa) == (1, 0, 0.0)
    assert cfr_entrega([], d("2025-12-31"), v1).taxa is None
    tudo_censurado = cfr_entrega([release("v1", "2025-12-30")], d("2025-12-31"), v1)
    assert tudo_censurado.taxa is None and tudo_censurado.censuradas == 1
