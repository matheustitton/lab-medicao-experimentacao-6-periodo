"""S03 - Passo 4: testes estatisticos da RQ3 (estrutura do codigo).

    python analise/rq3.py     (depende de scripts/run_metrics.ps1 e de analise/rq1_rq2.py)

RQ3: o uso de assistente de IA altera a complexidade ciclomatica ou a duplicacao do
codigo produzido?

Mesmo plano de `docs/desenho-experimento.md` usado na RQ1/RQ2, com a unica diferenca
prevista la: a RQ3 e BICAUDAL (nao ha direcao consensual para o efeito).

  1. Wilcoxon signed-rank pareado POR KATA          - teste principal
  2. Mann-Whitney U sobre os trials individuais     - teste secundario
  3. mediana e IQR em toda tabela (nunca media)     - descritiva
  4. tamanho de efeito reportado junto de todo p
  5. analise de sensibilidade                       - sem cada integrante (ameaca #5)

Metricas:
  cc_media          complexidade ciclomatica media por funcao   - primaria
  pct_duplicado     % de linhas duplicadas (jscpd)              - primaria
  loc               linhas de codigo                            - controle obrigatorio
  cc_soma_por_loc   complexidade somada normalizada por LOC     - leitura complementar

cc_soma_por_loc entra porque o desenho (secao B, decisao 2) registra que a media por
funcao "pune quem usa laco e premia quem usa array method" - a comparacao entre
tratamentos precisa da versao normalizada por tamanho, nao so da media bruta.

pct_duplicado nao e testado: so 1 dos 18 trials tem duplicacao, e o teste fica
degenerado. O script registra "nao aplicavel" com a razao, sem trocar de teste.

Saidas:
  data/metrics_consolidado.csv     metrics.csv deduplicado (18 linhas)
  data/resultados_rq3.csv          uma linha por teste executado
  data/descritivas_rq3.csv         mediana/IQR por tratamento
  docs/resultados/rq3.md           tabelas prontas para o relatorio final
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))

import comum as c  # noqa: E402
import rq1_rq2 as r12  # noqa: E402  - reusa os dois testes, sem reimplementar

RQ = "RQ3"
ALTERNATIVA = "two-sided"
METRICAS_TESTADAS = ("cc_media", "loc", "cc_soma_por_loc")
METRICAS_DESCRITIVAS = (
    "cc_media", "cc_max", "cc_soma", "n_funcoes", "loc", "cc_soma_por_loc", "pct_duplicado",
)
ROTULO = {
    "cc_media": "complexidade ciclomatica media por funcao",
    "cc_max": "complexidade ciclomatica maxima",
    "cc_soma": "complexidade ciclomatica somada",
    "n_funcoes": "numero de funcoes",
    "loc": "LOC (controle)",
    "cc_soma_por_loc": "complexidade somada / LOC",
    "pct_duplicado": "% de linhas duplicadas",
}


def consolidar_metrics() -> pd.DataFrame:
    """metrics.csv acumula uma linha por execucao do run_metrics.ps1 - fica a ultima de cada trial."""
    bruto = c.ler_csv(c.METRICS_BRUTO, dica="rode antes:  .\\scripts\\run_metrics.ps1 -Todos")
    df = bruto.drop_duplicates("trial_id", keep="last").sort_values(["integrante", "kata"])
    df = df.reset_index(drop=True)
    c.exigir(
        len(df) == c.N_TRIALS_ESPERADO,
        f"{c.METRICS_BRUTO.name} tem {len(df)} trials distintos, esperado {c.N_TRIALS_ESPERADO}.",
    )
    trials = set(c.carregar_trials()["trial_id"])
    faltando = trials - set(df["trial_id"])
    c.exigir(not faltando, "trials sem metricas estaticas: " + ", ".join(sorted(faltando)))
    print(f"{len(bruto)} linhas em {c.METRICS_BRUTO.name} -> {len(df)} trials distintos")
    return df


def descritivas(df: pd.DataFrame) -> pd.DataFrame:
    return pd.concat(
        [c.resumo_por_tratamento(df, m) for m in METRICAS_DESCRITIVAS], ignore_index=True
    )


def registrar_duplicacao_nao_aplicavel(df: pd.DataFrame) -> int:
    com_dup = df[df["pct_duplicado"] > 0]
    trials = ", ".join(f"{r.trial_id} ({c.fmt_num(r.pct_duplicado)}%)" for r in com_dup.itertuples())
    razao = (
        f"so {len(com_dup)} de {len(df)} trials com duplicacao ({trials or 'nenhum'}) - "
        "variancia quase nula, teste degenerado"
    )
    print(f"\n[{RQ}] pct_duplicado: testes nao executados - {razao}")
    for teste, efeito in (("Wilcoxon pareado por kata", "rank-biserial pareado"),
                          ("Mann-Whitney U", "Cliff's delta")):
        r12.registrar(
            rq=RQ, metrica="pct_duplicado", escopo="completo (18 trials)", teste=teste,
            n=float("nan"), estatistica=float("nan"), p_valor=float("nan"),
            alternativa=ALTERNATIVA, efeito=efeito, valor_efeito=float("nan"),
            magnitude="indefinido", decisao="nao aplicavel", observacao=razao,
        )
    return len(com_dup)


def montar_relatorio(df: pd.DataFrame, desc: pd.DataFrame, res: pd.DataFrame) -> str:
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

    def kata_md(metrica: str) -> list[str]:
        tabela = c.medianas_por_kata(df, metrica)
        linhas = [
            "| kata | IA | MANUAL | diferenca (IA - MANUAL) | par completo |",
            "|---|---|---|---|---|",
        ]
        for _, r in tabela.iterrows():
            linhas.append(
                f"| {r['kata']} | {c.fmt_num(r['IA'])} | {c.fmt_num(r['MANUAL'])} | "
                f"{c.fmt_num(r['diferenca_ia_menos_manual'])} | "
                f"{'sim' if r['par_completo'] else '**nao**'} |"
            )
        linhas.append("")
        return linhas

    def bloco(metrica: str, escopo: str) -> list[str]:
        sub = res[(res["metrica"] == metrica) & (res["escopo"] == escopo)]
        if sub.empty:
            return ["_sem resultado para este escopo._", ""]
        linhas = [
            "| teste | n | estatistica | p-valor | efeito | decisao (alfa = 0,05) |",
            "|---|---|---|---|---|---|",
        ]
        for _, r in sub.iterrows():
            n = "n/a" if pd.isna(r["n"]) else str(int(r["n"]))
            linhas.append(
                f"| {r['teste']} | {n} | {c.fmt_num(r['estatistica'], 1)} | "
                f"{c.fmt_p(r['p_valor'])} | {r['efeito']} = {c.fmt_num(r['valor_efeito'], 3)} "
                f"({r['magnitude']}) | {r['decisao']} |"
            )
        linhas.append("")
        for _, r in sub.iterrows():
            if isinstance(r["observacao"], str) and r["observacao"]:
                linhas.append(f"- **{r['teste']}**: {r['observacao']}")
        linhas.append("")
        return linhas

    md = [
        "# S03 - Resultados da RQ3 (estrutura do codigo)",
        "",
        "Gerado por `analise/rq3.py` a partir de `data/metrics_consolidado.csv`.",
        "Nao editar a mao - o texto interpretativo vai em `docs/relatorio/`.",
        "",
        "H0: mediana(metrica_IA) = mediana(metrica_MANUAL) | H1: as medianas **diferem** "
        "(bicaudal, alfa = 0,05)",
        "",
    ]
    for metrica in ("cc_media", "loc"):
        md += [f"## {metrica} - {ROTULO[metrica]}", "", "### Descritiva", ""]
        md += desc_md(metrica)
        md += ["### Medianas por kata (os blocos do Wilcoxon)", ""]
        md += kata_md(metrica)
        md += ["### Testes", ""]
        md += bloco(metrica, "completo (18 trials)")

    md += [
        "## pct_duplicado - % de linhas duplicadas (jscpd)",
        "",
        "### Descritiva",
        "",
    ]
    md += desc_md("pct_duplicado")
    md += bloco("pct_duplicado", "completo (18 trials)")

    md += [
        "## cc_soma_por_loc - complexidade normalizada por tamanho",
        "",
        "Leitura complementar exigida pelo desenho (secao B, decisao 2): a media por funcao",
        "depende do estilo (laco vs. array method), a soma por LOC nao.",
        "",
        "### Descritiva",
        "",
    ]
    md += desc_md("cc_soma_por_loc")
    md += ["### Testes", ""]
    md += bloco("cc_soma_por_loc", "completo (18 trials)")

    md += ["## Demais metricas de complexidade (so descritiva)", ""]
    for metrica in ("cc_max", "cc_soma", "n_funcoes"):
        md += [f"**{metrica}** - {ROTULO[metrica]}", ""]
        md += desc_md(metrica)

    md += [
        "## Analise de sensibilidade - cc_media sem cada integrante",
        "",
        "Previsto no plano sem P1 (ameaca #5, contaminacao do autor das katas); repetido",
        "sem P2 e sem P3 para mostrar se algum integrante sozinho carrega o resultado.",
        "",
    ]
    for pessoa in c.INTEGRANTES:
        md += [f"**Sem os trials de {pessoa.upper()}:**", ""]
        md += bloco("cc_media", f"sem {pessoa.upper()}")

    md += ["## Trials por metrica (dado bruto consolidado)", ""]
    md += [
        "| trial | tratamento | loc | cc_media | cc_max | cc_soma_por_loc | pct_duplicado |",
        "|---|---|---|---|---|---|---|",
    ]
    for _, r in df.sort_values(["tratamento", "kata"]).iterrows():
        md.append(
            f"| {r['trial_id']} | {r['tratamento']} | {int(r['loc'])} | {c.fmt_num(r['cc_media'])} | "
            f"{int(r['cc_max'])} | {c.fmt_num(r['cc_soma_por_loc'], 4)} | "
            f"{c.fmt_num(r['pct_duplicado'])} |"
        )
    return "\n".join(md) + "\n"


def main() -> int:
    c.cabecalho("S03 - RQ3 (complexidade, duplicacao, LOC)")
    df = consolidar_metrics()

    desc = descritivas(df)
    print("\nDescritiva (mediana [Q1 - Q3]):")
    for _, r in desc.iterrows():
        print(
            f"  {r['metrica']:<16} {r['tratamento']:<7} n={int(r['n'])}  "
            f"mediana={c.fmt_num(r['mediana'])}  [Q1={c.fmt_num(r['q1'])}  Q3={c.fmt_num(r['q3'])}]"
        )

    escopo = "completo (18 trials)"
    for metrica in METRICAS_TESTADAS:
        r12.wilcoxon_por_kata(df, metrica, ALTERNATIVA, RQ, escopo)
        r12.mann_whitney(df, metrica, ALTERNATIVA, RQ, escopo)
    registrar_duplicacao_nao_aplicavel(df)

    for pessoa in c.INTEGRANTES:
        sub = df[df["integrante"] != pessoa]
        r12.wilcoxon_por_kata(sub, "cc_media", ALTERNATIVA, RQ, f"sem {pessoa.upper()}")
        r12.mann_whitney(sub, "cc_media", ALTERNATIVA, RQ, f"sem {pessoa.upper()}")

    res = pd.DataFrame([r for r in r12.resultados if r["rq"] == RQ])
    res["n"] = res["n"].astype("Int64")
    print("\narquivos gerados:")
    c.escrever_csv(df, c.METRICS)
    c.escrever_csv(res, c.RESULTADOS_RQ3)
    c.escrever_csv(desc, c.DATA / "descritivas_rq3.csv")
    c.escrever_md(montar_relatorio(df, desc, res), c.RESULTADOS / "rq3.md")
    print("\nProximo passo: conferir docs/relatorio/04-resultados-rq3.md contra estes numeros.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
