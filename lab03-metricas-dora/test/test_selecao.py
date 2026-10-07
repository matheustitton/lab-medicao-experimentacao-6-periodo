from pipeline.selecao import buscar_candidatos, montar_consulta, tem_actions
from tests.fakes import ClienteFalso


def test_buscar_candidatos_fatia_por_estrelas_e_deduplica():
    consultas = []

    def handler(caminho, params):
        consultas.append(params["q"])
        item = lambda n, e: {"full_name": n, "stargazers_count": e, "language": "Go", "default_branch": "main",
                             "created_at": "2020-01-01T00:00:00Z", "outro_campo": "x"}
        return 200, {"total_count": 2, "items": [item("a/1", 1100), item("a/2", 1150)]}

    achados = buscar_candidatos(ClienteFalso(handler), ["1000..1199", "1200..1499"])
    assert [m["repo"] for m in achados] == ["a/1", "a/2"]
    assert achados[0] == {"repo": "a/1", "estrelas": 1100, "linguagem": "Go",
                          "criado_em": "2020-01-01T00:00:00Z", "default_branch": "main"}
    assert consultas == [montar_consulta("1000..1199"), montar_consulta("1200..1499")]
    assert "stars:1000..1199" in consultas[0]


def test_tem_actions():
    c = ClienteFalso(lambda caminho, p: (200, {"total_count": 3 if "com" in caminho else 0}))
    assert tem_actions(c, "o/com") and not tem_actions(c, "o/sem")
    assert not tem_actions(ClienteFalso(lambda *_: (404, None)), "o/x")
