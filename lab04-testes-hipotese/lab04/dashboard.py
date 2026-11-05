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
from lab04.caminhos import CSV_REAIS, DASHBOARD, JSON_EXEMPLO, JSON_PARAMETROS
from lab04.exemplo import formatar_numero as fmt
from lab04.exemplo import formatar_p
from lab04.graficos import grafico_g1, grafico_g2, simular_estatisticas_h0

LINK_REPOSITORIO = "https://github.com/matheustitton/lab01-repositorios-populares"
LINK_FONTE = f"{LINK_REPOSITORIO}/blob/main/lab04-testes-hipotese/dados/FONTE.md"
LINK_CENARIO = f"{LINK_REPOSITORIO}/blob/main/lab04-testes-hipotese/docs/cenario.md"
LINK_PROJECTS: str | None = 'https://github.com/users/matheustitton/projects/2'  # preencher com a URL do GitHub Projects do grupo
LINK_DASHBOARD: str | None = None  # preencher se o dashboard for publicado

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
.pendente {{ color: var(--tinta-sec); border-left: 3px solid var(--grade); padding-left: 12px; }}
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
  <p class="subtitulo">Laboratório 04 · Laboratório de Experimentação de Software · Matheus, Pedro e Murilo · Sprint 1</p>
  <ul class="links">
    <li>{dashboard}</li>
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
  <p>Um único conjunto de dados não mostra qual teste é melhor: isso depende das simulações repetidas da Sprint 2.</p>
</section>"""


def _secao_pendente(numero: int, entrega: str, descricao: str, extra: str = "") -> str:
    return f"""<section id="secao-{numero}">
  <h2>{TITULOS_SECOES[numero - 1]}</h2>
  {extra}<p class="pendente">Pendente ({entrega}): {descricao}</p>
</section>"""


def gerar_html(tabela: pd.DataFrame, exemplo: dict, parametros: dict, simulados: dict[str, np.ndarray]) -> str:
    g1 = grafico_g1(tabela, exemplo)
    g2 = grafico_g2(exemplo, simulados)
    html_g1 = "".join(
        f"<div>{_figura_html(fig, f'g1-{i}', carregar_plotly=i == 0)}</div>" for i, fig in enumerate(g1)
    )
    html_g2 = "".join(f"<div>{_figura_html(fig, f'g2-{i}', carregar_plotly=False)}</div>" for i, fig in enumerate(g2))
    expectativa = (
        "<p><strong>Expectativa antes de simular:</strong> o Mann-Whitney deve ter mais poder que o Welch, porque poucos "
        "PRs longos inflam a variância usada pelo Welch. No erro tipo I, esperamos o Mann-Whitney perto de 5% e o Welch "
        "abaixo disso.</p>\n  "
    )
    secoes = [
        _secao_cenario(tabela),
        _secao_dados(tabela, exemplo, parametros, html_g1),
        _secao_testes(exemplo, simulados, html_g2),
        _secao_pendente(4, "Sprint 2", "gráfico G3, com o erro tipo I dos dois testes em cada situação simulada."),
        _secao_pendente(5, "Sprint 2", "gráfico G4, com as curvas de poder dos dois testes."),
        _secao_pendente(6, "Entrega final", "tabela com estatística, p-valor, tamanho do efeito e conclusão nos dados reais."),
        _secao_pendente(7, "Entrega final", "comparação com o resultado das simulações e recomendação de qual teste usar.", expectativa),
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
    exemplo = json.loads(JSON_EXEMPLO.read_text(encoding="utf-8"))
    parametros = json.loads(JSON_PARAMETROS.read_text(encoding="utf-8"))
    html = gerar_html(tabela, exemplo, parametros, simular_estatisticas_h0(parametros))
    DASHBOARD.mkdir(parents=True, exist_ok=True)
    caminho = DASHBOARD / "index.html"
    caminho.write_text(html, encoding="utf-8", newline="\n")
    print(f"Dashboard em {caminho}")
    return caminho


if __name__ == "__main__":
    main()
