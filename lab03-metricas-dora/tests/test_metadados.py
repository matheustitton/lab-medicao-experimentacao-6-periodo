from pipeline.github_client import ErroAPI
from pipeline.metadados import coletar_metadados
from tests.fakes import ClienteFalso


def test_contribuidores_pela_ultima_pagina():
    c = ClienteFalso(lambda caminho, p: (200, [{}], {"last": "https://api.github.com/x?per_page=1&anon=true&page=17"}))
    assert coletar_metadados(c, "o/r") == {"contribuidores": 17}
    assert c.chamadas[0][1] == {"anon": "true", "per_page": 1}


def test_lista_grande_demais_vira_ausente():
    def recusa(caminho, p):
        raise ErroAPI("403: contributor list too large", 403)
    assert coletar_metadados(ClienteFalso(recusa), "o/r") == {"contribuidores": None}
