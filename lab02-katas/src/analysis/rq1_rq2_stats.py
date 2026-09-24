"""RQ1 (tempo) e RQ2 (defeitos) - Lab02 Sprint 03, Passo 4.

    python -m src.analysis.rq1_rq2_stats

RQ1: o uso de assistente de IA reduz o tempo ate passar em todos os testes?
RQ2: o uso de assistente de IA reduz a quantidade de defeitos no codigo produzido?

Segue o "Plano de analise estatistica" de docs/desenho-experimento.md, fixado antes
da coleta:
    1. Wilcoxon signed-rank pareado por kata (teste principal)
    2. Mann-Whitney U sobre os 18 trials (teste secundario)
    3. Mediana/Q1/Q3 (nunca media/desvio)
    4. Effect size junto de todo p-valor
    5. Sensibilidade excluindo quem escreveu as katas (ameaca de validade #5)

Ver `stats_utils.py` para o desvio descoberto na limpeza dos dados: so 4 das 6 katas
planejadas tem os dois tratamentos representados na execucao real (n=4 no teste
principal, nao os n=6 planejados) - reportado explicitamente, nao escondido.
"""

from __future__ import annotations

import pandas as pd

from src.analysis.data_loader import load_trials
from src.analysis.stats_utils import mann_whitney, resumo, sensibilidade_excluindo, wilcoxon_por_kata

#: Trials de IA com tempo abaixo disto sao suspeitos de vazamento de solucao (a pessoa
#: pode ja ter tido a resposta pronta antes do cronometro comecar) - reportados a
#: parte, nunca removidos da analise principal sem dizer.
LIMIAR_SUSPEITO_S = 10


def rq1_tempo(trials: pd.DataFrame) -> dict:
    ia = trials[trials.tratamento == "IA"]["time_to_green_s"]
    manual = trials[trials.tratamento == "MANUAL"]["time_to_green_s"]

    suspeitos = trials[(trials.tratamento == "IA") & (trials.time_to_green_s < LIMIAR_SUSPEITO_S)]

    return {
        "ia": resumo(ia),
        "manual": resumo(manual),
        "wilcoxon_por_kata": wilcoxon_por_kata(trials, "time_to_green_s"),
        "mann_whitney": mann_whitney(trials, "time_to_green_s"),
        "trials_suspeitos": suspeitos["trial_id"].tolist(),
    }


def rq2_defeitos(trials: pd.DataFrame) -> dict:
    resultado: dict = {}
    for tratamento in ("IA", "MANUAL"):
        subframe = trials[trials.tratamento == tratamento]
        resultado[tratamento] = {
            "n_trials": int(len(subframe)),
            "taxa_sucesso_media": round(float(subframe["taxa_sucesso"].mean()), 4),
            "trials_com_falha": int((subframe["testes_passando"] < subframe["testes_total"]).sum()),
        }
    resultado["variancia_nula"] = bool((trials["taxa_sucesso"] == 1.0).all())
    return resultado


def main() -> int:
    trials = load_trials()

    r1 = rq1_tempo(trials)
    print("=== RQ1 - Tempo (time-to-green) ===")
    print(f"IA:     {r1['ia']}")
    print(f"MANUAL: {r1['manual']}")

    wk = r1["wilcoxon_por_kata"]
    print(f"\nWilcoxon por kata (principal): n={wk['n_katas_valido']} de {wk['n_katas_planejado']} planejadas")
    print(f"  katas usadas: {wk['katas_usadas']}")
    print(f"  katas excluidas (so 1 tratamento): {wk['katas_excluidas']}")
    print(f"  estatistica={wk['statistic']}, p={wk['p']}, effect_size_r={wk['effect_size_r']}")

    mw = r1["mann_whitney"]
    print(f"\nMann-Whitney U (secundario, 9 vs 9): estatistica={mw['statistic']}, p={mw['p']:.4f}, effect_size_r={mw['effect_size_r']}")

    print(f"\nTrials de IA suspeitos (<{LIMIAR_SUSPEITO_S}s): {r1['trials_suspeitos']}")

    print("\n--- Sensibilidade: excluindo cada integrante (ameaca #5) ---")
    for pessoa in ("p1", "p2", "p3"):
        sens = sensibilidade_excluindo(trials, "time_to_green_s", pessoa)
        wk_s = sens["wilcoxon_por_kata"]
        print(f"  sem {pessoa}: Wilcoxon-por-kata n={wk_s['n_katas_valido']} p={wk_s['p']} | "
              f"Mann-Whitney p={sens['mann_whitney']['p']:.4f}")

    r2 = rq2_defeitos(trials)
    print("\n=== RQ2 - Defeitos ===")
    print(r2)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())