"""Infraestrutura comum da analise da S03.

Tudo que os scripts de analise compartilham mora aqui: caminhos, constantes do
desenho experimental, leitura/escrita de CSV a prova das duas armadilhas do
PowerShell 5.1 (BOM e virgula decimal), estatistica descritiva e tamanhos de efeito.

Nenhum script de analise deve reimplementar nada deste modulo - se cada frente
calcular mediana de um jeito diferente, o relatorio sai com tres numeros
diferentes para a mesma coisa.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterable, Sequence

import pandas as pd

# ---------------------------------------------------------------- caminhos ---

RAIZ = Path(__file__).resolve().parent.parent
DATA = RAIZ / "data"
DOCS = RAIZ / "docs"
FIGURAS = DOCS / "figuras"
RESULTADOS = DOCS / "resultados"

TRIALS_BRUTO = DATA / "trials.csv"                      # escrito pelo run_trial.ps1
TRIALS = DATA / "trials_consolidado.csv"                # saida do consolidar_dados.py
TRIALS_DESCARTADOS = DATA / "trials_descartados.csv"
METRICS_BRUTO = DATA / "metrics.csv"                    # escrito pelo run_metrics.ps1
METRICS = DATA / "metrics_consolidado.csv"              # saida do rq3.py
POOL_DUPLICACAO = DATA / "metrics_duplicacao_pool.csv"
RESULTADOS_RQ12 = DATA / "resultados_rq1_rq2.csv"
RESULTADOS_RQ3 = DATA / "resultados_rq3.csv"

# ------------------------------------------------- constantes do desenho ----

ALFA = 0.05
TIME_BOX_S = 2100                 # 35 min, docs/desenho-experimento.md secao (G)
N_TRIALS_ESPERADO = 18            # 3 integrantes x 6 katas
INTEGRANTES: tuple[str, ...] = ("p1", "p2", "p3")
TRATAMENTOS: tuple[str, ...] = ("IA", "MANUAL")
KATAS: tuple[str, ...] = (
    "kata-01-faixas",
    "kata-02-espiral",
    "kata-03-duracao",
    "kata-04-romanos",
    "kata-05-rainha",
    "kata-06-delimitadores",
)
ROTULO_KATA = {
    "kata-01-faixas": "K1 faixas",
    "kata-02-espiral": "K2 espiral",
    "kata-03-duracao": "K3 duracao",
    "kata-04-romanos": "K4 romanos",
    "kata-05-rainha": "K5 rainha",
    "kata-06-delimitadores": "K6 delimit.",
}

# Abaixo deste tempo o trial nao e cronometragem de resolucao: o run_trial.ps1
# so reavalia a suite a cada 5 s, entao um verde em menos de 30 s significa que o
# codigo ja existia quando o cronometro comecou. Nao se descarta nada por isso -
# o dado e marcado e entra na analise de sensibilidade.
LIMIAR_CRONOMETRO_SUSPEITO_S = 30

# -------------------------------------------------------- cores dos graficos -
# Slots 1 e 2 da paleta categorica de referencia. Validados para daltonismo
# (delta E 24,7 sob protanopia e 33,6 em visao normal - ambos acima do piso).
COR = {"IA": "#2a78d6", "MANUAL": "#eb6834"}
COR_NEUTRA = "#8a8984"
COR_TEXTO = "#0b0b0b"
COR_TEXTO_SEC = "#52514e"
COR_GRID = "#e6e5e1"
COR_SUPERFICIE = "#fcfcfb"

# ------------------------------------------------------------ utilitarios ---


def cabecalho(titulo: str) -> None:
    print()
    print("=" * 78)
    print(titulo)
    print("=" * 78)


def exigir(condicao: bool, mensagem: str) -> None:
    """Aborta com mensagem acionavel em vez de estourar um traceback obscuro."""
    if not condicao:
        print("\nERRO: " + mensagem, file=sys.stderr)
        sys.exit(1)


def ler_csv(caminho: Path, dica: str = "") -> pd.DataFrame:
    """Le CSV tolerando o BOM que o PowerShell insiste em gravar.

    O encoding utf-8-sig e obrigatorio: sem ele a primeira coluna vira
    "<BOM>trial_id" e todo acesso por nome falha com KeyError.
    """
    if not caminho.exists():
        msg = "arquivo nao encontrado: " + str(caminho)
        if dica:
            msg += "\n       " + dica
        exigir(False, msg)
    df = pd.read_csv(caminho, encoding="utf-8-sig")
    df.columns = [c.strip().lstrip("﻿") for c in df.columns]
    return df


def escrever_csv(df: pd.DataFrame, caminho: Path) -> None:
    """Grava UTF-8 sem BOM, decimal com ponto e LF - o mesmo contrato dos .ps1."""
    caminho.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(caminho, index=False, encoding="utf-8", lineterminator="\n")
    print("  -> " + str(caminho.relative_to(RAIZ)) + "  (" + str(len(df)) + " linhas)")


def escrever_md(texto: str, caminho: Path) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(texto, encoding="utf-8", newline="\n")
    print("  -> " + str(caminho.relative_to(RAIZ)))


def carregar_trials() -> pd.DataFrame:
    """Dataset canonico da RQ1/RQ2 - 18 linhas, uma por trial."""
    df = ler_csv(TRIALS, dica="rode antes:  python analise/consolidar_dados.py")
    exigir(
        len(df) == N_TRIALS_ESPERADO,
        f"{TRIALS.name} tem {len(df)} linhas, esperado {N_TRIALS_ESPERADO}. "
        "Rode o consolidar_dados.py de novo.",
    )
    return df


# ------------------------------------------------ estatistica descritiva ----


def mediana_iqr(valores: Sequence[float]) -> tuple[float, float, float, float]:
    """(mediana, q1, q3, iqr). Mediana e IQR, nunca media e desvio: N pequeno."""
    s = pd.Series(list(valores), dtype="float64")
    q1, q3 = s.quantile(0.25), s.quantile(0.75)
    return float(s.median()), float(q1), float(q3), float(q3 - q1)


def resumo_por_tratamento(df: pd.DataFrame, coluna: str) -> pd.DataFrame:
    """Uma linha por tratamento: n, mediana, IQR, min, max."""
    linhas = []
    for tratamento in TRATAMENTOS:
        valores = df.loc[df["tratamento"] == tratamento, coluna].dropna()
        if valores.empty:
            continue
        mediana, q1, q3, iqr = mediana_iqr(valores)
        linhas.append(
            {
                "metrica": coluna,
                "tratamento": tratamento,
                "n": int(len(valores)),
                "mediana": round(mediana, 4),
                "q1": round(q1, 4),
                "q3": round(q3, 4),
                "iqr": round(iqr, 4),
                "min": round(float(valores.min()), 4),
                "max": round(float(valores.max()), 4),
            }
        )
    return pd.DataFrame(linhas)


def medianas_por_kata(df: pd.DataFrame, coluna: str) -> pd.DataFrame:
    """Bloco do Wilcoxon: uma linha por kata, a mediana de cada tratamento.

    Retorna sempre as 6 katas, com NaN onde o tratamento nao foi executado -
    as katas incompletas precisam aparecer no relatorio, nao sumir num dropna.
    """
    tabela = df.pivot_table(
        index="kata", columns="tratamento", values=coluna, aggfunc="median"
    ).reindex(index=list(KATAS), columns=list(TRATAMENTOS))
    tabela.columns = [str(c) for c in tabela.columns]
    tabela = tabela.reset_index()
    tabela["par_completo"] = tabela[["IA", "MANUAL"]].notna().all(axis=1)
    tabela["diferenca_ia_menos_manual"] = tabela["IA"] - tabela["MANUAL"]
    return tabela


# --------------------------------------------------- tamanhos de efeito ----


def cliffs_delta(a: Iterable[float], b: Iterable[float]) -> tuple[float, str]:
    """Cliff's delta entre duas amostras independentes.

    delta = P(a > b) - P(a < b). Nao parametrico, sem suposicao de distribuicao,
    e identico a correlacao rank-biserial do Mann-Whitney. Limiares de
    Romano et al. (2006): 0,147 / 0,33 / 0,474.
    """
    xs, ys = list(a), list(b)
    if not xs or not ys:
        return float("nan"), "indefinido"
    maiores = sum(1 for x in xs for y in ys if x > y)
    menores = sum(1 for x in xs for y in ys if x < y)
    delta = (maiores - menores) / (len(xs) * len(ys))
    mag = abs(delta)
    if mag < 0.147:
        rotulo = "desprezivel"
    elif mag < 0.33:
        rotulo = "pequeno"
    elif mag < 0.474:
        rotulo = "medio"
    else:
        rotulo = "grande"
    return round(delta, 4), rotulo


def rank_biserial_pareado(diferencas: Iterable[float]) -> float:
    """Correlacao rank-biserial pareada - o tamanho de efeito do Wilcoxon.

    (soma dos postos positivos - soma dos negativos) / soma total dos postos.
    Varia em [-1, 1]; 1 = toda diferenca na mesma direcao.
    """
    difs = [d for d in diferencas if d == d and d != 0]  # descarta NaN e zeros
    if not difs:
        return float("nan")
    postos = pd.Series([abs(d) for d in difs]).rank().tolist()
    positivos = sum(p for p, d in zip(postos, difs) if d > 0)
    negativos = sum(p for p, d in zip(postos, difs) if d < 0)
    total = positivos + negativos
    return round((positivos - negativos) / total, 4) if total else float("nan")


def p_minimo_wilcoxon(n_pares: int, unicaudal: bool) -> float:
    """Menor p-valor alcancavel pelo Wilcoxon exato com n pares.

    Com n pares todos na mesma direcao o p exato e 1/2^n (unicaudal). Com n = 4
    isso da 0,0625 - acima de alfa = 0,05. Ou seja: existe N em que o teste NAO
    PODE rejeitar H0, por mais forte que seja o efeito. Isso precisa aparecer no
    relatorio, e nao ser confundido com "ausencia de efeito".
    """
    if n_pares <= 0:
        return float("nan")
    p = 1 / (2 ** n_pares)
    return round(p if unicaudal else min(1.0, 2 * p), 6)


def holm_bonferroni(pvalores: Sequence[float]) -> list[float]:
    """Correcao de Holm-Bonferroni para uma familia de testes.

    Menos conservadora que Bonferroni puro e sem suposicao de independencia -
    apropriada para as 7 metricas da RQ3, que sao correlacionadas entre si.
    """
    m = len(pvalores)
    if m == 0:
        return []
    indexados = sorted((p if p == p else 1.0, i) for i, p in enumerate(pvalores))
    ajustados = [0.0] * m
    corrente = 0.0
    for posicao, (p, indice_original) in enumerate(indexados):
        valor = min(1.0, (m - posicao) * p)
        corrente = max(corrente, valor)  # garante monotonicidade
        ajustados[indice_original] = round(corrente, 6)
    return ajustados


def fmt_p(p: float) -> str:
    if p != p:
        return "n/a"
    return "< 0,0001" if p < 0.0001 else f"{p:.4f}".replace(".", ",")


def fmt_num(v: float, casas: int = 2) -> str:
    if v != v:
        return "n/a"
    return f"{v:.{casas}f}".replace(".", ",")
