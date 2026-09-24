"""S03 - Passo 4: testes estatisticos da RQ1 (tempo) e da RQ2 (defeitos).

    python analise/rq1_rq2.py     (depende de analise/consolidar_dados.py)

Executa exatamente o plano fixado em `docs/desenho-experimento.md`, secao
"Plano de analise estatistica", sem escolher teste depois de ver os dados:

  1. Wilcoxon signed-rank pareado POR KATA          - teste principal
  2. Mann-Whitney U sobre os trials individuais     - teste secundario
  3. mediana e IQR em toda tabela (nunca media)     - descritiva
  4. tamanho de efeito reportado junto de todo p
  5. analise de sensibilidade                       - sem P1 e sem cronometragem suspeita

Hipoteses (unicaudais, alfa = 0,05):
  RQ1  H0: mediana(tempo_IA) = mediana(tempo_MANUAL)   H1: IA < MANUAL
  RQ2  H0: mediana(sucesso_IA) = mediana(sucesso_MAN)  H1: IA > MANUAL

Saidas:
  data/resultados_rq1_rq2.csv      uma linha por teste executado
  data/descritivas_rq1_rq2.csv     mediana/IQR por tratamento
  docs/resultados/rq1-rq2.md       tabelas prontas para o relatorio final
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent))

import comum as c  # noqa: E402

resultados: list[dict] = []


def registrar(**campos) -> None:
    resultados.append(campos)


def decidir(p: float) -> str:
    if p != p:
        return "nao aplicavel"
    return "rejeita H0" if p < c.ALFA else "nao rejeita H0"


def wilcoxon_por_kata(df: pd.DataFrame, coluna: str, alternativa: str, rq: str, escopo: str) -> None:
    """Teste principal: a kata e o bloco, a mediana de cada tratamento e o par."""
    tabela = c.medianas_por_kata(df, coluna)
    completos = tabela[tabela["par_completo"]]
    n = len(completos)
    incompletas = tabela.loc[~tabela["par_completo"], "kata"].tolist()

    print(f"\n[{rq}] Wilcoxon pareado por kata - escopo: {escopo}")
    for _, r in tabela.iterrows():
        if r["par_completo"]:
            print(
                f"  {c.ROTULO_KATA[r['kata']]:<16} IA={c.fmt_num(r['IA'])}"
                f"   MANUAL={c.fmt_num(r['MANUAL'])}"
                f"   dif={c.fmt_num(r['diferenca_ia_menos_manual'])}"
            )
        else:
            print(f"  {c.ROTULO_KATA[r['kata']]:<16} SEM PAR - fora do teste")

    if n < 2:
        print(f"  -> pares insuficientes (n={n}): teste nao executado")
        registrar(
            rq=rq, metrica=coluna, escopo=escopo, teste="Wilcoxon pareado por kata",
            n=n, estatistica=float("nan"), p_valor=float("nan"), alternativa=alternativa,
            efeito="rank-biserial pareado", valor_efeito=float("nan"), magnitude="indefinido",
            decisao="nao aplicavel",
            observacao=f"apenas {n} pares completos; katas sem par: {', '.join(incompletas)}",
        )
        return

    difs = completos["diferenca_ia_menos_manual"].tolist()
    p_minimo = c.p_minimo_wilcoxon(n, unicaudal=alternativa != "two-sided")

    if all(d == 0 for d in difs):
        print("  -> todas as diferencas sao zero: o teste e indefinido (efeito teto)")
        registrar(
            rq=rq, metrica=coluna, escopo=escopo, teste="Wilcoxon pareado por kata",
            n=n, estatistica=float("nan"), p_valor=float("nan"), alternativa=alternativa,
            efeito="rank-biserial pareado", valor_efeito=0.0, magnitude="nulo",
            decisao="nao aplicavel",
            observacao="diferenca zero em todos os pares - sem variancia para testar",
        )
        return

    resultado = stats.wilcoxon(
        completos["IA"].to_numpy(dtype=float),
        completos["MANUAL"].to_numpy(dtype=float),
        alternative=alternativa,
    )
    efeito = c.rank_biserial_pareado(difs)
    observacao = f"katas sem par excluidas: {', '.join(incompletas)}" if incompletas else ""
    if p_minimo > c.ALFA:
        observacao = (
            f"n={n}: o menor p alcancavel pelo teste exato e {c.fmt_p(p_minimo)}, acima de "
            f"alfa={c.ALFA} - o teste nao pode rejeitar H0 neste N. " + observacao
        )

    print(
        f"  -> W = {resultado.statistic:.1f}   p = {c.fmt_p(float(resultado.pvalue))}"
        f"   ({decidir(float(resultado.pvalue))})   rank-biserial = {c.fmt_num(efeito, 3)}"
    )
    if p_minimo > c.ALFA:
        print(f"     ATENCAO: com n={n} o menor p possivel e {c.fmt_p(p_minimo)} > alfa={c.ALFA}")

    registrar(
        rq=rq, metrica=coluna, escopo=escopo, teste="Wilcoxon pareado por kata",
        n=n, estatistica=round(float(resultado.statistic), 4),
        p_valor=round(float(resultado.pvalue), 6), alternativa=alternativa,
        efeito="rank-biserial pareado", valor_efeito=efeito,
        magnitude="direcao consistente" if abs(efeito) == 1 else "direcao mista",
        decisao=decidir(float(resultado.pvalue)), observacao=observacao,
    )


def mann_whitney(df: pd.DataFrame, coluna: str, alternativa: str, rq: str, escopo: str) -> None:
    """Teste secundario: 9 trials IA contra 9 MANUAL, sem pareamento."""
    ia = df.loc[df["tratamento"] == "IA", coluna].dropna().to_numpy(dtype=float)
    manual = df.loc[df["tratamento"] == "MANUAL", coluna].dropna().to_numpy(dtype=float)

    print(f"\n[{rq}] Mann-Whitney U - escopo: {escopo}  (n_IA={len(ia)}, n_MANUAL={len(manual)})")

    if len(ia) < 2 or len(manual) < 2:
        print("  -> amostras insuficientes")
        return

    if len(set(ia.tolist() + manual.tolist())) == 1:
        print("  -> todos os valores identicos nos dois grupos: teste indefinido (efeito teto)")
        registrar(
            rq=rq, metrica=coluna, escopo=escopo, teste="Mann-Whitney U",
            n=len(ia) + len(manual), estatistica=float("nan"), p_valor=float("nan"),
            alternativa=alternativa, efeito="Cliff's delta", valor_efeito=0.0, magnitude="nulo",
            decisao="nao aplicavel",
            observacao="variancia zero nos dois grupos - nao ha o que ordenar",
        )
        return

    resultado = stats.mannwhitneyu(ia, manual, alternative=alternativa)
    delta, magnitude = c.cliffs_delta(ia.tolist(), manual.tolist())
    print(
        f"  -> U = {resultado.statistic:.1f}   p = {c.fmt_p(float(resultado.pvalue))}"
        f"   ({decidir(float(resultado.pvalue))})   Cliff's delta = "
        f"{c.fmt_num(delta, 3)} ({magnitude})"
    )
    registrar(
        rq=rq, metrica=coluna, escopo=escopo, teste="Mann-Whitney U",
        n=len(ia) + len(manual), estatistica=round(float(resultado.statistic), 4),
        p_valor=round(float(resultado.pvalue), 6), alternativa=alternativa,
        efeito="Cliff's delta", valor_efeito=delta, magnitude=magnitude,
        decisao=decidir(float(resultado.pvalue)), observacao="",
    )


def descritivas(df: pd.DataFrame) -> pd.DataFrame:
    tabelas = [
        c.resumo_por_tratamento(df, "time_to_green_s"),
        c.resumo_por_tratamento(df, "taxa_sucesso"),
        c.resumo_por_tratamento(df, "testes_passando"),
    ]
    prompts = df[df["tratamento"] == "IA"]["n_prompts"].dropna()
    if not prompts.empty:
        mediana, q1, q3, iqr = c.mediana_iqr(prompts)
        tabelas.append(
            pd.DataFrame([{
                "metrica": "n_prompts", "tratamento": "IA", "n": int(len(prompts)),
                "mediana": round(mediana, 4), "q1": round(q1, 4), "q3": round(q3, 4),
                "iqr": round(iqr, 4), "min": float(prompts.min()), "max": float(prompts.max()),
            }])
        )
    return pd.concat(tabelas, ignore_index=True)


def montar_relatorio(df: pd.DataFrame, desc: pd.DataFrame, res: pd.DataFrame) -> str:
    censurados = df.groupby("tratamento")["censurado"].sum().to_dict()
    tempo = c.medianas_por_kata(df, "time_to_green_s")
    pares = int(tempo["par_completo"].sum())

    def bloco(rq: str, escopo: str) -> list[str]:
        sub = res[(res["rq"] == rq) & (res["escopo"] == escopo)]
        if sub.empty:
            return ["_sem resultado para este escopo._", ""]
        linhas = [
            "| teste | n | estatistica | p-valor | efeito | decisao (alfa = 0,05) |",
            "|---|---|---|---|---|---|",
        ]
        for _, r in sub.iterrows():
            linhas.append(
                f"| {r['teste']} | {r['n']} | {c.fmt_num(r['estatistica'], 1)} | "
                f"{c.fmt_p(r['p_valor'])} | {r['efeito']} = {c.fmt_num(r['valor_efeito'], 3)} "
                f"({r['magnitude']}) | {r['decisao']} |"
            )
        linhas.append("")
        for _, r in sub.iterrows():
            if r["observacao"]:
                linhas.append(f"- **{r['teste']}**: {r['observacao']}")
        linhas.append("")
        return linhas

    def desc_md(metrica: str) -> list[str]:
        sub = desc[desc["metrica"] == metrica]
        linhas = [
            "| tratamento | n | mediana | Q1 | Q3 | IQR | min | max |",
            "|---|---|---|---|---|---|---|---|",
        ]
        for _, r in sub.iterrows():
            linhas.append(
                f"| {r['tratamento']} | {int(r['n'])} | {c.fmt_num(r['mediana'])} | "
                f"{c.fmt_num(r['q1'])} | {c.fmt_num(r['q3'])} | {c.fmt_num(r['iqr'])} | "
                f"{c.fmt_num(r['min'])} | {c.fmt_num(r['max'])} |"
            )
        linhas.append("")
        return linhas

    md = [
        "# S03 - Resultados da RQ1 (tempo) e da RQ2 (defeitos)",
        "",
        "Gerado por `analise/rq1_rq2.py` a partir de `data/trials_consolidado.csv`.",
        "Nao editar a mao - o texto interpretativo vai em `docs/relatorio/`.",
        "",
        "## RQ1 - Tempo de resolucao (time-to-green, em segundos)",
        "",
        "H0: mediana(tempo_IA) = mediana(tempo_MANUAL) | H1: **IA < MANUAL** "
        "(unicaudal, alfa = 0,05)",
        "",
        "### Descritiva",
        "",
    ]
    md += desc_md("time_to_green_s")
    md += [
        f"Trials censurados (atingiram o time-box de {c.TIME_BOX_S}s): "
        f"IA = {int(censurados.get('IA', 0))}, MANUAL = {int(censurados.get('MANUAL', 0))}.",
        "",
        "### Medianas por kata (os blocos do Wilcoxon)",
        "",
        "| kata | IA | MANUAL | diferenca (IA - MANUAL) | par completo |",
        "|---|---|---|---|---|",
    ]
    for _, r in tempo.iterrows():
        md.append(
            f"| {r['kata']} | {c.fmt_num(r['IA'])} | {c.fmt_num(r['MANUAL'])} | "
            f"{c.fmt_num(r['diferenca_ia_menos_manual'])} | "
            f"{'sim' if r['par_completo'] else '**nao**'} |"
        )
    md += ["", f"**{pares} de 6 pares completos.**", "", "### Testes", ""]
    md += bloco("RQ1", "completo (18 trials)")
    md += [
        "### Analise de sensibilidade",
        "",
        "Previstas no plano (ameaca #5, contaminacao do autor das katas) e acrescentada a",
        "exclusao dos trials com cronometragem implausivel (ver `00-consolidacao.md`).",
        "",
        "**Sem os trials de P1:**",
        "",
    ]
    md += bloco("RQ1", "sem P1")
    md += ["**Sem os trials com cronometro suspeito:**", ""]
    md += bloco("RQ1", "sem cronometro suspeito")
    md += [
        "## RQ2 - Qualidade funcional (taxa de sucesso dos testes de aceitacao)",
        "",
        "H0: mediana(sucesso_IA) = mediana(sucesso_MANUAL) | H1: **IA > MANUAL** "
        "(unicaudal, alfa = 0,05)",
        "",
        "### Descritiva",
        "",
    ]
    md += desc_md("taxa_sucesso")
    md += ["### Testes", ""]
    md += bloco("RQ2", "completo (18 trials)")
    md += ["## Metrica exploratoria - numero de prompts (so tratamento IA)", ""]
    md += desc_md("n_prompts")
    return "\n".join(md) + "\n"


def main() -> int:
    c.cabecalho("S03 - RQ1 (tempo) e RQ2 (defeitos)")
    df = c.carregar_trials()

    print(
        f"{len(df)} trials | IA: {(df['tratamento'] == 'IA').sum()} | "
        f"MANUAL: {(df['tratamento'] == 'MANUAL').sum()} | "
        f"censurados: {int(df['censurado'].sum())}"
    )

    desc = descritivas(df)
    print("\nDescritiva (mediana [min - max]):")
    for _, r in desc.iterrows():
        print(
            f"  {r['metrica']:<16} {r['tratamento']:<7} n={int(r['n'])}  "
            f"mediana={c.fmt_num(r['mediana'])}  IQR={c.fmt_num(r['iqr'])}  "
            f"[{c.fmt_num(r['min'])} - {c.fmt_num(r['max'])}]"
        )

    # ---------------------------------------------------------------- RQ1 ---
    escopo = "completo (18 trials)"
    wilcoxon_por_kata(df, "time_to_green_s", "less", "RQ1", escopo)
    mann_whitney(df, "time_to_green_s", "less", "RQ1", escopo)

    # ---------------------------------------------------------------- RQ2 ---
    wilcoxon_por_kata(df, "taxa_sucesso", "greater", "RQ2", escopo)
    mann_whitney(df, "taxa_sucesso", "greater", "RQ2", escopo)

    if df["taxa_sucesso"].nunique() == 1:
        print(
            f"\n[RQ2] NOTA: todos os {len(df)} trials terminaram com taxa de sucesso "
            f"{c.fmt_num(df['taxa_sucesso'].iloc[0])} e nenhum foi censurado. Isso e um EFEITO "
            "TETO: nao ha variancia na variavel dependente, entao nenhum teste pode detectar "
            "diferenca. A RQ2 se responde pela descritiva, e a limitacao vai declarada no "
            "relatorio."
        )

    # ------------------------------------------------------- sensibilidade ---
    sem_p1 = df[df["integrante"] != "p1"]
    wilcoxon_por_kata(sem_p1, "time_to_green_s", "less", "RQ1", "sem P1")
    mann_whitney(sem_p1, "time_to_green_s", "less", "RQ1", "sem P1")

    sem_suspeitos = df[~df["cronometro_suspeito"].astype(bool)]
    if len(sem_suspeitos) < len(df):
        wilcoxon_por_kata(sem_suspeitos, "time_to_green_s", "less", "RQ1", "sem cronometro suspeito")
        mann_whitney(sem_suspeitos, "time_to_green_s", "less", "RQ1", "sem cronometro suspeito")

    res = pd.DataFrame(resultados)
    print("\narquivos gerados:")
    c.escrever_csv(res, c.RESULTADOS_RQ12)
    c.escrever_csv(desc, c.DATA / "descritivas_rq1_rq2.csv")
    c.escrever_md(montar_relatorio(df, desc, res), c.RESULTADOS / "rq1-rq2.md")
    print(
        "\nProximo passo: conferir docs/relatorio/03-resultados-rq1-rq2.md contra estes numeros."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
