"""DataFrame sintético com as colunas do dataset_dora.csv usadas pelas análises da Sprint 3."""
import numpy as np
import pandas as pd


def df_sintetico(n: int = 60, semente: int = 7) -> pd.DataFrame:
    rng = np.random.default_rng(semente)
    freq = np.sort(rng.uniform(0.1, 3.0, n))
    return pd.DataFrame({
        "repo": [f"org/r{i}" for i in range(n)],
        "linguagem": rng.choice(["Python", "Go", "Rust", "Zig"], n, p=[0.45, 0.3, 0.2, 0.05]),
        "estrelas": rng.integers(1000, 50000, n),
        "contribuidores": rng.integers(3, 500, n),
        "idade_dias": rng.integers(200, 4000, n),
        "freq_deploy_semana": freq,
        "lead_time_a_h": rng.uniform(5, 2000, n),
        "lead_time_b_h": rng.uniform(5, 1500, n),
        "cfr_ci": rng.uniform(0, 0.4, n),
        "cfr_entrega": np.clip(freq / 3 + rng.normal(0, 0.05, n), 0, 1),
        "recuperacao_h": np.where(np.arange(n) % 10 == 0, np.nan, rng.uniform(0.2, 90, n)),
        "classe_dora_c1": rng.choice(["Elite", "High", "Medium", "Low"], n),
        "n_episodios": np.where(np.arange(n) % 10 == 0, 0, 5),
        "n_episodios_censurados": np.where(np.arange(n) % 7 == 0, 1, 0),
        "prop_episodios_censurados": np.where(np.arange(n) % 7 == 0, 0.2, 0.0),
        "n_releases_censuradas": 1,
        "n_lead_negativos": np.where(np.arange(n) % 20 == 0, 2, 0),
        "teto_runs_atingido": False,
    })
