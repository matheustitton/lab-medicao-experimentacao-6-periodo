"""Exemplo da RQ03 (b) do enunciado, com fixtures do pytest (Sprint 2)."""
from metricas.cfr_entrega import cfr_entrega
from metricas.heuristica import v1


def test_rq03b_v230_falhou_e_v240_nao(historia_cfr, janela_fim):
    r = cfr_entrega(historia_cfr, janela_fim, v1, dias=7)
    assert (r.avaliadas, r.falhas) == (4, 1)
    assert v1(historia_cfr[1]) and not v1(historia_cfr[3])
