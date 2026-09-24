"""S03 - Passo 6: dashboard de visualizacao (consolidacao das tres RQs).

    python analise/dashboard.py     (depende de analise/rq1_rq2.py e analise/rq3.py)

Nao recalcula nenhum teste: le os CSVs que rq1_rq2.py e rq3.py gravaram e so desenha.
Assim a figura e a tabela do relatorio nunca divergem.

Figuras (docs/figuras/):
  fig01-rq1-tempo-por-tratamento.png   boxplot + trials + par por integrante, escala log
  fig02-rq1-mediana-por-kata.png       mediana IA x MANUAL em cada kata (blocos do Wilcoxon)
  fig03-rq2-taxa-sucesso.png           taxa de sucesso por trial (efeito teto)
  fig04-rq3-complexidade.png           boxplot + trials, complexidade ciclomatica media
  fig05-rq3-loc.png                    boxplot + trials, LOC (controle)
  fig06-rq3-complexidade-por-kata.png  mediana IA x MANUAL da complexidade em cada kata

Codificacao visual: a cor e sempre o TRATAMENTO (comum.COR - mesma cor em todas as
figuras); o integrante vai no formato do marcador, para nao competir com a cor. A caixa e
mediana/IQR, nunca media - mesma convencao das tabelas.
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.ticker  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))

import comum as c  # noqa: E402

MARCADOR = {"p1": "o", "p2": "s", "p3": "^"}
ROTULO_TRATAMENTO = {"IA": "Com IA", "MANUAL": "Manual"}

plt.rcParams.update({
    "figure.dpi": 150, "savefig.dpi": 150, "savefig.bbox": "tight",
    "figure.facecolor": c.COR_SUPERFICIE, "axes.facecolor": c.COR_SUPERFICIE,
    "font.size": 10, "axes.titlesize": 11, "axes.titleweight": "bold",
    "axes.titlelocation": "left", "axes.labelcolor": c.COR_TEXTO_SEC,
    "text.color": c.COR_TEXTO, "xtick.color": c.COR_TEXTO_SEC, "ytick.color": c.COR_TEXTO_SEC,
    "axes.edgecolor": c.COR_GRID, "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "axes.axisbelow": True, "grid.color": c.COR_GRID, "grid.linewidth": 0.8,
    "legend.frameon": False,
})


def _salvar(fig: plt.Figure, nome: str) -> Path:
    c.FIGURAS.mkdir(parents=True, exist_ok=True)
    caminho = c.FIGURAS / nome
    fig.savefig(caminho)
    plt.close(fig)
    print("  -> " + str(caminho.relative_to(c.RAIZ)))
    return caminho


def _eixo_log(eixo: matplotlib.axis.Axis) -> None:
    """Escala log com ticks em segundos legiveis (5, 10, 30...), nao em potencias de 10."""
    eixo.set_major_locator(matplotlib.ticker.FixedLocator([5, 10, 30, 60, 100, 300, 600, 1000]))
    eixo.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:.0f}"))
    eixo.set_minor_formatter(matplotlib.ticker.NullFormatter())


def _legenda_integrantes(ax: plt.Axes) -> None:
    alcas = [
        plt.Line2D([], [], marker=MARCADOR[p], linestyle="none", markersize=7,
                   markerfacecolor=c.COR_NEUTRA, markeredgecolor=c.COR_SUPERFICIE, label=p.upper())
        for p in c.INTEGRANTES
    ]
    ax.legend(handles=alcas, title="Integrante", loc="upper left", bbox_to_anchor=(1.0, 1.0))


def boxplot_pareado(
    df: pd.DataFrame, coluna: str, titulo: str, ylabel: str, nome: str,
    logscale: bool = False, rotular: pd.Series | None = None,
) -> Path:
    """Caixa (mediana/IQR) por tratamento + cada trial + linha ligando as medianas de cada integrante.

    A linha por integrante torna visivel o desenho within-subject: cada pessoa fez as duas
    condicoes, em katas diferentes.
    """
    fig, ax = plt.subplots(figsize=(7, 4.6))
    posicoes = {t: i for i, t in enumerate(c.TRATAMENTOS)}

    for t, x in posicoes.items():
        valores = df.loc[df["tratamento"] == t, coluna].dropna().to_numpy(dtype=float)
        ax.boxplot(
            [valores], positions=[x], widths=0.42, patch_artist=True, showfliers=False,
            whis=(0, 100),
            boxprops=dict(facecolor=c.COR[t], alpha=0.18, edgecolor=c.COR[t], linewidth=1.2),
            medianprops=dict(color=c.COR[t], linewidth=2.4),
            whiskerprops=dict(color=c.COR[t], linewidth=1.2), capprops=dict(color=c.COR[t], linewidth=1.2),
        )
        mediana = float(np.median(valores))
        ax.annotate(
            f"mediana {c.fmt_num(mediana, 0 if mediana.is_integer() else 2)}", (x + 0.24, mediana),
            xytext=(4, 0), textcoords="offset points", va="center", fontsize=9, color=c.COR_TEXTO,
        )

    for pessoa in c.INTEGRANTES:
        sub = df[df["integrante"] == pessoa]
        medianas = [sub.loc[sub["tratamento"] == t, coluna].median() for t in c.TRATAMENTOS]
        ax.plot(list(posicoes.values()), medianas, color=c.COR_NEUTRA, linewidth=1.2,
                alpha=0.55, zorder=2, linestyle=(0, (3, 2)))
        for t, x in posicoes.items():
            valores = sub.loc[sub["tratamento"] == t, coluna]
            # deslocamento deterministico por integrante - pontos empatados nao se escondem
            desloc = (c.INTEGRANTES.index(pessoa) - 1) * 0.07
            ax.scatter(
                np.full(len(valores), x + desloc), valores, marker=MARCADOR[pessoa], s=48,
                color=c.COR[t], edgecolors=c.COR_SUPERFICIE, linewidths=1.5, zorder=3,
            )

    if rotular is not None:
        for _, r in df[rotular].iterrows():
            x = posicoes[r["tratamento"]] + (c.INTEGRANTES.index(r["integrante"]) - 1) * 0.07
            ax.annotate(f"{r['trial_id']} (outlier)", (x, r[coluna]), xytext=(10, 0),
                        textcoords="offset points", ha="left", va="center", fontsize=8,
                        color=c.COR_TEXTO_SEC)

    ax.set_xticks(list(posicoes.values()))
    ax.set_xticklabels([ROTULO_TRATAMENTO[t] for t in c.TRATAMENTOS])
    ax.set_xlim(-0.6, 1.9)
    ax.grid(axis="x", visible=False)
    ax.set_ylabel(ylabel)
    ax.set_title(titulo)
    if logscale:
        ax.set_yscale("log")
        _eixo_log(ax.yaxis)
    _legenda_integrantes(ax)
    return _salvar(fig, nome)


def dumbbell_por_kata(df: pd.DataFrame, coluna: str, titulo: str, xlabel: str, nome: str,
                      logscale: bool = False) -> Path:
    """Os blocos do Wilcoxon: mediana IA e MANUAL por kata. Kata sem par aparece, so com um ponto."""
    tabela = c.medianas_por_kata(df, coluna)
    fig, ax = plt.subplots(figsize=(7, 3.8))
    ys = np.arange(len(tabela))[::-1]

    for y, (_, r) in zip(ys, tabela.iterrows()):
        if r["par_completo"]:
            ax.plot([r["IA"], r["MANUAL"]], [y, y], color=c.COR_NEUTRA, linewidth=2, zorder=2)
        for t in c.TRATAMENTOS:
            if pd.notna(r[t]):
                ax.scatter(r[t], y, s=70, color=c.COR[t], edgecolors=c.COR_SUPERFICIE,
                           linewidths=2, zorder=3)
        if not r["par_completo"]:
            valor = r["IA"] if pd.notna(r["IA"]) else r["MANUAL"]
            ax.annotate("sem par - fora do teste", (valor, y), xytext=(10, 0),
                        textcoords="offset points", va="center", fontsize=8, color=c.COR_TEXTO_SEC)

    ax.set_yticks(ys)
    ax.set_yticklabels([c.ROTULO_KATA[k] for k in tabela["kata"]])
    ax.grid(axis="y", visible=False)
    ax.set_xlabel(xlabel)
    ax.set_title(titulo)
    if logscale:
        ax.set_xscale("log")
        _eixo_log(ax.xaxis)
    alcas = [
        plt.Line2D([], [], marker="o", linestyle="none", markersize=8, markerfacecolor=c.COR[t],
                   markeredgecolor=c.COR_SUPERFICIE, label=ROTULO_TRATAMENTO[t])
        for t in c.TRATAMENTOS
    ]
    ax.legend(handles=alcas, loc="upper left", bbox_to_anchor=(1.0, 1.0))
    return _salvar(fig, nome)


def taxa_sucesso(trials: pd.DataFrame) -> Path:
    fig, ax = plt.subplots(figsize=(7, 3.6))
    for i, t in enumerate(c.TRATAMENTOS):
        sub = trials[trials["tratamento"] == t]
        for pessoa in c.INTEGRANTES:
            valores = sub.loc[sub["integrante"] == pessoa, "taxa_sucesso"] * 100
            desloc = (c.INTEGRANTES.index(pessoa) - 1) * 0.12
            xs = i + desloc + np.linspace(-0.03, 0.03, len(valores)) if len(valores) > 1 else [i + desloc]
            ax.scatter(xs, valores, marker=MARCADOR[pessoa], s=48, color=c.COR[t],
                       edgecolors=c.COR_SUPERFICIE, linewidths=1.5, zorder=3)
        n_total = len(sub)
        n_cheio = int((sub["taxa_sucesso"] == 1).sum())
        ax.annotate(f"{n_cheio} de {n_total} trials com 100%", (i, 100), xytext=(0, 14),
                    textcoords="offset points", ha="center", fontsize=9, color=c.COR_TEXTO)
    ax.set_xticks(range(len(c.TRATAMENTOS)))
    ax.set_xticklabels([ROTULO_TRATAMENTO[t] for t in c.TRATAMENTOS])
    ax.set_xlim(-0.6, 1.6)
    ax.set_ylim(0, 115)
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.grid(axis="x", visible=False)
    ax.set_ylabel("Testes de aceitacao passando (%)")
    ax.set_title("RQ2 - Taxa de sucesso por trial: efeito teto nos dois tratamentos")
    _legenda_integrantes(ax)
    return _salvar(fig, "fig03-rq2-taxa-sucesso.png")


def _linha(res: pd.DataFrame, rq: str, metrica: str, teste: str, escopo: str = "completo (18 trials)") -> pd.Series:
    sub = res[(res["rq"] == rq) & (res["metrica"] == metrica) & (res["teste"] == teste)
              & (res["escopo"] == escopo)]
    c.exigir(len(sub) == 1, f"resultado ausente: {rq} {metrica} {teste} ({escopo}). Rode o script da RQ.")
    return sub.iloc[0]


def _mediana(desc: pd.DataFrame, metrica: str, tratamento: str) -> float:
    return float(desc[(desc["metrica"] == metrica) & (desc["tratamento"] == tratamento)]["mediana"].iloc[0])


def resumo_console(res: pd.DataFrame, desc: pd.DataFrame) -> None:
    c.cabecalho("Consolidacao Lab02 - Sprint 03")

    def teste_str(rq: str, metrica: str) -> str:
        wk = _linha(res, rq, metrica, "Wilcoxon pareado por kata")
        mw = _linha(res, rq, metrica, "Mann-Whitney U")
        if wk["decisao"] == "nao aplicavel" and mw["decisao"] == "nao aplicavel":
            return "testes nao aplicaveis (" + str(mw["observacao"]) + ")"
        return (
            f"Wilcoxon por kata n={int(wk['n'])}/6 p={c.fmt_p(wk['p_valor'])} "
            f"(rank-biserial {c.fmt_num(wk['valor_efeito'], 3)}) | "
            f"Mann-Whitney p={c.fmt_p(mw['p_valor'])} (Cliff {c.fmt_num(mw['valor_efeito'], 3)}, "
            f"{mw['magnitude']}) -> {mw['decisao']}"
        )

    linhas = [
        ("RQ1 tempo (s)", "RQ1", "time_to_green_s", 0),
        ("RQ2 taxa de sucesso", "RQ2", "taxa_sucesso", 2),
        ("RQ3 cc_media", "RQ3", "cc_media", 1),
        ("RQ3 loc", "RQ3", "loc", 0),
        ("RQ3 cc_soma_por_loc", "RQ3", "cc_soma_por_loc", 3),
        ("RQ3 pct_duplicado", "RQ3", "pct_duplicado", 2),
    ]
    for rotulo, rq, metrica, casas in linhas:
        ia, man = _mediana(desc, metrica, "IA"), _mediana(desc, metrica, "MANUAL")
        print(f"\n{rotulo}: mediana IA={c.fmt_num(ia, casas)} vs MANUAL={c.fmt_num(man, casas)}")
        print("  " + teste_str(rq, metrica))


def main() -> int:
    trials = c.carregar_trials()
    metrics = c.ler_csv(c.METRICS, dica="rode antes:  python analise/rq3.py")
    res = pd.concat([
        c.ler_csv(c.RESULTADOS_RQ12, dica="rode antes:  python analise/rq1_rq2.py"),
        c.ler_csv(c.RESULTADOS_RQ3, dica="rode antes:  python analise/rq3.py"),
    ], ignore_index=True)
    desc = pd.concat([
        c.ler_csv(c.DATA / "descritivas_rq1_rq2.csv"),
        c.ler_csv(c.DATA / "descritivas_rq3.csv"),
    ], ignore_index=True)

    resumo_console(res, desc)

    print("\nfiguras geradas:")
    boxplot_pareado(
        trials, "time_to_green_s", "RQ1 - Tempo ate a suite ficar verde (time-to-green)",
        "Segundos (escala log)", "fig01-rq1-tempo-por-tratamento.png", logscale=True,
    )
    dumbbell_por_kata(
        trials, "time_to_green_s", "RQ1 - Mediana do tempo por kata (blocos do Wilcoxon)",
        "Segundos (escala log)", "fig02-rq1-mediana-por-kata.png", logscale=True,
    )
    taxa_sucesso(trials)
    boxplot_pareado(
        metrics, "cc_media", "RQ3 - Complexidade ciclomatica media por funcao",
        "Complexidade ciclomatica (media por funcao)", "fig04-rq3-complexidade.png",
    )
    boxplot_pareado(
        metrics, "loc", "RQ3 - Linhas de codigo (LOC), metrica de controle", "LOC",
        "fig05-rq3-loc.png", rotular=metrics["pct_duplicado"] > 0,
    )
    dumbbell_por_kata(
        metrics, "cc_media", "RQ3 - Mediana da complexidade por kata (blocos do Wilcoxon)",
        "Complexidade ciclomatica (media por funcao)", "fig06-rq3-complexidade-por-kata.png",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
