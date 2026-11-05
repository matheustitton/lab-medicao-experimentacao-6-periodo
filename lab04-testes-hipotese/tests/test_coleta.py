import pytest

from lab04.coleta import eh_autor_bot, horas_ate_merge, montar_linhas


def item_pr(numero, login="ana", tipo="User", merged_at="2024-08-02T00:00:00Z"):
    return {
        "number": numero,
        "user": {"login": login, "type": tipo},
        "created_at": "2024-08-01T00:00:00Z",
        "html_url": f"https://github.com/o/r/pull/{numero}",
        "pull_request": {"merged_at": merged_at},
    }


def test_horas_ate_merge():
    assert horas_ate_merge("2024-08-01T00:00:00Z", "2024-08-02T12:30:00Z") == pytest.approx(36.5)


@pytest.mark.parametrize("login,tipo,esperado", [
    ("ana", "User", False),
    ("dependabot[bot]", "Bot", True),
    ("renovate[bot]", "User", True),
    ("github-actions", "Bot", True),
])
def test_eh_autor_bot(login, tipo, esperado):
    assert eh_autor_bot(item_pr(1, login, tipo)) is esperado


def test_montar_linhas_remove_bots_e_nao_mergeados():
    itens = [item_pr(1), item_pr(2, "dependabot[bot]", "Bot"), item_pr(3, merged_at=None), item_pr(4)]
    linhas = montar_linhas(itens, "sem_bot")
    assert [linha["numero"] for linha in linhas] == [1, 4]
    assert linhas[0]["grupo"] == "sem_bot"
    assert linhas[0]["horas_ate_merge"] == pytest.approx(24.0)


def test_montar_linhas_respeita_limite():
    assert len(montar_linhas([item_pr(i) for i in range(5)], "com_bot", limite=3)) == 3
