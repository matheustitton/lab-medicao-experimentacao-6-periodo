from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # backend sem janela: roda igual em qualquer maquina

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import seaborn as sns  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))

import comum as c  # noqa: E402

DPI = 200


def aplicar_estilo() -> None:
    sns.set_theme(style="whitegrid")
    plt.rcParams.update({
        "figure.facecolor": c.COR_SUPERFICIE,
        "axes.facecolor": c.COR_SUPERFICIE,
        "savefig.facecolor": c.COR_SUPERFICIE,
        "axes.edgecolor": c.COR_GRID,
        "axes.labelcolor": c.COR_TEXTO_SEC,
        "axes.titlecolor": c.COR_TEXTO,
        "axes.titlesize": 13,
        "axes.titleweight": "semibold",
        "axes.labelsize": 10,
        "axes.grid": True,
        "grid.color": c.COR_GRID,
        "grid.linewidth": 0.8,
        "grid.linestyle": "-",          # grade tracejada le como "projecao"; e so grade
        "text.color": c.COR_TEXTO,
        "xtick.color": c.COR_TEXTO_SEC,
        "ytick.color": c.COR_TEXTO_SEC,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "legend.frameon": False,
        "legend.fontsize": 9,
        "font.size": 10,
    })


def virgula_decimal(eixo) -> None:
    """Rotulo de eixo em pt-BR: 0,25 e nao 0.25.

    Sem isso a figura mistura as duas notacoes - o eixo com ponto e o rotulo da
    mediana com virgula, que sao gerados por caminhos diferentes.
    """
    eixo.set_major_formatter(
        matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:g}".replace(".", ","))
    )


def limpar_eixo(ax, eixo_x_apenas: bool = True) -> None:
    for lado in ("top", "right", "left"):
        ax.spines[lado].set_visible(False)
    ax.spines["bottom"].set_color(c.COR_GRID)
    ax.set_axisbelow(True)
    virgula_decimal(ax.xaxis)
    if eixo_x_apenas:
        ax.grid(axis="y", visible=False)
        ax.grid(axis="x", visible=True)


def salvar(fig, nome: str) -> None:
    c.FIGURAS.mkdir(parents=True, exist_ok=True)
    caminho = c.FIGURAS / nome
    fig.savefig(caminho, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print("  -> " + str(caminho.relative_to(c.RAIZ)))


def pontos_por_tratamento(ax, df: pd.DataFrame, coluna: str, rotulo_x: str,
                          titulo: str, casas: int = 0) -> None:
    """Dot plot horizontal: um ponto por trial, mediana marcada e rotulada."""
    ordem = [t for t in c.TRATAMENTOS if (df["tratamento"] == t).any()]
    rng = np.random.default_rng(42)  # jitter reprodutivel

    for i, tratamento in enumerate(ordem):
        valores = df.loc[df["tratamento"] == tratamento, coluna].dropna().to_numpy(dtype=float)
        if valores.size == 0:
            continue
        jitter = rng.uniform(-0.13, 0.13, size=valores.size)
        ax.scatter(
            valores, np.full(valores.size, i) + jitter,
            s=70, color=c.COR[tratamento], alpha=0.85,
            edgecolors=c.COR_SUPERFICIE, linewidths=2, zorder=3,
        )
        mediana = float(np.median(valores))
        ax.plot([mediana, mediana], [i - 0.28, i + 0.28],
                color=c.COR[tratamento], linewidth=2.5, zorder=4)
        ax.annotate(
            f"mediana {c.fmt_num(mediana, casas)}",
            xy=(mediana, i + 0.34), ha="center", va="bottom",
            fontsize=9, color=c.COR_TEXTO_SEC,
        )

    ax.set_yticks(range(len(ordem)))
    ax.set_yticklabels([f"{t}  (n={int((df['tratamento'] == t).sum())})" for t in ordem])
    ax.set_ylim(-0.6, len(ordem) - 0.35)
    ax.set_xlabel(rotulo_x)
    ax.set_title(titulo, loc="left", pad=12)
    limpar_eixo(ax)


# --------------------------------------------------------------- figuras ---


def fig_tempo(df: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(9, 3.6))
    pontos_por_tratamento(
        ax, df, "time_to_green_s", "time-to-green (segundos)",
        "RQ1 - tempo ate a suite ficar verde, por tratamento",
    )
    ia = df.loc[df["tratamento"] == "IA", "time_to_green_s"]
    manual = df.loc[df["tratamento"] == "MANUAL", "time_to_green_s"]
    ax.annotate(
        f"separacao completa: o trial IA mais lento ({int(ia.max())}s) ainda e mais rapido\n"
        f"que o trial MANUAL mais rapido ({int(manual.min())}s)",
        xy=(0.5, -0.42), xycoords="axes fraction", ha="center",
        fontsize=9, color=c.COR_TEXTO_SEC,
    )
    salvar(fig, "fig01-rq1-tempo-por-tratamento.png")


def fig_tempo_por_kata(df: pd.DataFrame) -> None:
    """Halteres: a mediana de cada tratamento na mesma kata, ligadas.

    E a figura que mostra o bloco do Wilcoxon - inclusive as duas katas que nao
    formam par, que aparecem marcadas para nao sumirem da historia.
    """
    tabela = c.medianas_por_kata(df, "time_to_green_s")
    fig, ax = plt.subplots(figsize=(9, 4.2))

    for i, (_, r) in enumerate(tabela.iterrows()):
        if r["par_completo"]:
            ax.plot([r["MANUAL"], r["IA"]], [i, i], color=c.COR_GRID, linewidth=3, zorder=1)
        for tratamento in c.TRATAMENTOS:
            valor = r[tratamento]
            if valor == valor:
                ax.scatter(valor, i, s=110, color=c.COR[tratamento], zorder=3,
                           edgecolors=c.COR_SUPERFICIE, linewidths=2)
        if not r["par_completo"]:
            presente = "IA" if r["IA"] == r["IA"] else "MANUAL"
            ax.annotate(
                f"sem par - so {presente}", xy=(float(r[presente]), i),
                xytext=(14, 0), textcoords="offset points", va="center",
                fontsize=9, color=c.COR_NEUTRA, style="italic",
            )

    ax.set_yticks(range(len(tabela)))
    ax.set_yticklabels([c.ROTULO_KATA[k] for k in tabela["kata"]])
    ax.invert_yaxis()
    ax.set_xlabel("mediana do time-to-green (segundos)")
    ax.set_title("RQ1 - mediana por kata: os blocos do Wilcoxon pareado", loc="left", pad=12)
    limpar_eixo(ax)
    for tratamento in c.TRATAMENTOS:
        ax.scatter([], [], s=110, color=c.COR[tratamento], label=tratamento)
    ax.legend(loc="upper right")
    pares = int(tabela["par_completo"].sum())
    ax.annotate(
        f"{pares} de 6 katas receberam os dois tratamentos - o n do teste pareado e {pares}, nao 6",
        xy=(0.5, -0.24), xycoords="axes fraction", ha="center",
        fontsize=9, color=c.COR_TEXTO_SEC,
    )
    salvar(fig, "fig02-rq1-mediana-por-kata.png")


def fig_taxa_sucesso(df: pd.DataFrame) -> None:
    """RQ2 e um numero, nao um grafico: painel de numero + dispersao dos trials."""
    fig, (ax_num, ax_pontos) = plt.subplots(
        1, 2, figsize=(9.5, 3.2), gridspec_kw={"width_ratios": [1, 2], "wspace": 0.5}
    )

    taxa = df["taxa_sucesso"].mean() * 100
    ax_num.axis("off")
    ax_num.text(0.0, 0.62, f"{taxa:.0f}%".replace(".", ","), fontsize=44,
                color=c.COR_TEXTO, ha="left", va="center", fontweight="bold")
    ax_num.text(0.0, 0.30, "taxa de sucesso em\ntodos os 18 trials", fontsize=10,
                color=c.COR_TEXTO_SEC, ha="left", va="center")
    ax_num.text(0.0, 0.06, f"{int(df['censurado'].sum())} trials censurados", fontsize=10,
                color=c.COR_TEXTO_SEC, ha="left", va="center")

    pontos_por_tratamento(
        ax_pontos, df, "taxa_sucesso", "taxa de sucesso",
        "RQ2 - efeito teto: nenhuma variancia para testar", casas=2,
    )
    ax_pontos.set_xlim(0.5, 1.08)
    salvar(fig, "fig03-rq2-taxa-sucesso.png")


def fig_rq3_complexidade(metrics: pd.DataFrame) -> None:
    painel = [
        ("cc_max_por_loc", "CC maxima / LOC", 3),
        ("cc_soma", "CC somada", 0),
        ("loc", "LOC (controle)", 0),
    ]
    fig, eixos = plt.subplots(len(painel), 1, figsize=(9, 8.4))
    for ax, (coluna, titulo, casas) in zip(eixos, painel):
        pontos_por_tratamento(ax, metrics, coluna, titulo, titulo, casas=casas)
        ax.set_title(titulo, loc="left", pad=12)
        ax.set_xlabel("")
    eixos[0].annotate(
        "RQ3 - estrutura do codigo final, um ponto por trial",
        xy=(0, 1.35), xycoords="axes fraction", ha="left",
        fontsize=13, fontweight="semibold", color=c.COR_TEXTO,
    )
    fig.tight_layout(h_pad=3.2)
    salvar(fig, "fig04-rq3-complexidade.png")


def fig_rq3_duplicacao(metrics: pd.DataFrame) -> None:
    pool = c.ler_csv(c.POOL_DUPLICACAO) if c.POOL_DUPLICACAO.exists() else pd.DataFrame()
    fig, (ax_trial, ax_pool) = plt.subplots(1, 2, figsize=(10, 3.8))

    pontos_por_tratamento(
        ax_trial, metrics, "pct_duplicado", "% de linhas duplicadas",
        "Duplicacao dentro de cada trial (primaria)", casas=2,
    )

    if pool.empty:
        ax_pool.axis("off")
        ax_pool.text(0.5, 0.5, "pool de duplicacao ausente\n(rode run_metrics.ps1 -Todos)",
                     ha="center", va="center", color=c.COR_TEXTO_SEC, fontsize=10)
    else:
        pool = pool.copy()
        pool["pct_duplicado"] = pd.to_numeric(pool["pct_duplicado"], errors="coerce")
        pool["n_trials"] = pd.to_numeric(pool["n_trials"], errors="coerce")
        # log de append, igual ao metrics.csv: a medicao mais recente e a que vale
        pool = pool.drop_duplicates(["kata", "tratamento"], keep="last")
        # so os pools que realmente comparam pessoas entre si
        pool = pool[pool["n_trials"] >= 2]

        largura = 0.38
        katas = [k for k in c.KATAS if k in set(pool["kata"])]
        for deslocamento, tratamento in zip((-largura / 2, largura / 2), c.TRATAMENTOS):
            valores, posicoes, ns = [], [], []
            for i, kata in enumerate(katas):
                linha = pool[(pool["kata"] == kata) & (pool["tratamento"] == tratamento)]
                if not linha.empty:
                    valores.append(float(linha["pct_duplicado"].iloc[0]))
                    posicoes.append(i + deslocamento)
                    ns.append(int(linha["n_trials"].iloc[0]))
            if valores:
                ax_pool.bar(posicoes, valores, width=largura * 0.92,
                            color=c.COR[tratamento], label=tratamento, zorder=3)
                # Barra de 0% e invisivel: sem o rotulo, o leitor nao distingue
                # "pool sem duplicacao" de "nao existe pool deste tratamento aqui".
                for x, valor, n in zip(posicoes, valores, ns):
                    ax_pool.annotate(
                        f"{c.fmt_num(valor)}\nn={n}", xy=(x, valor), xytext=(0, 4),
                        textcoords="offset points", ha="center", va="bottom",
                        fontsize=8, color=c.COR_TEXTO_SEC,
                    )
        ax_pool.set_xticks(range(len(katas)))
        ax_pool.set_xticklabels([c.ROTULO_KATA[k] for k in katas], rotation=30, ha="right")
        ax_pool.set_ylabel("% duplicado no pool")
        ax_pool.set_title("Duplicacao entre solucoes de integrantes diferentes",
                          loc="left", pad=12)
        ax_pool.set_ylim(0, max(6.0, float(pool["pct_duplicado"].max()) * 1.35))
        virgula_decimal(ax_pool.yaxis)
        for lado in ("top", "right"):
            ax_pool.spines[lado].set_visible(False)
        ax_pool.grid(axis="x", visible=False)
        ax_pool.set_axisbelow(True)
        ax_pool.legend(loc="upper left")
        ax_pool.annotate(
            "cada kata recebeu os dois tratamentos em pessoas diferentes; onde falta barra,\n"
            "aquele tratamento nao teve 2+ solucoes para comparar",
            xy=(0, -0.42), xycoords="axes fraction", fontsize=8, color=c.COR_NEUTRA,
        )

    fig.tight_layout(w_pad=3.0)
    salvar(fig, "fig05-rq3-duplicacao.png")


def fig_painel(df: pd.DataFrame, metrics: pd.DataFrame | None) -> None:
    """O painel unico do Passo 6: os tres RQs numa figura so."""
    fig = plt.figure(figsize=(13, 8.5))
    grade = fig.add_gridspec(3, 3, height_ratios=[0.5, 1.15, 1.15], hspace=0.75, wspace=0.28)

    # --- faixa de indicadores ------------------------------------------------
    ax_kpi = fig.add_subplot(grade[0, :])
    ax_kpi.axis("off")
    ia = df.loc[df["tratamento"] == "IA", "time_to_green_s"]
    manual = df.loc[df["tratamento"] == "MANUAL", "time_to_green_s"]
    reducao = (1 - ia.median() / manual.median()) * 100
    indicadores = [
        (f"{int(ia.median())}s", "mediana IA", c.COR["IA"]),
        (f"{int(manual.median())}s", "mediana MANUAL", c.COR["MANUAL"]),
        (f"-{reducao:.0f}%".replace(".", ","), "reducao da mediana", c.COR_TEXTO),
        (f"{df['taxa_sucesso'].mean() * 100:.0f}%".replace(".", ","),
         "sucesso nos 18 trials", c.COR_TEXTO),
        (f"{int(df['censurado'].sum())}", "trials censurados", c.COR_TEXTO),
    ]
    for i, (valor, rotulo, cor) in enumerate(indicadores):
        x = i / len(indicadores)
        ax_kpi.text(x, 0.45, valor, fontsize=30, fontweight="bold", color=cor,
                    ha="left", va="center", transform=ax_kpi.transAxes)
        ax_kpi.text(x, 0.05, rotulo, fontsize=10, color=c.COR_TEXTO_SEC,
                    ha="left", va="center", transform=ax_kpi.transAxes)
    ax_kpi.text(0, 1.25, "Lab02 - assistente de IA vs. codificacao manual",
                fontsize=16, fontweight="bold", color=c.COR_TEXTO,
                ha="left", va="center", transform=ax_kpi.transAxes)
    ax_kpi.text(0, 0.95, "18 trials | 3 integrantes | 6 katas | time-box de 35 min | medianas e IQR",
                fontsize=10, color=c.COR_TEXTO_SEC, ha="left", va="center",
                transform=ax_kpi.transAxes)

    # --- RQ1 -----------------------------------------------------------------
    ax1 = fig.add_subplot(grade[1, :2])
    pontos_por_tratamento(ax1, df, "time_to_green_s", "segundos",
                          "RQ1 - time-to-green por trial")

    ax2 = fig.add_subplot(grade[1, 2])
    tabela = c.medianas_por_kata(df, "time_to_green_s")
    for i, (_, r) in enumerate(tabela.iterrows()):
        if r["par_completo"]:
            ax2.plot([r["MANUAL"], r["IA"]], [i, i], color=c.COR_GRID, linewidth=2.5, zorder=1)
        for tratamento in c.TRATAMENTOS:
            if r[tratamento] == r[tratamento]:
                ax2.scatter(r[tratamento], i, s=60, color=c.COR[tratamento], zorder=3,
                            edgecolors=c.COR_SUPERFICIE, linewidths=1.5)
    ax2.set_yticks(range(len(tabela)))
    ax2.set_yticklabels([c.ROTULO_KATA[k] for k in tabela["kata"]], fontsize=8)
    ax2.invert_yaxis()
    ax2.set_xlabel("mediana (s)")
    ax2.set_title("RQ1 - por kata", loc="left", pad=26)  # espaco para a legenda abaixo
    limpar_eixo(ax2)
    for tratamento in c.TRATAMENTOS:   # identidade nunca so pela cor
        ax2.scatter([], [], s=60, color=c.COR[tratamento], label=tratamento)
    # Acima do eixo: dentro da area de plot a legenda cobre os pontos das katas K5/K6.
    ax2.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=2, fontsize=8)
    sem_par = [c.ROTULO_KATA[k] for k in tabela.loc[~tabela["par_completo"], "kata"]]
    if sem_par:
        ax2.annotate(
            " e ".join(sem_par) + ": so um tratamento",
            xy=(0, -0.30), xycoords="axes fraction", fontsize=8, color=c.COR_NEUTRA,
        )

    # --- RQ2 e RQ3 -----------------------------------------------------------
    ax3 = fig.add_subplot(grade[2, 0])
    ax3.axis("off")
    ax3.text(0, 0.78, f"{df['taxa_sucesso'].mean() * 100:.0f}%".replace(".", ","),
             fontsize=44, fontweight="bold", color=c.COR_TEXTO, ha="left", va="center")
    ax3.text(0, 0.42, "RQ2 - taxa de sucesso\nidentica nos dois tratamentos", fontsize=10,
             color=c.COR_TEXTO_SEC, ha="left", va="center")
    ax3.text(0, 0.12, "efeito teto: sem variancia,\nnenhum teste e aplicavel", fontsize=9,
             color=c.COR_NEUTRA, ha="left", va="center", style="italic")

    if metrics is not None and not metrics.empty:
        ax4 = fig.add_subplot(grade[2, 1])
        pontos_por_tratamento(ax4, metrics, "cc_max_por_loc", "CC maxima / LOC",
                              "RQ3 - complexidade normalizada", casas=3)
        ax5 = fig.add_subplot(grade[2, 2])
        pontos_por_tratamento(ax5, metrics, "loc", "LOC", "RQ3 - tamanho (controle)")
    else:
        ax4 = fig.add_subplot(grade[2, 1:])
        ax4.axis("off")
        ax4.text(0.5, 0.5, "RQ3 sem dados: rode run_metrics.ps1 -Todos e depois analise/rq3.py",
                 ha="center", va="center", color=c.COR_TEXTO_SEC, fontsize=11)

    salvar(fig, "fig06-painel-resumo.png")


def escrever_indice(figuras: list[tuple[str, str]]) -> None:
    linhas = [
        "# S03 - Dashboard de visualizacao (Passo 6)",
        "",
        "Figuras geradas por `analise/dashboard.py`. Regerar sempre que o dataset mudar -",
        "nenhuma delas e editada a mao.",
        "",
    ]
    for nome, legenda in figuras:
        linhas += [f"## {legenda}", "", f"![{legenda}](../figuras/{nome})", ""]
    c.escrever_md("\n".join(linhas) + "\n", c.RESULTADOS / "dashboard.md")


def main() -> int:
    c.cabecalho("S03 - dashboard de visualizacao")
    aplicar_estilo()

    df = c.carregar_trials()
    metrics = None
    if c.METRICS.exists():
        metrics = c.ler_csv(c.METRICS)
        for coluna in ("loc", "cc_max", "cc_soma", "cc_media", "cc_max_por_loc",
                       "cc_soma_por_loc", "pct_duplicado"):
            metrics[coluna] = pd.to_numeric(metrics[coluna], errors="coerce")
        if len(metrics) != c.N_TRIALS_ESPERADO:
            print(f"AVISO: metrics_consolidado.csv tem {len(metrics)} trials, "
                  f"esperado {c.N_TRIALS_ESPERADO}. As figuras da RQ3 saem PARCIAIS.")
    else:
        print("AVISO: data/metrics_consolidado.csv ausente - figuras da RQ3 puladas.")
        print("       Rode antes:  .\\scripts\\run_metrics.ps1 -Todos  e  python analise/rq3.py")

    print("\nfiguras geradas:")
    figuras = []
    fig_tempo(df)
    figuras.append(("fig01-rq1-tempo-por-tratamento.png", "RQ1 - tempo por tratamento"))
    fig_tempo_por_kata(df)
    figuras.append(("fig02-rq1-mediana-por-kata.png", "RQ1 - mediana por kata"))
    fig_taxa_sucesso(df)
    figuras.append(("fig03-rq2-taxa-sucesso.png", "RQ2 - taxa de sucesso"))

    if metrics is not None and not metrics.empty:
        fig_rq3_complexidade(metrics)
        figuras.append(("fig04-rq3-complexidade.png", "RQ3 - complexidade e LOC"))
        fig_rq3_duplicacao(metrics)
        figuras.append(("fig05-rq3-duplicacao.png", "RQ3 - duplicacao"))

    fig_painel(df, metrics)
    figuras.append(("fig06-painel-resumo.png", "Painel consolidado"))

    escrever_indice(figuras)
    print("\nProximo passo: montar o relatorio com  python analise/montar_relatorio.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
