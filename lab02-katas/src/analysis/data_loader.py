"""Leitura e limpeza de data/trials.csv e data/metrics.csv (Lab02 - Sprint 03, Passo 4).

Compartilhado pelas tres partes da analise (RQ1+RQ2, RQ3, dashboard) para que a
limpeza dos dados seja identica nas tres - nenhuma delas deve reimplementar as
regras abaixo.

Duas limpezas foram necessarias nos dados brutos, ambas documentadas aqui em vez de
feitas "no braco" numa planilha:

1. Duas linhas de 2026-09-14 (p1-kata-01-faixas-ia e p1-kata-02-espiral-manual, ambas
   com time_to_green_s = 4) sao autoteste do proprio script `run_trial.ps1`, escritas
   por engano no `data/trials.csv` real em vez de um arquivo temporario - resolver um
   kata MANUAL em 4 segundos e fisicamente impossivel. A execucao real da Sprint 02
   comecou em 2026-09-15.
2. Alguns trial_id aparecem mais de uma vez (reinicio do trial por ambiente quebrado,
   ver `scripts/run_trial.ps1`, exit code 3). Mantemos a tentativa mais recente
   (`inicio_iso` maximo) como a oficial.

Isso deixa exatamente 18 trials (3 integrantes x 6 katas) em `data/trials.csv` e
`data/metrics.csv`.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parents[2] / "data"

#: Trials anteriores a esta data sao autoteste do script, nao execucao real (ver
#: docstring do modulo, limpeza 1).
INICIO_EXECUCAO_REAL = "2026-09-15"


def load_trials(path: Path | None = None) -> pd.DataFrame:
    """Le e limpa `data/trials.csv`. Devolve exatamente 1 linha por trial_id."""
    csv_path = path or DATA_DIR / "trials.csv"
    frame = pd.read_csv(csv_path, encoding="utf-8-sig")
    frame["inicio_iso"] = pd.to_datetime(frame["inicio_iso"])

    frame = frame[frame["inicio_iso"] >= INICIO_EXECUCAO_REAL]
    frame = frame.sort_values("inicio_iso").drop_duplicates(subset="trial_id", keep="last")

    return frame.sort_values(["integrante", "ordem"]).reset_index(drop=True)


def load_metrics(path: Path | None = None) -> pd.DataFrame:
    """Le e limpa `data/metrics.csv`. Devolve exatamente 1 linha por trial_id.

    O CSV corrigido trazia blocos inteiros repetidos (reexecucoes de
    `run_metrics.ps1 -Todos` sem limpar o arquivo antes) - mantemos a ultima
    ocorrencia de cada trial_id, que reflete o codigo final de cada trial.
    """
    csv_path = path or DATA_DIR / "metrics.csv"
    frame = pd.read_csv(csv_path, encoding="utf-8-sig")
    frame = frame.drop_duplicates(subset="trial_id", keep="last")
    return frame.sort_values(["integrante", "kata"]).reset_index(drop=True)


def load_all(trials_path: Path | None = None, metrics_path: Path | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Atalho: carrega e valida trials + metrics juntos (18 linhas cada)."""
    trials = load_trials(trials_path)
    metrics = load_metrics(metrics_path)

    if len(trials) != 18:
        raise ValueError(f"esperava 18 trials apos limpeza, encontrei {len(trials)}")
    if len(metrics) != 18:
        raise ValueError(f"esperava 18 metrics apos limpeza, encontrei {len(metrics)}")

    return trials, metrics