"""Gráficos G3 (erro tipo I) e G4 (curvas de poder) do dashboard, a partir de saida/simulacoes_s02.json.

Os dois gráficos têm botões para trocar α entre 0,05 e 0,01 (pergunta 12 da apresentação).
"""
from __future__ import annotations

import math

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from lab04 import cores
from lab04.exemplo import formatar_numero
from lab04.graficos import estilizar
from lab04.simulacoes import margem_monte_carlo

NOMES_TESTES = {"welch": "t de Welch", "mann_whitney": "Mann-Whitney"}
CORES_TESTES = {"welch": cores.COR_WELCH, "mann_whitney": cores.COR_MANN_WHITNEY}
# Além da cor, cada teste tem marcador e traço próprios, para não depender só da cor.
MARCADORES = {"welch": "circle", "mann_whitney": "square"}
TRACOS = {"welch": "solid", "mann_whitney": "dash"}
PODER_REFERENCIA = 0.8
COLUNAS_G4 = 3


def _pct(valor: float, casas: int = 1) -> str:
    return f"{formatar_numero(100 * valor, casas)}%"


def _linha_horizontal(y: float, texto: str, xref: str = "paper", yref: str = "y", tracejado: str = "dot") -> tuple:
    forma = {
        "type": "line", "xref": xref, "yref": yref, "x0": 0, "x1": 1, "y0": y, "y1": y,
        "line": {"color": cores.TINTA, "width": 1.5, "dash": tracejado},
    }
    rotulo = {
        "xref": xref, "yref": yref, "x": 0, "y": y, "text": texto, "showarrow": False,
        "xanchor": "left", "yanchor": "bottom", "font": {"color": cores.TINTA, "size": 11},
    }
    return forma, rotulo


def _botoes_alfa(alfas: list[float], visiveis: dict[float, list[bool]], layouts: dict[float, dict]) -> list[dict]:
    return [{
        "type": "buttons",
        "direction": "right",
        "x": 1, "xanchor": "right", "y": 1.02, "yanchor": "bottom", "pad": {"t": 0, "b": 10},
        "showactive": True,
        "bgcolor": cores.SUPERFICIE,
        "bordercolor": cores.EIXO,
        "font": {"color": cores.TINTA},
        "buttons": [
            {"label": f"α = {formatar_numero(alfa)}", "method": "update", "args": [{"visible": visiveis[alfa]}, layouts[alfa]]}
            for alfa in alfas
        ],
    }]


def grafico_g3(simulacoes: dict) -> go.Figure:
    """Barras agrupadas: erro tipo I de cada teste em cada situação, com a margem da simulação."""
    alfas = simulacoes["alfas"]
    repeticoes = simulacoes["repeticoes"]
    rotulos = [s["rotulo"] for s in simulacoes["situacoes"]]
    fig = go.Figure()
    visiveis: dict[float, list[bool]] = {alfa: [] for alfa in alfas}
    for alfa in alfas:
        for teste in NOMES_TESTES:
            taxas = [s["erro_tipo1"][teste][str(alfa)] for s in simulacoes["situacoes"]]
            fig.add_bar(
                x=rotulos,
                y=taxas,
                name=NOMES_TESTES[teste],
                legendgroup=teste,
                visible=alfa == alfas[0],
                marker={"color": CORES_TESTES[teste], "pattern": {"shape": "" if teste == "welch" else "/"}},
                text=[_pct(t) for t in taxas],
                textposition="outside",
                cliponaxis=False,
                hovertemplate="%{x}<br>%{text} dos conjuntos rejeitaram H₀<extra>" + NOMES_TESTES[teste] + "</extra>",
            )
            for a in alfas:
                visiveis[a].append(a == alfa)
    layouts = {}
    for alfa in alfas:
        margem = margem_monte_carlo(alfa, repeticoes)
        forma, rotulo = _linha_horizontal(alfa, f"α = {_pct(alfa, 0)}: faixa cinza = variação esperada só pelo acaso")
        faixa = {
            "type": "rect", "xref": "paper", "yref": "y", "x0": 0, "x1": 1, "y0": alfa - margem, "y1": alfa + margem,
            "fillcolor": cores.com_opacidade(cores.TINTA_FRACA, 0.18), "line": {"width": 0}, "layer": "below",
        }
        rotulo["y"] = alfa + margem
        layouts[alfa] = {
            "shapes": [faixa, forma], "annotations": [rotulo],
            "yaxis.range": [0, alfa * 1.5],
        }
    estilizar(
        fig,
        "G3 · Erro tipo I: rejeições com H₀ verdadeira",
        "Situação simulada",
        "Proporção de rejeições de H₀",
    )
    primeiro = alfas[0]
    fig.update_layout(
        barmode="group", bargap=0.25, bargroupgap=0.05, barcornerradius=3,
        shapes=layouts[primeiro]["shapes"], annotations=layouts[primeiro]["annotations"],
        updatemenus=_botoes_alfa(alfas, visiveis, layouts), margin={"t": 64},
    )
    fig.update_yaxes(range=layouts[primeiro]["yaxis.range"], tickformat=".1%")
    fig.update_xaxes(showgrid=False)
    return fig


def grafico_g4(simulacoes: dict) -> go.Figure:
    """Uma curva de poder por teste, em um painel por situação, com o mesmo eixo em todos."""
    alfas = simulacoes["alfas"]
    situacoes = simulacoes["situacoes"]
    reducoes_pct = [100 * r for r in simulacoes["reducoes"]]
    linhas = math.ceil(len(situacoes) / COLUNAS_G4)
    fig = make_subplots(
        rows=linhas, cols=COLUNAS_G4, shared_yaxes=True,
        subplot_titles=[s["rotulo"] for s in situacoes],
        horizontal_spacing=0.05, vertical_spacing=0.16,
    )
    visiveis: dict[float, list[bool]] = {alfa: [] for alfa in alfas}
    for indice, situacao in enumerate(situacoes):
        linha, coluna = indice // COLUNAS_G4 + 1, indice % COLUNAS_G4 + 1
        for alfa in alfas:
            for teste in NOMES_TESTES:
                fig.add_scatter(
                    x=reducoes_pct,
                    y=situacao["poder"][teste][str(alfa)],
                    mode="lines+markers",
                    name=NOMES_TESTES[teste],
                    legendgroup=teste,
                    showlegend=indice == 0 and alfa == alfas[0],
                    visible=alfa == alfas[0],
                    line={"color": CORES_TESTES[teste], "width": 2, "dash": TRACOS[teste]},
                    marker={"symbol": MARCADORES[teste], "size": 6},
                    hovertemplate=(
                        f"{situacao['rotulo']}<br>redução de %{{x:.0f}}% na mediana"
                        "<br>poder %{y:.1%}<extra>" + NOMES_TESTES[teste] + "</extra>"
                    ),
                    row=linha, col=coluna,
                )
                for a in alfas:
                    visiveis[a].append(a == alfa)
    estilizar(
        fig,
        "G4 · Poder: proporção de rejeições × tamanho do efeito",
        "Redução da mediana do tempo até o merge (%)",
        "Proporção de rejeições (poder)",
    )
    titulos = list(fig.layout.annotations)
    layouts = {}
    for alfa in alfas:
        formas = []
        for indice in range(len(situacoes)):
            sufixo = "" if indice == 0 else str(indice + 1)
            for y, tracejado in ((alfa, "dot"), (PODER_REFERENCIA, "dash")):
                forma, _ = _linha_horizontal(y, "", xref=f"x{sufixo} domain", yref=f"y{sufixo}", tracejado=tracejado)
                forma["line"]["color"] = cores.TINTA_FRACA
                forma["line"]["width"] = 1
                formas.append(forma)
        legenda_linhas = {
            "xref": "paper", "yref": "paper", "x": 1, "y": 0.02, "xanchor": "right", "yanchor": "bottom",
            "showarrow": False, "align": "right", "font": {"color": cores.TINTA_SECUNDARIA, "size": 11},
            "text": f"pontilhado: α = {formatar_numero(alfa)}<br>tracejado: poder de 80%",
        }
        layouts[alfa] = {"shapes": formas, "annotations": titulos + [legenda_linhas]}
    primeiro = alfas[0]
    fig.update_layout(
        height=330 * linhas + 170,
        shapes=layouts[primeiro]["shapes"],
        annotations=layouts[primeiro]["annotations"],
        updatemenus=_botoes_alfa(alfas, visiveis, layouts),
        margin={"t": 96, "b": 90},
        # O sexto painel fica vazio: a legenda vai para lá, longe dos eixos.
        legend={"orientation": "v", "x": 0.72, "xanchor": "left", "y": 0.36, "yanchor": "top"},
    )
    for anotacao in fig.layout.annotations[: len(situacoes)]:
        anotacao.font = {"size": 13, "color": cores.TINTA}
    fig.update_yaxes(range=[0, 1.05], tickformat=".0%", dtick=0.2)
    fig.update_xaxes(range=[-3, max(reducoes_pct) + 3], dtick=10)
    # Título do eixo x só no painel de baixo de cada coluna, e do eixo y só na primeira coluna.
    ultimos_por_coluna = {i % COLUNAS_G4: i for i in range(len(situacoes))}.values()
    for indice in range(linhas * COLUNAS_G4):
        sufixo = "" if indice == 0 else str(indice + 1)
        eixo_x, eixo_y = fig.layout[f"xaxis{sufixo}"], fig.layout[f"yaxis{sufixo}"]
        if indice >= len(situacoes):
            eixo_x.visible = eixo_y.visible = False
            continue
        eixo_x.title.text = "Redução da mediana (%)" if indice in ultimos_por_coluna else None
        eixo_y.title.text = "Poder" if indice % COLUNAS_G4 == 0 else None
    return fig


def grafico_amostra(amostra: dict) -> go.Figure:
    """Poder de cada teste para detectar o efeito observado, conforme cresce o n por grupo."""
    tamanhos = amostra["tamanhos"]
    fig = go.Figure()
    for teste in NOMES_TESTES:
        fig.add_scatter(
            x=tamanhos,
            y=amostra["poder"][teste],
            mode="lines+markers",
            name=NOMES_TESTES[teste],
            line={"color": CORES_TESTES[teste], "width": 2, "dash": TRACOS[teste]},
            marker={"symbol": MARCADORES[teste], "size": 7},
            hovertemplate="%{x} PRs por grupo<br>poder %{y:.1%}<extra>" + NOMES_TESTES[teste] + "</extra>",
        )
    alvo = amostra["poder_alvo"]
    n_real = tamanhos[0]
    estilizar(
        fig,
        f"Poder para detectar a redução observada ({_pct(amostra['reducao_observada'], 0)} na mediana)",
        "PRs por grupo",
        "Proporção de rejeições (poder)",
    )
    fig.update_layout(
        height=400,
        shapes=[
            {"type": "line", "xref": "paper", "x0": 0, "x1": 1, "y0": alvo, "y1": alvo,
             "line": {"color": cores.TINTA_FRACA, "width": 1, "dash": "dash"}},
            {"type": "line", "yref": "paper", "x0": n_real, "x1": n_real, "y0": 0, "y1": 1,
             "line": {"color": cores.TINTA_FRACA, "width": 1, "dash": "dot"}},
        ],
        annotations=[
            {"xref": "paper", "x": 1, "y": alvo, "text": f"meta de {_pct(alvo, 0)}", "showarrow": False,
             "xanchor": "right", "yanchor": "bottom", "font": {"color": cores.TINTA_SECUNDARIA, "size": 11}},
            {"x": n_real, "yref": "paper", "y": 1, "text": f"n coletado: {n_real}", "showarrow": False,
             "xanchor": "left", "yanchor": "top", "xshift": 4, "font": {"color": cores.TINTA_SECUNDARIA, "size": 11}},
        ],
    )
    fig.update_yaxes(range=[0, 1.02], tickformat=".0%", dtick=0.2)
    fig.update_xaxes(rangemode="tozero")
    return fig
