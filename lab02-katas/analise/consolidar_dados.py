"""S03 - Passo 4, etapa 0: dataset canonico da RQ1/RQ2.

    python analise/consolidar_dados.py

O `data/trials.csv` e um log de append: o `run_trial.ps1` acrescenta uma linha a
cada execucao, inclusive nas de teste do proprio script. Rodar a analise direto
nele conta o mesmo trial duas vezes e move a mediana.

Este script transforma o log em dataset:

1. deduplica por `trial_id`, mantendo a execucao mais recente (`inicio_iso`);
2. valida o dataset contra o desenho (18 trials, 3x6, 9 IA / 9 MANUAL);
3. audita a cobertura por kata - quais katas tem os DOIS tratamentos, que e o
   que define o n do Wilcoxon pareado;
4. marca trials cujo tempo e curto demais para ser cronometragem de resolucao.

Saidas:
  data/trials_consolidado.csv     dataset canonico, entrada de todo o resto
  data/trials_descartados.csv     o que saiu, com motivo (auditoria)
  data/cobertura_katas.csv        cobertura IA/MANUAL por kata
  data/aderencia_desenho.csv      executado vs. planejado, por trial
  docs/resultados/00-consolidacao.md
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))

import comum as c  # noqa: E402

COLUNAS_NUMERICAS = [
    "ordem",
    "time_to_green_s",
    "testes_total",
    "testes_passando",
    "taxa_sucesso",
]


def carregar_bruto() -> pd.DataFrame:
    df = c.ler_csv(
        c.TRIALS_BRUTO,
        dica="este e o CSV que o scripts/run_trial.ps1 grava durante a S02.",
    )
    for coluna in COLUNAS_NUMERICAS:
        df[coluna] = pd.to_numeric(df[coluna], errors="coerce")
    df["n_prompts"] = pd.to_numeric(df.get("n_prompts"), errors="coerce")
    df["censurado"] = df["censurado"].astype(str).str.strip().str.lower() == "true"
    df["tratamento"] = df["tratamento"].astype(str).str.strip().str.upper()
    return df


def deduplicar(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Mantem a execucao mais recente de cada trial_id.

    A regra e "a ultima vale" porque o refazer de um trial (ambiente quebrado,
    engano na invocacao) acontece DEPOIS do registro errado, nunca antes.
    """
    ordenado = df.sort_values(["trial_id", "inicio_iso"], kind="stable")
    manter = ordenado.drop_duplicates("trial_id", keep="last")
    descartados = ordenado.loc[~ordenado.index.isin(manter.index)].copy()
    descartados["motivo"] = "execucao anterior do mesmo trial_id (superada por uma mais recente)"
    return manter.reset_index(drop=True), descartados.reset_index(drop=True)


def validar(df: pd.DataFrame) -> list[str]:
    """Checagens que, se falharem, invalidam a analise. Retorna a lista de falhas."""
    falhas: list[str] = []

    if len(df) != c.N_TRIALS_ESPERADO:
        falhas.append(
            f"{len(df)} trials apos deduplicar, o desenho preve {c.N_TRIALS_ESPERADO}"
        )

    for integrante in c.INTEGRANTES:
        katas = set(df.loc[df["integrante"] == integrante, "kata"])
        faltando = sorted(set(c.KATAS) - katas)
        if faltando:
            falhas.append(f"{integrante} nao tem trial para: {', '.join(faltando)}")

    por_tratamento = df["tratamento"].value_counts().to_dict()
    if por_tratamento.get("IA") != 9 or por_tratamento.get("MANUAL") != 9:
        falhas.append(f"balanco IA/MANUAL fora do desenho: {por_tratamento}")

    fora_do_intervalo = df[(df["taxa_sucesso"] < 0) | (df["taxa_sucesso"] > 1)]
    if not fora_do_intervalo.empty:
        falhas.append(
            "taxa_sucesso fora de [0,1] em: "
            + ", ".join(fora_do_intervalo["trial_id"])
            + " (sintoma classico de CSV gravado com virgula decimal)"
        )

    incoerentes = df[df["testes_passando"] > df["testes_total"]]
    if not incoerentes.empty:
        falhas.append("testes_passando > testes_total em: " + ", ".join(incoerentes["trial_id"]))

    censura_errada = df[df["censurado"] & (df["time_to_green_s"] != c.TIME_BOX_S)]
    if not censura_errada.empty:
        falhas.append(
            "trial censurado com tempo != time-box em: " + ", ".join(censura_errada["trial_id"])
        )

    return falhas


def auditar_cobertura(df: pd.DataFrame) -> pd.DataFrame:
    """Quantos trials de cada tratamento cada kata recebeu.

    O Wilcoxon do plano pareia POR KATA. Uma kata que so recebeu um dos
    tratamentos nao forma par e sai do teste - o que reduz o n efetivo abaixo
    dos 6 pares previstos no desenho.
    """
    linhas = []
    for kata in c.KATAS:
        bloco = df[df["kata"] == kata]
        n_ia = int((bloco["tratamento"] == "IA").sum())
        n_manual = int((bloco["tratamento"] == "MANUAL").sum())
        linhas.append(
            {
                "kata": kata,
                "n_ia": n_ia,
                "n_manual": n_manual,
                "par_completo": n_ia > 0 and n_manual > 0,
                "integrantes_ia": ",".join(
                    sorted(bloco.loc[bloco["tratamento"] == "IA", "integrante"])
                ),
                "integrantes_manual": ",".join(
                    sorted(bloco.loc[bloco["tratamento"] == "MANUAL", "integrante"])
                ),
            }
        )
    return pd.DataFrame(linhas)


def auditar_aderencia_ao_desenho(df: pd.DataFrame) -> pd.DataFrame:
    """Compara a alocacao executada com o quadrado latino de docs/desenho-experimento.md."""
    planejado = {
        ("p1", "kata-01-faixas"): "IA",
        ("p1", "kata-02-espiral"): "MANUAL",
        ("p1", "kata-03-duracao"): "IA",
        ("p1", "kata-04-romanos"): "MANUAL",
        ("p1", "kata-05-rainha"): "IA",
        ("p1", "kata-06-delimitadores"): "MANUAL",
        ("p2", "kata-03-duracao"): "MANUAL",
        ("p2", "kata-04-romanos"): "IA",
        ("p2", "kata-05-rainha"): "MANUAL",
        ("p2", "kata-06-delimitadores"): "IA",
        ("p2", "kata-01-faixas"): "MANUAL",
        ("p2", "kata-02-espiral"): "IA",
        ("p3", "kata-05-rainha"): "IA",
        ("p3", "kata-06-delimitadores"): "MANUAL",
        ("p3", "kata-01-faixas"): "MANUAL",
        ("p3", "kata-02-espiral"): "IA",
        ("p3", "kata-03-duracao"): "MANUAL",
        ("p3", "kata-04-romanos"): "IA",
    }
    linhas = []
    for _, linha in df.iterrows():
        esperado = planejado.get((linha["integrante"], linha["kata"]))
        linhas.append(
            {
                "trial_id": linha["trial_id"],
                "integrante": linha["integrante"],
                "kata": linha["kata"],
                "tratamento_executado": linha["tratamento"],
                "tratamento_planejado": esperado,
                "aderente": esperado == linha["tratamento"],
            }
        )
    return pd.DataFrame(linhas).sort_values(["integrante", "kata"]).reset_index(drop=True)


def marcar_cronometro_suspeito(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["cronometro_suspeito"] = df["time_to_green_s"] < c.LIMIAR_CRONOMETRO_SUSPEITO_S
    return df


def montar_relatorio(
    bruto: pd.DataFrame,
    consolidado: pd.DataFrame,
    descartados: pd.DataFrame,
    cobertura: pd.DataFrame,
    aderencia: pd.DataFrame,
    falhas: list[str],
) -> str:
    pares = int(cobertura["par_completo"].sum())
    suspeitos = consolidado[consolidado["cronometro_suspeito"]]
    desviantes = aderencia[~aderencia["aderente"]]

    linhas = [
        "# S03 - Consolidacao do dataset (auditoria)",
        "",
        "Gerado por `analise/consolidar_dados.py`. Nao editar a mao: rode o script de novo.",
        "",
        "## 1. Deduplicacao",
        "",
        f"- linhas no log bruto (`data/trials.csv`): **{len(bruto)}**",
        f"- trials distintos apos deduplicar: **{len(consolidado)}**",
        f"- linhas descartadas: **{len(descartados)}** (mantida sempre a execucao mais recente)",
        "",
    ]
    if not descartados.empty:
        linhas += [
            "| trial_id | inicio descartado | tempo (s) | motivo |",
            "|---|---|---|---|",
        ]
        for _, d in descartados.iterrows():
            linhas.append(
                f"| `{d['trial_id']}` | {d['inicio_iso']} | {int(d['time_to_green_s'])} | {d['motivo']} |"
            )
        linhas += [
            "",
            "As linhas acima ficam versionadas em `data/trials_descartados.csv` - descarte sem",
            "registro seria manipulacao de dado, ainda que involuntaria.",
            "",
        ]

    linhas += ["## 2. Validacao contra o desenho", ""]
    if falhas:
        linhas.append("**FALHAS ENCONTRADAS:**")
        linhas += [f"- {f}" for f in falhas]
    else:
        linhas.append(
            "Todas as checagens passaram: 18 trials, 3 integrantes x 6 katas, 9 IA / 9 MANUAL."
        )
    linhas.append("")

    linhas += [
        "## 3. Cobertura por kata - o n real do Wilcoxon",
        "",
        "| kata | trials IA | trials MANUAL | forma par? |",
        "|---|---|---|---|",
    ]
    for _, r in cobertura.iterrows():
        marca = "sim" if r["par_completo"] else "**NAO**"
        linhas.append(f"| {r['kata']} | {r['n_ia']} | {r['n_manual']} | {marca} |")
    linhas += ["", f"**Pares completos: {pares} de 6.**", ""]

    if pares < 6:
        p_min = c.p_minimo_wilcoxon(pares, unicaudal=True)
        linhas += [
            f"O plano de analise previa n = 6 pares. Com {pares}, o menor p-valor que o Wilcoxon",
            f"exato unicaudal pode produzir e **{c.fmt_p(p_min)}**"
            + (
                f" - acima de alfa = {c.ALFA}. Nessa configuracao o teste pareado NAO PODE rejeitar"
                " H0, por maior que seja o efeito."
                if p_min > c.ALFA
                else "."
            ),
            "O Mann-Whitney sobre os 18 trials individuais passa a ser o teste com poder, e o",
            "Wilcoxon entra como evidencia de direcao consistente entre blocos.",
            "",
        ]

    linhas += [
        "## 4. Aderencia ao contrabalanceamento planejado",
        "",
        f"Trials fora do quadrado latino de `docs/desenho-experimento.md`: "
        f"**{len(desviantes)}** de {len(aderencia)}.",
        "",
    ]
    if not desviantes.empty:
        linhas += ["| trial | planejado | executado |", "|---|---|---|"]
        for _, d in desviantes.iterrows():
            linhas.append(
                f"| `{d['integrante']} / {d['kata']}` | {d['tratamento_planejado']} "
                f"| {d['tratamento_executado']} |"
            )
        linhas += [
            "",
            "Desvio de execucao, nao erro de digitacao: e a causa direta das katas sem par da",
            "secao 3. Entra no relatorio final como ameaca a validade (item novo), com o efeito",
            "que teve sobre o n do teste pareado.",
            "",
        ]

    linhas += [
        "## 5. Trials com tempo curto demais para ser cronometragem",
        "",
        f"Limiar: {c.LIMIAR_CRONOMETRO_SUSPEITO_S} s (o `run_trial.ps1` so reavalia a suite a cada 5 s).",
        f"Trials marcados: **{len(suspeitos)}**.",
        "",
    ]
    if not suspeitos.empty:
        linhas += ["| trial_id | tratamento | tempo (s) |", "|---|---|---|"]
        for _, s in suspeitos.iterrows():
            linhas.append(f"| `{s['trial_id']}` | {s['tratamento']} | {int(s['time_to_green_s'])} |")
        linhas += [
            "",
            "Um verde em poucos segundos significa que o codigo ja estava escrito quando o",
            "cronometro comecou - o tempo registrado mede a execucao do Jest, nao a resolucao",
            "da kata. **Nenhum destes e descartado**: eles entram na analise de sensibilidade",
            "do `analise/rq1_rq2.py`, que refaz os testes sem eles e mostra se a conclusao muda.",
            "",
        ]

    return "\n".join(linhas) + "\n"


def main() -> int:
    c.cabecalho("S03 - consolidacao do dataset de trials")

    bruto = carregar_bruto()
    print(f"log bruto: {len(bruto)} linhas em {c.TRIALS_BRUTO.name}")

    consolidado, descartados = deduplicar(bruto)
    print(
        f"deduplicado: {len(consolidado)} trials distintos "
        f"({len(descartados)} linhas descartadas)"
    )

    consolidado = marcar_cronometro_suspeito(consolidado)
    consolidado = consolidado.sort_values(["integrante", "ordem"]).reset_index(drop=True)

    falhas = validar(consolidado)
    cobertura = auditar_cobertura(consolidado)
    aderencia = auditar_aderencia_ao_desenho(consolidado)

    print("\ncobertura por kata (o n do Wilcoxon sai daqui):")
    for _, r in cobertura.iterrows():
        marca = "par ok" if r["par_completo"] else "SEM PAR"
        print(f"  {r['kata']:<24} IA={r['n_ia']}  MANUAL={r['n_manual']}   {marca}")
    pares = int(cobertura["par_completo"].sum())
    print(f"  => {pares} pares completos de 6")

    desviantes = aderencia[~aderencia["aderente"]]
    if not desviantes.empty:
        print(f"\nAVISO: {len(desviantes)} trials fora do contrabalanceamento planejado:")
        for _, d in desviantes.iterrows():
            print(
                f"  {d['integrante']} / {d['kata']}: planejado {d['tratamento_planejado']}, "
                f"executado {d['tratamento_executado']}"
            )

    suspeitos = consolidado[consolidado["cronometro_suspeito"]]
    if not suspeitos.empty:
        print(
            f"\nAVISO: {len(suspeitos)} trials com time-to-green < "
            f"{c.LIMIAR_CRONOMETRO_SUSPEITO_S}s (marcados, nao descartados)"
        )

    print("\narquivos gerados:")
    c.escrever_csv(consolidado, c.TRIALS)
    c.escrever_csv(descartados, c.TRIALS_DESCARTADOS)
    c.escrever_csv(cobertura, c.DATA / "cobertura_katas.csv")
    c.escrever_csv(aderencia, c.DATA / "aderencia_desenho.csv")
    c.escrever_md(
        montar_relatorio(bruto, consolidado, descartados, cobertura, aderencia, falhas),
        c.RESULTADOS / "00-consolidacao.md",
    )

    if falhas:
        print("\nVALIDACAO FALHOU:")
        for f in falhas:
            print("  - " + f)
        print("\nO dataset foi gravado mesmo assim para inspecao, mas NAO rode a analise")
        print("antes de resolver os itens acima.")
        return 1

    print("\nValidacao OK. Proximo passo: python analise/rq1_rq2.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
