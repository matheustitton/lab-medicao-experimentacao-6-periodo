from pipeline.cache import Cache, chave_requisicao


def test_cache_ida_e_volta_e_persistencia(tmp_path):
    arq = str(tmp_path / "c.sqlite")
    Cache(arq).salvar("k", 200, {"a": 1}, {"next": "x"})
    assert Cache(arq).obter("k") == (200, {"a": 1}, {"next": "x"})   # outra instância = retomada
    assert Cache(arq).obter("outra") is None and Cache(arq).total() == 1


def test_chave_ignora_ordem_dos_parametros():
    assert chave_requisicao("/x", {"b": 2, "a": 1}) == chave_requisicao("/x", {"a": 1, "b": 2})
