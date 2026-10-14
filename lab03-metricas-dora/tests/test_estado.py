from pipeline.estado import ETAPAS, RepoStore, funil_markdown


def metas(*nomes):
    return [{"repo": n, "estrelas": 1000, "linguagem": "Go", "criado_em": "2020-01-01T00:00:00Z",
             "default_branch": "main"} for n in nomes]


def test_funil_e_motivos_de_descarte():
    s = RepoStore(":memory:")
    assert s.adicionar_candidatos(metas("a/1", "a/2", "a/3", "a/4", "a/5")) == 5
    assert s.adicionar_candidatos(metas("a/1")) == 0                    # sem duplicar
    s.descartar("a/1", "sem_actions")                                  # parou na etapa 0
    for r in ("a/2", "a/3", "a/4", "a/5"):
        s.avancar(r, 1)
    s.descartar("a/2", "releases_insuficientes")                      # parou na etapa 1
    for r in ("a/3", "a/4", "a/5"):
        s.avancar(r, 2)
    s.descartar("a/3", "runs_insuficientes")                          # parou na etapa 2
    for r in ("a/4", "a/5"):
        s.avancar(r, 3)
    s.salvar_coleta("a/4", {"meta": {}})                              # a/5 segue pendente na etapa 3
    contagens = [n for _, n in s.funil()]
    assert contagens == [5, 4, 3, 2, 1] and len(contagens) == len(ETAPAS)
    assert s.descartes() == {"sem_actions": 1, "releases_insuficientes": 1, "runs_insuficientes": 1}
    assert s.contar_incluidos() == 1 and s.incluidos()[0][0] == "a/4"
    md = funil_markdown(s)
    assert "sem_actions" in md and "| 5 |" in md


def test_pendentes_em_ordem_reprodutivel_e_sem_decididos():
    s = RepoStore(":memory:")
    s.adicionar_candidatos(metas(*[f"o/{i}" for i in range(20)]))
    s.descartar("o/3", "sem_actions"); s.salvar_coleta("o/4", {})
    a = [m["repo"] for m in s.pendentes(42)]
    assert a == [m["repo"] for m in s.pendentes(42)] and a != [m["repo"] for m in s.pendentes(7)]
    assert "o/3" not in a and "o/4" not in a and len(a) == 18


def test_estado_persiste_em_arquivo(tmp_path):
    arq = str(tmp_path / "e.sqlite")
    RepoStore(arq).adicionar_candidatos(metas("a/1"))
    assert RepoStore(arq).total() == 1
