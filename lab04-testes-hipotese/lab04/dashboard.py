"""Monta o dashboard: página HTML única com as 7 seções pedidas no enunciado.

Todos os números dos textos vêm dos dados, para que texto e gráficos nunca divirjam.

Uso: python -m lab04.dashboard
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy import stats

from lab04 import cores
from lab04.caminhos import (
    CSV_REAIS, DASHBOARD, JSON_AMOSTRA, JSON_DADOS_REAIS, JSON_EXEMPLO, JSON_PARAMETROS, JSON_SIMULACOES,
)
from lab04.exemplo import formatar_numero as fmt
from lab04.exemplo import formatar_p
from lab04.graficos import grafico_g1, grafico_g2, simular_estatisticas_h0
from lab04.graficos_s02 import NOMES_TESTES, grafico_g3, grafico_g4
from lab04.simulacoes import margem_monte_carlo

LINK_REPOSITORIO = "https://github.com/matheustitton/lab01-repositorios-populares"
LINK_FONTE = f"{LINK_REPOSITORIO}/blob/main/lab04-testes-hipotese/dados/FONTE.md"
LINK_CENARIO = f"{LINK_REPOSITORIO}/blob/main/lab04-testes-hipotese/docs/cenario.md"
LINK_PROJECTS: str | None = 'https://github.com/users/matheustitton/projects/2'  # preencher com a URL do GitHub Projects do grupo
# GitHub Pages do repositório (Settings → Pages → Deploy from a branch → main / root).
LINK_DASHBOARD: str | None = (
    "https://matheustitton.github.io/lab01-repositorios-populares/lab04-testes-hipotese/dashboard/"
)

TITULOS_SECOES = [
    "1. Cenário",
    "2. Os dados",
    "3. Como os testes funcionam",
    "4. Erro tipo I",
    "5. Poder",
    "6. Dados reais",
    "7. Conclusão",
]

CSS = f"""
:root {{
  color-scheme: light;
  --superficie: {cores.SUPERFICIE};
  --fundo: {cores.FUNDO_PAGINA};
  --tinta: {cores.TINTA};
  --tinta-sec: {cores.TINTA_SECUNDARIA};
  --tinta-fraca: {cores.TINTA_FRACA};
  --grade: {cores.GRADE};
}}
* {{ box-sizing: border-box; }}
body {{
  margin: 0;
  background: var(--fundo);
  color: var(--tinta);
  font: 16px/1.55 system-ui, -apple-system, "Segoe UI", sans-serif;
}}
main, header {{ max-width: 1120px; margin: 0 auto; padding: 0 16px; }}
header {{ padding-top: 32px; }}
h1 {{ font-size: 1.75rem; line-height: 1.2; margin: 0 0 4px; text-wrap: balance; }}
h2 {{ font-size: 1.25rem; margin: 0 0 12px; }}
h3 {{ font-size: 1rem; margin: 20px 0 8px; }}
a {{ color: #1c5cab; }}
.subtitulo {{ color: var(--tinta-sec); margin: 0 0 12px; }}
.links {{ display: flex; flex-wrap: wrap; gap: 4px 24px; margin: 0 0 24px; padding: 0; list-style: none; }}
.a-preencher {{ color: var(--tinta-sec); font-style: italic; }}
section {{
  background: var(--superficie);
  border: 1px solid var(--grade);
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 16px;
}}
section > p {{ max-width: 76ch; }}
section > p:last-child {{ margin-bottom: 0; }}
.hipoteses {{ margin: 0 0 12px; padding-left: 20px; max-width: 76ch; }}
.graficos {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; margin: 16px 0; }}
.graficos > div {{ min-width: 0; }}
.rolagem {{ overflow-x: auto; margin: 12px 0; }}
table {{ border-collapse: collapse; width: 100%; font-size: 0.875rem; }}
caption {{ text-align: left; color: var(--tinta-sec); padding-bottom: 8px; }}
th, td {{ padding: 6px 12px 6px 0; border-bottom: 1px solid var(--grade); text-align: right; white-space: nowrap; }}
td {{ font-variant-numeric: tabular-nums; }}
th:first-child, td:first-child, .texto {{ text-align: left; }}
td.texto {{ white-space: normal; min-width: 180px; }}
footer {{ color: var(--tinta-sec); font-size: 0.875rem; text-align: center; padding: 8px 16px 32px; }}
@media (max-width: 900px) {{ .graficos {{ grid-template-columns: minmax(0, 1fr); }} }}
@media (max-width: 600px) {{ section {{ padding: 16px; }} h1 {{ font-size: 1.5rem; }} }}
"""


def resumir_amostra(horas: np.ndarray) -> dict:
    return {
        "n": len(horas),
        "mediana": float(np.median(horas)),
        "media": float(np.mean(horas)),
        "desvio": float(np.std(horas, ddof=1)),
        "maximo": float(np.max(horas)),
        "assimetria": float(stats.skew(horas)),
        "abaixo_1h": float(np.mean(horas < 1)),
    }


def _horas_reais(tabela: pd.DataFrame, grupo: str) -> np.ndarray:
    return tabela.loc[tabela["grupo"] == grupo, "horas_ate_merge"].to_numpy()


def _data_br(timestamp: str) -> str:
    ano, mes, dia = timestamp[:10].split("-")
    return f"{dia}/{mes}/{ano}"


def _figura_html(fig: go.Figure, div_id: str, carregar_plotly: bool) -> str:
    return fig.to_html(
        full_html=False,
        include_plotlyjs="cdn" if carregar_plotly else False,
        div_id=div_id,
        default_width="100%",
        config={"responsive": True, "displaylogo": False},
    )


def _tabela_dados(tabela: pd.DataFrame, exemplo: dict) -> str:
    linhas = []
    for grupo, rotulo in (("sem_bot", "Sem bot"), ("com_bot", "Com bot")):
        for origem, horas in (
            ("real", _horas_reais(tabela, grupo)),
            ("simulado", np.array(exemplo["grupos"][grupo])),
        ):
            r = resumir_amostra(horas)
            linhas.append(
                f"<tr><td>{rotulo}, {origem}</td><td>{r['n']}</td><td>{fmt(r['mediana'], 1)}</td>"
                f"<td>{fmt(r['media'], 1)}</td><td>{fmt(r['desvio'], 1)}</td><td>{fmt(r['maximo'], 1)}</td>"
                f"<td>{fmt(r['assimetria'])}</td><td>{fmt(100 * r['abaixo_1h'], 0)}%</td></tr>"
            )
    return (
        '<div class="rolagem"><table><caption>Resumo dos dados do G1, com tempos em horas. Cada grupo simulado é uma única '
        f"amostra de {len(exemplo['grupos']['sem_bot'])} PRs (k = {fmt(exemplo['fator'], 1)} no grupo com bot), a mesma "
        "usada na seção 3, então parte da diferença em relação ao real é acaso.</caption>"
        "<thead><tr><th>Grupo e origem</th><th>n</th><th>Mediana</th><th>Média</th><th>Desvio-padrão</th>"
        "<th>Máximo</th><th>Assimetria</th><th>Abaixo de 1 h</th></tr></thead>"
        f"<tbody>{''.join(linhas)}</tbody></table></div>"
    )


def _tabela_exemplo(exemplo: dict) -> str:
    alfa = exemplo["alfa"]
    linhas = []
    for nome, chave, simbolo, casas in (("t de Welch", "welch", "t", 2), ("Mann-Whitney", "mann_whitney", "U", 1)):
        r = exemplo[chave]
        decisao = "Rejeita H₀" if r["p_valor"] < alfa else "Não rejeita H₀"
        linhas.append(
            f"<tr><td>{nome}</td><td>{simbolo} = {fmt(r["estatistica"], casas)}</td><td>{formatar_p(r['p_valor'])}</td>"
            f'<td class="texto">{r["nome_efeito"]} = {fmt(r["efeito"])}</td><td class="texto">{decisao}</td></tr>'
        )
    return (
        '<div class="rolagem"><table>'
        f"<caption>Os dois testes aplicados ao conjunto simulado (n = {len(exemplo['grupos']['sem_bot'])} por grupo, "
        f"k = {fmt(exemplo['fator'], 1)})</caption>"
        '<thead><tr><th>Teste</th><th>Estatística</th><th>p-valor</th><th class="texto">Tamanho do efeito</th>'
        '<th class="texto">Decisão</th></tr></thead>'
        f"<tbody>{''.join(linhas)}</tbody></table></div>"
    )


def _cabecalho() -> str:
    dashboard = (
        f'<a href="{LINK_DASHBOARD}">Dashboard publicado</a>' if LINK_DASHBOARD
        else "Dashboard: gerado localmente com <code>python rodar.py</code>"
    )
    projects = (
        f'<a href="{LINK_PROJECTS}">GitHub Projects</a>' if LINK_PROJECTS
        else '<span class="a-preencher">GitHub Projects: link a preencher</span>'
    )
    return f"""<header>
  <h1>Testes de hipótese por dentro: t de Welch × Mann-Whitney</h1>
  <p class="subtitulo">Laboratório 04 · Laboratório de Experimentação de Software · Matheus, Pedro e Murilo · Sprint 2</p>
  <ul class="links">
    <li>{dashboard} (ou localmente com <code>python rodar.py</code>)</li>
    <li><a href="{LINK_REPOSITORIO}">Repositório</a></li>
    <li>{projects}</li>
  </ul>
</header>"""


def _secao_cenario(tabela: pd.DataFrame) -> str:
    sem_bot = tabela[tabela["grupo"] == "sem_bot"]
    com_bot = tabela[tabela["grupo"] == "com_bot"]
    return f"""<section id="secao-1">
  <h2>{TITULOS_SECOES[0]}</h2>
  <p><strong>Pergunta:</strong> adotar um bot de revisão (CodeRabbit) muda o tempo até o merge dos PRs?</p>
  <ul class="hipoteses">
    <li><strong>H₀:</strong> o tempo até o merge tem a mesma distribuição com e sem bot.</li>
    <li><strong>H₁:</strong> as distribuições diferem. O teste é bicaudal porque o bot pode acelerar a revisão, mas também pode gerar retrabalho.</li>
  </ul>
  <p><strong>Dados reais:</strong> {len(tabela)} PRs mergeados do repositório <code>formbricks/formbricks</code>, coletados pela API do GitHub ({len(sem_bot)} sem bot, criados de {_data_br(sem_bot["criado_em"].min())} a {_data_br(sem_bot["criado_em"].max())}, e {len(com_bot)} com bot, de {_data_br(com_bot["criado_em"].min())} a {_data_br(com_bot["criado_em"].max())}). A fase de transição foi excluída, pois nela o bot comentava só em parte dos PRs. Critérios e limitações estão em <a href="{LINK_FONTE}">dados/FONTE.md</a>, e o cenário completo está em <a href="{LINK_CENARIO}">docs/cenario.md</a>.</p>
</section>"""


def _secao_dados(tabela: pd.DataFrame, exemplo: dict, parametros: dict, graficos: str) -> str:
    real = resumir_amostra(_horas_reais(tabela, "sem_bot"))
    real_com = resumir_amostra(_horas_reais(tabela, "com_bot"))
    mediana, sigma = parametros["mediana_horas"], parametros["sigma_log"]
    amostral = parametros["sigma_log_amostral"]
    media_amostral = mediana * np.exp(amostral**2 / 2)
    abaixo_1h_teorico = stats.norm.cdf(-np.log(mediana) / sigma)
    return f"""<section id="secao-2">
  <h2>{TITULOS_SECOES[1]}</h2>
  <div class="graficos">{graficos}</div>
  <p>Os dados reais são muito assimétricos: sem bot, a média ({fmt(real["media"], 1)} h) é {fmt(real["media"] / real["mediana"], 1)} vezes a mediana ({fmt(real["mediana"], 1)} h), e o PR mais longo levou {fmt(real["maximo"], 0)} h. A simulação usa uma lognormal com a mediana real e σ = {fmt(sigma)}, valor que reproduz a razão média/mediana. O desvio-padrão do log (σ = {fmt(amostral)}) foi descartado para o cenário-base porque daria média teórica de cerca de {fmt(media_amostral, 0)} h, muito acima da real, e fica para o cenário de cauda pesada da S02. A principal diferença visível é à esquerda: a lognormal escolhida prevê {fmt(100 * abaixo_1h_teorico, 0)}% de PRs abaixo de 1 h, contra {fmt(100 * real["abaixo_1h"], 0)}% (sem bot) e {fmt(100 * real_com["abaixo_1h"], 0)}% (com bot) nos dados reais.</p>
  {_tabela_dados(tabela, exemplo)}
</section>"""


def _secao_testes(exemplo: dict, simulados: dict[str, np.ndarray], graficos: str) -> str:
    alfa = exemplo["alfa"]
    critico_t = stats.t(exemplo["welch"]["gl"]).isf(alfa / 2)
    critico_z = stats.norm.isf(alfa / 2)
    repeticoes = f"{len(simulados['welch']):,}".replace(",", ".")
    return f"""<section id="secao-3">
  <h2>{TITULOS_SECOES[2]}</h2>
  <div class="graficos">{graficos}</div>
  <p>O Welch compara médias, dividindo a diferença entre elas pelo erro-padrão, e o Mann-Whitney compara postos, com U padronizado em z. Como o teste é bicaudal, a região de rejeição fica nas duas pontas, além de ±{fmt(critico_t)} no Welch e ±{fmt(critico_z)} no Mann-Whitney, onde a estatística cairia só {fmt(100 * alfa, 0)}% das vezes se H₀ fosse verdadeira. O p-valor é a área colorida: a probabilidade, supondo H₀ verdadeira, de obter uma estatística tão extrema quanto a do exemplo ou mais, e não a probabilidade de H₀ ser verdadeira. O histograma cinza mostra a estatística em {repeticoes} conjuntos simulados sob H₀: no Mann-Whitney ele acompanha a curva teórica, e no Welch se afasta dela, com picos perto de ±1, porque um único PR muito longo domina tanto a diferença de médias quanto o erro-padrão.</p>
  <h3>Exemplo: os dois testes em um conjunto simulado</h3>
  {_tabela_exemplo(exemplo)}
  <p>{exemplo["interpretacao"]["welch"]}</p>
  <p>{exemplo["interpretacao"]["mann_whitney"]}</p>
  <p>Um único conjunto de dados não mostra qual teste é melhor: para isso servem as simulações repetidas das seções 4 e 5.</p>
</section>"""


def _pct(valor: float, casas: int = 1) -> str:
    return f"{fmt(100 * valor, casas)}%"


def _lista(itens: list[str]) -> str:
    if len(itens) <= 1:
        return "".join(itens)
    return ", ".join(itens[:-1]) + " e " + itens[-1]


def _situacao(simulacoes: dict, chave: str) -> dict:
    return next(s for s in simulacoes["situacoes"] if s["chave"] == chave)


def _poder_em(situacao: dict, reducoes: list[float], teste: str, reducao: float, alfa: float = 0.05) -> float:
    return situacao["poder"][teste][str(alfa)][reducoes.index(reducao)]


def _secao_erro_tipo1(simulacoes: dict, grafico: str) -> str:
    alfa = simulacoes["alfas"][0]
    margem = margem_monte_carlo(alfa, simulacoes["repeticoes"])
    situacoes = simulacoes["situacoes"]
    assimetricas = [s for s in situacoes if s["chave"] != "quase_simetrico"]
    taxas_mw = [s["erro_tipo1"]["mann_whitney"][str(alfa)] for s in situacoes]
    taxas_welch = [s["erro_tipo1"]["welch"][str(alfa)] for s in assimetricas]
    fora_mw = [s["rotulo"].lower() for s in situacoes if abs(s["erro_tipo1"]["mann_whitney"][str(alfa)] - alfa) > margem]
    contraste = _situacao(simulacoes, "quase_simetrico")["erro_tipo1"]["welch"][str(alfa)]
    pior = min(assimetricas, key=lambda s: s["erro_tipo1"]["welch"][str(alfa)])
    nota_mw = (
        f" A exceção é a {_lista(fora_mw)}, um pouco abaixo da faixa: com n pequeno a estatística U só assume "
        "poucos valores, e o teste fica levemente conservador."
        if fora_mw else ""
    )
    return f"""<section id="secao-4">
  <h2>{TITULOS_SECOES[3]}</h2>
  {grafico}
  <p>Com H₀ verdadeira, o Mann-Whitney rejeitou entre {_pct(min(taxas_mw))} e {_pct(max(taxas_mw))} das vezes, perto dos {_pct(alfa, 0)} esperados (a faixa cinza, de ±{fmt(100 * margem, 2)} ponto percentual, é a variação que {fmt(simulacoes["repeticoes"] / 1000, 0)} mil repetições produzem só por acaso).{nota_mw} O Welch se desviou em todas as situações assimétricas, sempre para baixo ({_pct(min(taxas_welch))} a {_pct(max(taxas_welch))}): é <strong>conservador</strong>, e o pior caso é a {pior["rotulo"].lower()}. O motivo é que um PR muito longo entra ao mesmo tempo na diferença de médias e no erro-padrão, então |t| quase nunca fica grande. Só com dados quase simétricos ele volta a {_pct(contraste)}. Errar menos que 5% parece bom, mas o preço aparece no poder, a seguir.</p>
</section>"""


def _frase_80(base: dict, reducoes: list[float]) -> str:
    """Primeira redução em que algum teste chega a 80% de poder no cenário-base."""
    alcancam = [
        (reducao, teste) for teste in ("mann_whitney", "welch")
        for reducao, valor in zip(reducoes, base["poder"][teste]["0.05"]) if valor >= 0.8
    ]
    if not alcancam:
        return (f"Com n = {base['n']}, nenhum teste chega a 80% de poder no cenário-base, nem com redução de "
                f"{_pct(reducoes[-1], 0)} na mediana.")
    reducao, teste = min(alcancam)
    return (f"Com n = {base['n']}, o primeiro a chegar a 80% de poder no cenário-base é o {NOMES_TESTES[teste]}, "
            f"com redução de {_pct(reducao, 0)}.")


def _secao_poder(simulacoes: dict, grafico: str) -> str:
    reducoes = simulacoes["reducoes"]
    base = _situacao(simulacoes, "base")
    cauda = _situacao(simulacoes, "cauda_pesada")
    contraste = _situacao(simulacoes, "quase_simetrico")
    meio = 0.5
    menor = reducoes[1]
    alfa_rigido = simulacoes["alfas"][-1]
    max_welch_cauda = max(cauda["poder"]["welch"]["0.05"])
    assimetricas = [s for s in simulacoes["situacoes"] if s["chave"] != "quase_simetrico"]
    mw_sempre_ganha = all(
        mw >= w for s in assimetricas
        for mw, w in zip(s["poder"]["mann_whitney"]["0.05"][1:], s["poder"]["welch"]["0.05"][1:])
    )
    vantagem = "Em todas as situações assimétricas" if mw_sempre_ganha else "Na maior parte das situações assimétricas"
    return f"""<section id="secao-5">
  <h2>{TITULOS_SECOES[4]}</h2>
  {grafico}
  <p>{vantagem}, o <strong>Mann-Whitney detecta melhor o efeito</strong>, e a distância cresce com o tamanho do efeito: no cenário-base, quando o bot corta a mediana pela metade, ele rejeita H₀ em {_pct(_poder_em(base, reducoes, "mann_whitney", meio))} dos conjuntos, contra {_pct(_poder_em(base, reducoes, "welch", meio))} do Welch. Na cauda pesada o Welch quase não sai do lugar (no máximo {_pct(max_welch_cauda)}), porque os PRs gigantes escondem qualquer diferença nas médias. A vantagem só muda de lado com dados quase simétricos, e por pouco: com redução de {_pct(menor, 0)}, Welch {_pct(_poder_em(contraste, reducoes, "welch", menor))} × Mann-Whitney {_pct(_poder_em(contraste, reducoes, "mann_whitney", menor))}. {_frase_80(base, reducoes)} Com α = {fmt(alfa_rigido)} (botão no gráfico), o erro tipo I cai para perto de 1%, mas o poder cai junto: no cenário-base, com redução de 50%, o Mann-Whitney vai a {_pct(_poder_em(base, reducoes, "mann_whitney", meio, alfa_rigido))} e o Welch a {_pct(_poder_em(base, reducoes, "welch", meio, alfa_rigido))}.</p>
</section>"""


def _tabela_dados_reais(reais: dict) -> str:
    linhas = []
    for chave, simbolo, casas in (("welch", "t", 2), ("mann_whitney", "U", 1)):
        r = reais[chave]
        conclusao = (
            "Rejeita H₀: os tempos diferem" if r["rejeita"]
            else "Não rejeita H₀: os dados não mostram diferença"
        )
        linhas.append(
            f"<tr><td>{NOMES_TESTES[chave]}</td><td>{simbolo} = {fmt(r['estatistica'], casas)}</td>"
            f"<td>{formatar_p(r['p_valor'])}</td>"
            f'<td class="texto">{r["nome_efeito"]} = {fmt(r["efeito"])} ({r["magnitude"]})</td>'
            f'<td class="texto">{conclusao}</td></tr>'
        )
    return (
        '<div class="rolagem"><table>'
        f"<caption>Os dois testes nos {reais['n']['sem_bot'] + reais['n']['com_bot']} PRs reais "
        f"(α = {fmt(reais['alfa'])}, bicaudal). Efeito positivo indica PRs mais lentos sem bot.</caption>"
        '<thead><tr><th>Teste</th><th>Estatística</th><th>p-valor</th><th class="texto">Tamanho do efeito</th>'
        '<th class="texto">Conclusão</th></tr></thead>'
        f"<tbody>{''.join(linhas)}</tbody></table></div>"
    )


def _tabela_amostra(amostra: dict) -> str:
    linhas = "".join(
        f"<tr><td>{n}</td><td>{_pct(w)}</td><td>{_pct(m)}</td></tr>"
        for n, w, m in zip(amostra["tamanhos"], amostra["poder"]["welch"], amostra["poder"]["mann_whitney"])
    )
    return (
        '<div class="rolagem"><table>'
        f"<caption>Poder para detectar a redução observada ({_pct(amostra['reducao_observada'], 0)} na mediana), "
        f"no cenário-base, com {fmt(amostra['repeticoes'] / 1000, 0)} mil conjuntos por linha</caption>"
        "<thead><tr><th>PRs por grupo</th><th>Poder do Welch</th><th>Poder do Mann-Whitney</th></tr></thead>"
        f"<tbody>{linhas}</tbody></table></div>"
    )


def _faixa_n(amostra: dict, teste: str) -> str:
    n = amostra["n_para_alvo"][teste]
    tamanhos = amostra["tamanhos"]
    if n is None:
        return f"mais de {tamanhos[-1]:,}".replace(",", ".")
    indice = tamanhos.index(n)
    if indice == 0:
        return f"{n}"
    return f"entre {tamanhos[indice - 1]:,} e {n:,}".replace(",", ".")


def _secao_dados_reais(reais: dict, amostra: dict) -> str:
    mediana_a, mediana_b = reais["mediana"]["sem_bot"], reais["mediana"]["com_bot"]
    media_a, media_b = reais["media"]["sem_bot"], reais["media"]["com_bot"]
    ic_med = reais["ic_diferenca_medianas"]
    mesma = reais["welch"]["rejeita"] == reais["mann_whitney"]["rejeita"]
    concordancia = (
        "Os dois testes chegam à mesma conclusão: não rejeitam H₀."
        if mesma and not reais["welch"]["rejeita"]
        else "Os dois testes chegam à mesma conclusão: rejeitam H₀." if mesma
        else "Os testes discordam, o que é esperado quando os dados são tão assimétricos."
    )
    poder_real = amostra["poder_com_n_real"]
    return f"""<section id="secao-6">
  <h2>{TITULOS_SECOES[5]}</h2>
  {_tabela_dados_reais(reais)}
  <p>{concordancia} As médias são praticamente iguais ({fmt(media_a, 1)} h sem bot e {fmt(media_b, 1)} h com bot), mas a mediana caiu de {fmt(mediana_a, 1)} h para {fmt(mediana_b, 1)} h ({_pct(1 - reais["razao_medianas"], 0)} a menos). Isso mostra que os testes respondem perguntas diferentes: o Welch olha a média, que é a mesma, e o Mann-Whitney olha a ordem, que mudou um pouco. Na prática, a diferença de medianas tem intervalo de confiança bootstrap de {fmt(ic_med[0], 1)} h a {fmt(ic_med[1], 1)} h: o bot pode tanto adiantar o merge em mais de um dia quanto atrasá-lo, então não dá para afirmar importância prática em nenhuma direção.</p>
  <h3>Para discutir: o tamanho da amostra</h3>
  <p>Não rejeitar H₀ não prova que o bot não tem efeito. Se a redução real fosse a observada ({_pct(1 - reais["razao_medianas"], 0)} na mediana), com {reais["n"]["sem_bot"]} PRs por grupo o Mann-Whitney a detectaria só {_pct(poder_real["mann_whitney"], 0)} das vezes e o Welch {_pct(poder_real["welch"], 0)}. Para chegar a 80% de poder seriam necessários {_faixa_n(amostra, "mann_whitney")} PRs por grupo com Mann-Whitney e {_faixa_n(amostra, "welch")} com Welch. No formbricks isso significaria janelas de vários meses antes e depois do bot, o que mistura outras mudanças do projeto: a amostra pequena é a principal limitação deste resultado. Com amostras grandes vale o contrário: quase qualquer diferença vira "significativa", e o que importa passa a ser o tamanho do efeito.</p>
  {_tabela_amostra(amostra)}
</section>"""


def _secao_conclusao(simulacoes: dict, reais: dict) -> str:
    base = _situacao(simulacoes, "base")
    alfa = str(simulacoes["alfas"][0])
    return f"""<section id="secao-7">
  <h2>{TITULOS_SECOES[6]}</h2>
  <p><strong>O que esperávamos antes de simular:</strong> o Mann-Whitney com mais poder que o Welch, porque poucos PRs longos inflam a variância usada pelo Welch; no erro tipo I, o Mann-Whitney perto de 5% e o Welch abaixo disso.</p>
  <p><strong>O que encontramos:</strong> a expectativa se confirmou, e com mais força do que imaginávamos. O Welch ficou bem abaixo de 5% (de {_pct(base["erro_tipo1"]["welch"][alfa])} no cenário-base a {_pct(_situacao(simulacoes, "cauda_pesada")["erro_tipo1"]["welch"][alfa])} na cauda pesada), e esse conservadorismo veio junto com pouco poder. O que não esperávamos é que, nos dados reais, as médias fossem iguais enquanto a mediana caía {_pct(1 - reais["razao_medianas"], 0)}: um caso concreto em que os dois testes medem coisas diferentes.</p>
  <p><strong>Recomendação:</strong> para o tempo até o merge, usar o <strong>Mann-Whitney</strong>. Ele mantém o erro tipo I no nível prometido e detecta melhor o efeito em todas as situações realistas que simulamos. A escolha mudaria se a pergunta fosse sobre a <em>média</em> (por exemplo, o total de horas que a equipe gasta esperando merge, em que os PRs longos importam de verdade) ou se os dados fossem quase simétricos, como no contraste, onde o Welch empata ou ganha por pouco. Muitos empates (tempo medido em dias inteiros, por exemplo) também pediriam cuidado com o Mann-Whitney.</p>
  <p><strong>Limitações:</strong> o estudo real é antes e depois, sem grupo de controle; 30 PRs por grupo dão pouco poder; e a lognormal não reproduz o excesso de PRs mergeados em minutos.</p>
</section>"""


def gerar_html(
    tabela: pd.DataFrame,
    exemplo: dict,
    parametros: dict,
    simulados: dict[str, np.ndarray],
    simulacoes: dict,
    reais: dict,
    amostra: dict,
) -> str:
    g1 = grafico_g1(tabela, exemplo)
    g2 = grafico_g2(exemplo, simulados)
    html_g1 = "".join(
        f"<div>{_figura_html(fig, f'g1-{i}', carregar_plotly=i == 0)}</div>" for i, fig in enumerate(g1)
    )
    html_g2 = "".join(f"<div>{_figura_html(fig, f'g2-{i}', carregar_plotly=False)}</div>" for i, fig in enumerate(g2))
    html_g3 = _figura_html(grafico_g3(simulacoes), "g3", carregar_plotly=False)
    html_g4 = _figura_html(grafico_g4(simulacoes), "g4", carregar_plotly=False)
    secoes = [
        _secao_cenario(tabela),
        _secao_dados(tabela, exemplo, parametros, html_g1),
        _secao_testes(exemplo, simulados, html_g2),
        _secao_erro_tipo1(simulacoes, html_g3),
        _secao_poder(simulacoes, html_g4),
        _secao_dados_reais(reais, amostra),
        _secao_conclusao(simulacoes, reais),
    ]
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Lab04: Welch × Mann-Whitney</title>
<style>{CSS}</style>
</head>
<body>
{_cabecalho()}
<main>
{chr(10).join(secoes)}
</main>
<footer>Gerado por <code>python rodar.py</code> com semente {parametros["semente"]}.</footer>
</body>
</html>
"""


def main() -> Path:
    tabela = pd.read_csv(CSV_REAIS)
    ler = lambda caminho: json.loads(caminho.read_text(encoding="utf-8"))  # noqa: E731
    parametros = ler(JSON_PARAMETROS)
    html = gerar_html(
        tabela, ler(JSON_EXEMPLO), parametros, simular_estatisticas_h0(parametros),
        ler(JSON_SIMULACOES), ler(JSON_DADOS_REAIS), ler(JSON_AMOSTRA),
    )
    DASHBOARD.mkdir(parents=True, exist_ok=True)
    caminho = DASHBOARD / "index.html"
    caminho.write_text(html, encoding="utf-8", newline="\n")
    print(f"Dashboard em {caminho}")
    return caminho


if __name__ == "__main__":
    main()
