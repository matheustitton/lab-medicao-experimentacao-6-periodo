from datetime import timedelta

from pipeline.coleta_runs import TETO_API, coletar_runs, contar_runs_janela, fatiar_mensal
from pipeline.config import Janela
from tests.fakes import ClienteFalso
from tests.helpers import d

JANELA = Janela(d("2025-01-01"), d("2025-12-31T23:59:59"))


def test_fatiar_mensal_cobre_a_janela_sem_sobreposicao():
    fatias = fatiar_mensal(JANELA)
    assert len(fatias) == 12 and fatias[0][0] == JANELA.inicio and fatias[-1][1] == JANELA.fim
    for (_, fim), (ini, _) in zip(fatias, fatias[1:]):
        assert ini - fim == timedelta(seconds=1)
    assert len(fatiar_mensal(Janela(d("2025-01-15"), d("2025-03-10")))) == 3


def run_bruto(conclusao, quando):
    return {"workflow_id": 1, "conclusion": conclusao, "event": "push",
            "created_at": quando, "run_started_at": quando, "updated_at": quando}


def test_coletar_runs_filtra_conclusoes_e_conta_ignorados():
    def handler(caminho, params):
        assert params["event"] == "push" and params["branch"] == "main"
        return 200, {"total_count": 3, "workflow_runs": [
            run_bruto("success", "2025-01-02T10:00:00Z"), run_bruto("failure", "2025-01-02T11:00:00Z"),
            run_bruto("cancelled", "2025-01-02T12:00:00Z")]}
    pequena = Janela(d("2025-01-01"), d("2025-01-31T23:59:59"))
    runs, ignorados, teto = coletar_runs(ClienteFalso(handler), "o/r", "main", pequena)
    assert [r["conclusao"] for r in runs] == ["success", "failure"] and ignorados == 1 and not teto
    assert set(runs[0]) == {"workflow_id", "conclusao", "iniciada_em", "atualizada_em"}


def test_contar_runs_janela_usa_total_count():
    c = ClienteFalso(lambda caminho, p: (200, {"total_count": 77, "workflow_runs": []}))
    assert contar_runs_janela(c, "o/r", "main", JANELA) == 77 and c.chamadas[0][1]["per_page"] == 1


def test_subdivide_intervalo_quando_bate_no_teto_da_api():
    from metricas.tempo import parse_data

    def handler(caminho, params):
        ini, fim = (parse_data(x) for x in params["created"].split(".."))
        if fim - ini > timedelta(hours=30):
            return 200, {"total_count": TETO_API + 200, "workflow_runs": []}
        return 200, {"total_count": 2, "workflow_runs": [
            run_bruto("success", params["created"].split("..")[0]),
            run_bruto("cancelled", params["created"].split("..")[0])]}
    dois_dias = Janela(d("2025-01-01"), d("2025-01-02T23:59:59"))
    runs, ignorados, teto = coletar_runs(ClienteFalso(handler), "o/r", "main", dois_dias)
    assert len(runs) == 2 and ignorados == 2 and not teto


def test_sinaliza_teto_quando_nao_da_mais_para_subdividir():
    def handler(caminho, params):
        return 200, {"total_count": TETO_API, "workflow_runs": [run_bruto("success", "2025-01-01T00:00:00Z")]}
    _, _, teto = coletar_runs(ClienteFalso(handler), "o/r", "main", Janela(d("2025-01-01"), d("2025-01-01T23:59:59")))
    assert teto
