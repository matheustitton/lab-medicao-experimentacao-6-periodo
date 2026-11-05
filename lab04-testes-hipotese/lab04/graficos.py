"""Gráficos G1 (dados reais × simulados) e G2 (estatística sob H0) do dashboard."""
from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy import stats

from lab04 import cores
from lab04.exemplo import formatar_numero, formatar_p
from lab04.simulacao import gerar_grupos

REPETICOES_G2 = 10_000
# Bordas dos bins do G1 em log10(horas): meia década, de 3,6 s a 10.000 h.
BORDAS_LOG10 = np.arange(-3, 4.5, 0.5)
LIMITE_VISIVEL = 5.0
# As caudas seguem até onde a densidade é desprezível, para a área sombreada ser igual ao p.
LIMITE_CAUDA = 60.0
PONTOS_CAUDA = 301

ROTULOS_GRUPO = {"sem_bot": "Sem bot", "com_bot": "Com bot"}


def estilizar(fig: go.Figure, titulo: str, eixo_x: str, eixo_y: str) -> go.Figure:
    fig.update_layout(
        template="none",
        title={"text": titulo, "x": 0, "xref": "paper", "font": {"size": 15, "color": cores.TINTA}},
        font={"family": 'system-ui, -apple-system, "Segoe UI", sans-serif', "size": 12, "color": cores.TINTA_SECUNDARIA},
        separators=",.",
        paper_bgcolor=cores.SUPERFICIE,
        plot_bgcolor=cores.SUPERFICIE,
        height=470,
        margin={"l": 56, "r": 16, "t": 48, "b": 124},
        legend={"orientation": "h", "x": 0, "y": -0.2, "yanchor": "top"},
        hoverlabel={"bgcolor": cores.SUPERFICIE, "font": {"color": cores.TINTA}},
    )
    eixos = {"gridcolor": cores.GRADE, "linecolor": cores.EIXO, "zeroline": False, "automargin": True}
    fig.update_xaxes(title={"text": eixo_x}, **eixos)
    fig.update_yaxes(title={"text": eixo_y}, **eixos)
    return fig


def contar_em_bins(horas: np.ndarray) -> np.ndarray:
    """Conta PRs por bin; tempos fora da faixa entram no primeiro ou no último bin."""
    log_horas = np.clip(np.log10(np.maximum(horas, 1e-9)), BORDAS_LOG10[0], BORDAS_LOG10[-1] - 1e-9)
    contagens, _ = np.histogram(log_horas, bins=BORDAS_LOG10)
    return contagens


def _formatar_horas(horas: float) -> str:
    return f"{horas:.3g}".replace(".", ",")


def grafico_g1(tabela: pd.DataFrame, exemplo: dict) -> list[go.Figure]:
    """Um histograma por grupo, com real e simulado nos mesmos bins."""
    centros = (BORDAS_LOG10[:-1] + BORDAS_LOG10[1:]) / 2
    faixas = [
        f"{_formatar_horas(10**inicio)} a {_formatar_horas(10**fim)} h"
        for inicio, fim in zip(BORDAS_LOG10[:-1], BORDAS_LOG10[1:])
    ]
    series = {
        grupo: {
            "Dados reais": contar_em_bins(tabela.loc[tabela["grupo"] == grupo, "horas_ate_merge"].to_numpy()),
            "Dados simulados": contar_em_bins(np.array(exemplo["grupos"][grupo])),
        }
        for grupo in ROTULOS_GRUPO
    }
    teto = max(int(contagens.max()) for grupo in series.values() for contagens in grupo.values()) + 1
    marcas = list(range(-2, 4))
    rotulos_marcas = ["0,01", "0,1", "1", "10", "100", "1.000"]

    figuras = []
    for grupo, rotulo in ROTULOS_GRUPO.items():
        fig = go.Figure()
        for nome, cor in (("Dados reais", cores.COR_REAL), ("Dados simulados", cores.COR_SIMULADO)):
            fig.add_bar(
                x=centros,
                y=series[grupo][nome],
                name=nome,
                marker={"color": cor, "line": {"color": cores.SUPERFICIE, "width": 1}},
                customdata=faixas,
                hovertemplate="%{customdata}<br>%{y} PRs<extra>" + nome + "</extra>",
            )
        estilizar(fig, f"G1 · {rotulo}: real × simulado", "Tempo até o merge (horas, escala log)", "Quantidade de PRs")
        fig.update_layout(barmode="group", bargap=0.2, bargroupgap=0.05, barcornerradius=3)
        fig.update_xaxes(tickvals=marcas, ticktext=rotulos_marcas, range=[BORDAS_LOG10[0], BORDAS_LOG10[-1]], showgrid=False)
        fig.update_yaxes(range=[0, teto], dtick=2, rangemode="tozero")
        figuras.append(fig)
    return figuras


def simular_estatisticas_h0(parametros: dict, repeticoes: int = REPETICOES_G2) -> dict[str, np.ndarray]:
    """Estatística de cada teste em conjuntos de dados gerados com H0 verdadeira."""
    rng = np.random.default_rng(parametros["semente"] + 1)
    n = parametros["n_por_grupo"]
    a, b = gerar_grupos(rng, parametros["mediana_horas"], parametros["sigma_log"], n, n, repeticoes=repeticoes)
    welch = stats.ttest_ind(a, b, axis=1, equal_var=False).statistic
    # Sem empates em dados contínuos, o z do Mann-Whitney tem desvio de forma fechada.
    u_a = stats.mannwhitneyu(a, b, axis=1, alternative="two-sided").statistic
    diferenca = u_a - n * n / 2
    z = (diferenca - 0.5 * np.sign(diferenca)) / np.sqrt(n * n * (2 * n + 1) / 12)
    return {"welch": welch, "mann_whitney": z}


def _cauda_direita(inicio: float) -> np.ndarray:
    """Pontos mais densos perto de `inicio`, onde a densidade varia mais."""
    return inicio + np.expm1(np.linspace(0, np.log1p(LIMITE_CAUDA - inicio), PONTOS_CAUDA))


def _sombrear_duas_caudas(fig: go.Figure, densidade, inicio: float, nome: str, cor: str, grupo: str) -> None:
    direita = _cauda_direita(inicio)
    for x, mostrar in ((direita, True), (-direita[::-1], False)):
        fig.add_scatter(
            x=x,
            y=densidade(x),
            mode="lines",
            line={"width": 0},
            fill="tozeroy",
            fillcolor=cor,
            name=nome,
            legendgroup=grupo,
            showlegend=mostrar,
            hoverinfo="skip",
            meta=grupo,
        )


def _painel_g2(
    titulo: str,
    eixo_x: str,
    rotulo: str,
    distribuicao,
    nome_curva: str,
    cor: str,
    observado: float,
    p_valor: float,
    alfa: float,
    simulados: np.ndarray,
) -> go.Figure:
    bordas = np.linspace(-LIMITE_VISIVEL, LIMITE_VISIVEL, 51)
    contagens, _ = np.histogram(simulados, bins=bordas)
    largura = bordas[1] - bordas[0]
    critico = float(distribuicao.isf(alfa / 2))

    fig = go.Figure()
    fig.add_bar(
        x=(bordas[:-1] + bordas[1:]) / 2,
        y=contagens / (len(simulados) * largura),
        width=largura,
        name=f"Simulação sob H₀ ({len(simulados):,} conjuntos)".replace(",", "."),
        marker={"color": cores.EIXO, "line": {"width": 0}},
        opacity=0.55,
        hovertemplate=rotulo + " ≈ %{x:.1f}<br>densidade %{y:.3f}<extra>Simulação</extra>",
    )
    _sombrear_duas_caudas(
        fig, distribuicao.pdf, critico, f"Região de rejeição (α = {formatar_numero(alfa)})",
        cores.com_opacidade(cores.TINTA_FRACA, 0.35), "rejeicao",
    )
    _sombrear_duas_caudas(
        fig, distribuicao.pdf, abs(observado), "Área do p-valor do exemplo",
        cores.com_opacidade(cor, 0.45), "p_valor",
    )
    x_curva = np.linspace(-LIMITE_VISIVEL, LIMITE_VISIVEL, 241)
    fig.add_scatter(
        x=x_curva,
        y=distribuicao.pdf(x_curva),
        mode="lines",
        line={"color": cor, "width": 2},
        name=nome_curva,
        hovertemplate=rotulo + " = %{x:.2f}<br>densidade %{y:.3f}<extra></extra>",
    )
    fig.add_scatter(
        x=[observado, observado],
        y=[0, 0.44],
        mode="lines",
        line={"color": cores.TINTA, "width": 2},
        name="Estatística do exemplo",
        hoverinfo="skip",
    )
    fig.add_annotation(
        x=observado, y=0.44, text=f"{rotulo} = {formatar_numero(observado)}",
        showarrow=False, yanchor="bottom", font={"color": cores.TINTA},
    )
    fig.add_annotation(
        x=1, xref="paper", y=0.5, text=formatar_p(p_valor),
        showarrow=False, xanchor="right", yanchor="top", font={"color": cores.TINTA},
    )
    fig.add_annotation(
        x=critico + 0.1, y=0.075, text=f"crítico ±{formatar_numero(critico)}",
        showarrow=False, xanchor="left", font={"color": cores.TINTA_SECUNDARIA},
    )
    estilizar(fig, titulo, eixo_x, "Densidade de probabilidade")
    fig.update_xaxes(range=[-LIMITE_VISIVEL, LIMITE_VISIVEL], dtick=1)
    fig.update_yaxes(range=[0, 0.5], dtick=0.1)
    return fig


def grafico_g2(exemplo: dict, simulados: dict[str, np.ndarray]) -> list[go.Figure]:
    welch = exemplo["welch"]
    mann_whitney = exemplo["mann_whitney"]
    alfa = exemplo["alfa"]
    return [
        _painel_g2(
            "G2 · Welch: estatística t sob H₀",
            "Estatística t (em erros-padrão, sem unidade)",
            "t",
            stats.t(welch["gl"]),
            f"t teórica ({formatar_numero(welch['gl'], 1)} gl)",
            cores.COR_WELCH,
            welch["estatistica"],
            welch["p_valor"],
            alfa,
            simulados["welch"],
        ),
        _painel_g2(
            "G2 · Mann-Whitney: estatística z sob H₀",
            "Estatística z (U padronizado, sem unidade)",
            "z",
            stats.norm(),
            "Normal padrão (aproximação de U)",
            cores.COR_MANN_WHITNEY,
            mann_whitney["z"],
            mann_whitney["p_valor"],
            alfa,
            simulados["mann_whitney"],
        ),
    ]
