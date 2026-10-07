from pipeline.coleta_releases import coletar_commits, coletar_releases, coletar_releases_com_commits
from pipeline.config import Janela
from pipeline.github_client import ErroAPI
from tests.fakes import ClienteFalso
from tests.helpers import d

JANELA = Janela(d("2025-01-01"), d("2025-12-31T23:59:59"))


def rel(tag, quando, draft=False, pre=False):
    return {"tag_name": tag, "draft": draft, "prerelease": pre, "published_at": quando + "T12:00:00Z", "extra": 1}


def commit_bruto(n, quando="2025-03-01", msg="feat: x"):
    return {"sha": f"s{n}", "commit": {"author": {"date": quando + "T00:00:00Z"}, "message": msg + "\n\ncorpo"},
            "parents": [{}, {}] if n == 0 else [{}]}


def test_coletar_releases_filtra_ordena_e_encadeia_anterior():
    brutas = [rel("v1.1", "2025-03-01"), rel("v0.9", "2024-06-01"), rel("v1.0", "2025-01-10"),
              rel("rascunho", "2025-04-01", draft=True), rel("v2-rc", "2025-05-01", pre=True),
              rel("v1.2", "2026-02-01")]                        # depois da janela
    c = ClienteFalso(lambda caminho, p: (200, brutas))
    saida = coletar_releases(c, "o/r", JANELA)
    assert [r["tag"] for r in saida] == ["v1.0", "v1.1", "v2-rc"]
    assert [r["anterior_tag"] for r in saida] == ["v0.9", "v1.0", None]    # v0.9 está fora da janela
    assert saida[2]["prerelease"] is True


def _handler_compare(total, falha=None):
    def handler(caminho, params):
        if falha:
            return falha
        pagina, por = params["page"], params["per_page"]
        inicio = (pagina - 1) * por
        return 200, {"total_commits": total, "commits": [commit_bruto(i) for i in range(inicio, min(inicio + por, total))]}
    return handler


def test_commits_paginados_alem_de_100():
    c = ClienteFalso(_handler_compare(230))
    r = coletar_commits(c, "o/r", {"tag": "v2", "anterior_tag": "v1", "prerelease": False})
    assert r["status_compare"] == "ok" and len(r["commits"]) == 230 and len(c.chamadas) == 3
    assert r["commits"][1] == {"sha": "s1", "data": "2025-03-01T00:00:00Z", "msg": "feat: x", "merge": False}
    assert r["commits"][0]["merge"] is True
    assert c.chamadas[0][0] == "/repos/o/r/compare/v1...v2"


def test_commits_casos_de_borda():
    base = {"tag": "v2", "anterior_tag": "v1", "prerelease": False}
    assert coletar_commits(ClienteFalso(_handler_compare(0, (404, None))), "o/r", base)["status_compare"] == "indisponivel"
    assert coletar_commits(ClienteFalso(_handler_compare(5)), "o/r", {**base, "anterior_tag": None})["status_compare"] == "sem_anterior"
    assert coletar_commits(ClienteFalso(_handler_compare(5)), "o/r", {**base, "prerelease": True})["status_compare"] == "nao_coletado"
    assert coletar_commits(ClienteFalso(_handler_compare(250)), "o/r", base, max_paginas=2)["status_compare"] == "truncado"
    assert coletar_commits(ClienteFalso(_handler_compare(0)), "o/r", base)["commits"] == []

    def erro_422(caminho, params):
        raise ErroAPI("422", 422)
    assert coletar_commits(ClienteFalso(erro_422), "o/r", base)["status_compare"] == "indisponivel"

    def erro_500(caminho, params):
        raise ErroAPI("500", 500)
    try:
        coletar_commits(ClienteFalso(erro_500), "o/r", base)
        assert False, "deveria propagar"
    except ErroAPI:
        pass


def test_tag_com_barra_e_codificada():
    c = ClienteFalso(_handler_compare(1))
    coletar_commits(c, "o/r", {"tag": "pkg/v2 b", "anterior_tag": "pkg/v1", "prerelease": False})
    assert c.chamadas[0][0] == "/repos/o/r/compare/pkg/v1...pkg/v2%20b"


def test_releases_com_commits_integra_as_duas_etapas():
    def handler(caminho, params):
        if caminho.endswith("/releases"):
            return 200, [rel("v1", "2025-02-01"), rel("v2", "2025-03-01")]
        return 200, {"total_commits": 1, "commits": [commit_bruto(1)]}
    saida = coletar_releases_com_commits(ClienteFalso(handler), "o/r", JANELA)
    assert [r["status_compare"] for r in saida] == ["sem_anterior", "ok"]
