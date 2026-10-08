import pytest
import requests

from pipeline.cache import Cache
from pipeline.github_client import ClienteGitHub, ErroAPI, normalizar, parse_link


class RespostaFalsa:
    def __init__(self, status=200, corpo=None, headers=None, texto=""):
        self.status_code, self._corpo, self.headers, self.text = status, corpo, headers or {}, texto

    def json(self):
        return self._corpo


class SessaoFalsa:
    def __init__(self, respostas):
        self.respostas, self.headers, self.chamadas = list(respostas), {}, []

    def get(self, url, params=None, timeout=None):
        self.chamadas.append((url, params))
        r = self.respostas.pop(0)
        if isinstance(r, Exception):
            raise r
        return r


def cliente(respostas, cache=None, agora=1000.0, token="tok"):
    esperas = []
    sessao = SessaoFalsa(respostas)
    c = ClienteGitHub(token, cache or Cache(":memory:"), sessao=sessao,
                      dormir=esperas.append, agora=lambda: agora)
    return c, sessao, esperas


def test_normalizar_url_absoluta_do_link():
    assert normalizar("https://api.github.com/repos/o/r/releases?per_page=100&page=2") == (
        "/repos/o/r/releases", {"per_page": "100", "page": "2"})
    assert parse_link('<https://a/b?page=2>; rel="next", <https://a/b?page=9>; rel="last"') == {
        "next": "https://a/b?page=2", "last": "https://a/b?page=9"}


def test_segunda_chamada_vem_do_cache_sem_rede():
    c, sessao, _ = cliente([RespostaFalsa(200, {"ok": True})])
    assert c.get("/x", {"a": 1}).dados == {"ok": True}
    assert c.get("/x", {"a": 1}).dados == {"ok": True}
    assert len(sessao.chamadas) == 1 and c.n_chamadas_rede == 1


def test_retomada_apos_interrupcao_reaproveita_cache(tmp_path):
    arq = str(tmp_path / "c.sqlite")
    c1, _, _ = cliente([RespostaFalsa(200, [1])], cache=Cache(arq))
    c1.get("/a")
    c2, sessao2, _ = cliente([RespostaFalsa(200, [2])], cache=Cache(arq))   # novo processo
    assert c2.get("/a").dados == [1] and c2.get("/b").dados == [2]
    assert len(sessao2.chamadas) == 1       # só /b foi para a rede


def test_headers_de_autenticacao():
    c, sessao, _ = cliente([], token="abc")
    assert sessao.headers["Authorization"] == "Bearer abc"
    _, sessao2, _ = cliente([], token=None)
    assert "Authorization" not in sessao2.headers


def test_backoff_exponencial_em_5xx():
    c, _, esperas = cliente([RespostaFalsa(500), RespostaFalsa(502), RespostaFalsa(200, {"ok": 1})])
    assert c.get("/x").status == 200 and esperas == [1, 2]


def test_5xx_persistente_levanta_erro():
    c, _, esperas = cliente([RespostaFalsa(500)] * 5)
    with pytest.raises(ErroAPI):
        c.get("/x")
    assert esperas == [1, 2, 4, 8]


def test_erro_de_rede_tenta_de_novo():
    c, _, esperas = cliente([requests.ConnectionError(), RespostaFalsa(200, [])])
    assert c.get("/x").status == 200 and esperas == [1]


def test_rate_limit_403_espera_ate_o_reset():
    limite = RespostaFalsa(403, None, {"X-RateLimit-Remaining": "0", "X-RateLimit-Reset": "1030"})
    c, _, esperas = cliente([limite, RespostaFalsa(200, {"ok": 1})], agora=1000.0)
    assert c.get("/x").status == 200 and esperas == [31.0]


def test_rate_limit_secundario_usa_retry_after():
    c, _, esperas = cliente([RespostaFalsa(429, None, {"Retry-After": "10"}), RespostaFalsa(200, [])])
    c.get("/x")
    assert esperas == [11.0]


def test_pausa_preventiva_quando_cota_quase_acabando():
    r = RespostaFalsa(200, [], {"X-RateLimit-Remaining": "1", "X-RateLimit-Reset": "1060"})
    c, _, esperas = cliente([r], agora=1000.0)
    c.get("/x")
    assert esperas == [61.0]


def test_403_que_nao_e_rate_limit_levanta_erro():
    c, _, _ = cliente([RespostaFalsa(403, None, {}, "Repository access blocked")])
    with pytest.raises(ErroAPI) as e:
        c.get("/x")
    assert e.value.status == 403


def test_404_e_cacheado_e_nao_levanta():
    c, sessao, _ = cliente([RespostaFalsa(404, {"message": "Not Found"}), RespostaFalsa(404, {})])
    assert c.get("/x").status == 404 and c.get("/x").status == 404
    assert len(sessao.chamadas) == 1                 # segundo 404 veio do cache
    assert list(c.paginar("/y")) == []               # 404 na paginação = lista vazia, sem erro


def test_paginacao_segue_link_next():
    p1 = RespostaFalsa(200, [1, 2], {"Link": '<https://api.github.com/x?per_page=100&page=2>; rel="next"'})
    p2 = RespostaFalsa(200, [3])
    c, sessao, _ = cliente([p1, p2])
    assert list(c.paginar("/x")) == [1, 2, 3]
    assert sessao.chamadas[0][1] == {"per_page": 100} and sessao.chamadas[1][1]["page"] == "2"


def test_paginacao_com_chave_reducao_e_limite_de_paginas():
    link = {"Link": '<https://api.github.com/x?page=2>; rel="next"'}
    c, _, _ = cliente([RespostaFalsa(200, {"items": [{"v": 1, "lixo": 0}]}, link),
                       RespostaFalsa(200, {"items": [{"v": 2, "lixo": 0}]}, link)])
    reduz = lambda d: {"items": [{"v": i["v"]} for i in d["items"]]}
    assert list(c.paginar("/x", chave="items", reduzir=reduz, max_paginas=2)) == [{"v": 1}, {"v": 2}]
    assert c.cache.obter("/x?per_page=100")[1] == {"items": [{"v": 1}]}      # gravou o reduzido


def test_contar_via_ultima_pagina_ou_tamanho_da_lista():
    ult = RespostaFalsa(200, [{}], {"Link": '<https://api.github.com/c?per_page=1&page=42>; rel="last"'})
    c, _, _ = cliente([ult, RespostaFalsa(200, [{}, {}][:1])])
    assert c.contar("/c", {"anon": "true"}) == 42
    assert c.contar("/d") == 1
    c2, _, _ = cliente([RespostaFalsa(404, {})])
    assert c2.contar("/z") == 0
