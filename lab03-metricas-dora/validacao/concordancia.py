"""Concordância entre avaliadores (kappa de Fleiss) e consolidação do consenso.

Uso: python -m validacao.concordancia --config config.yaml
Protocolo de desempate: maioria simples (2 de 3). Casos 1-1-1 vão para
rotulos/consenso_pendentes.csv e são decididos em reunião, registrando o resultado em
rotulos/desempate_reuniao.csv (colunas: nivel, chave, dimensao, rotulo_final).
"""
import argparse
import os
from collections import Counter
from typing import Dict, List, Optional

import numpy as np
import pandas as pd
from statsmodels.stats.inter_rater import aggregate_raters, fleiss_kappa

from pipeline.config import carregar_config

DIMENSOES = {
    "repos": {"chave": ["repo"], "colunas": ["tipo_projeto", "releases_entregas_reais"]},
    "releases": {"chave": ["repo", "tag"], "colunas": ["corretiva"]},
}
VALIDOS = {
    "tipo_projeto": {"biblioteca_framework", "aplicacao_servico", "cli", "outro"},
    "releases_entregas_reais": {"sim", "nao", "incerto"},
    "corretiva": {"sim", "nao"},
}


def interpretar_kappa(k: float) -> str:
    """Landis & Koch (1977)."""
    if k != k:
        return "indefinido (sem variação nos rótulos)"
    if k < 0:
        return "pobre"
    for limite, nome in [(0.20, "leve"), (0.40, "razoável"), (0.60, "moderada"),
                         (0.80, "substancial"), (1.00, "quase perfeita")]:
        if k <= limite:
            return nome
    return "quase perfeita"


def kappa_fleiss(rotulos: List[List[str]]) -> float:
    """rotulos[i][j] = rótulo do avaliador j para o item i."""
    categorias = sorted({r for linha in rotulos for r in linha})
    indice = {c: i for i, c in enumerate(categorias)}
    codigos = np.array([[indice[r] for r in linha] for linha in rotulos])
    tabela, _ = aggregate_raters(codigos)
    if np.count_nonzero(tabela.sum(axis=0)) < 2:
        return float("nan")
    return float(fleiss_kappa(tabela, method="fleiss"))


def concordancia_bruta(rotulos: List[List[str]]) -> float:
    return float(np.mean([len(set(l)) == 1 for l in rotulos]))


def consenso_maioria(rotulos: List[str]) -> Optional[str]:
    rotulo, n = Counter(rotulos).most_common(1)[0]
    return rotulo if n >= 2 else None


def carregar_rotulos(rotulos_dir: str, avaliadores: List[str], nivel: str) -> pd.DataFrame:
    """Formato longo: nivel, chave, dimensao, avaliador, valor. Falha se houver célula vazia/inválida."""
    spec, partes = DIMENSOES[nivel], []
    for nome in avaliadores:
        df = pd.read_csv(os.path.join(rotulos_dir, f"rotulos_{nome}_{nivel}.csv"), dtype=str).fillna("")
        for col in spec["colunas"]:
            valores = df[col].str.strip().str.lower()
            invalidos = df[~valores.isin(VALIDOS[col])]
            if len(invalidos):
                raise ValueError(f"{nome}/{nivel}: {len(invalidos)} valores vazios ou inválidos em '{col}' "
                                 f"(linhas {list(invalidos.index[:5] + 2)}...). Aceitos: {sorted(VALIDOS[col])}")
            partes.append(pd.DataFrame({
                "nivel": nivel,
                "chave": df[spec["chave"]].agg("@".join, axis=1),
                "dimensao": col, "avaliador": nome, "valor": valores,
            }))
    return pd.concat(partes, ignore_index=True)


def analisar(longo: pd.DataFrame, avaliadores: List[str], desempates: Optional[pd.DataFrame] = None):
    """Retorna (tabela de kappa por dimensão, consenso, pendentes)."""
    kappas, consenso, pendentes = [], [], []
    for dim, g in longo.groupby("dimensao"):
        matriz = g.pivot(index="chave", columns="avaliador", values="valor")[avaliadores]
        linhas = matriz.values.tolist()
        k = kappa_fleiss(linhas)
        kappas.append({"dimensao": dim, "n_itens": len(linhas), "kappa_fleiss": round(k, 4),
                       "interpretacao": interpretar_kappa(k),
                       "concordancia_bruta": round(concordancia_bruta(linhas), 4)})
        for chave, linha in zip(matriz.index, linhas):
            nivel = g["nivel"].iloc[0]
            final = consenso_maioria(linha)
            if final is None and desempates is not None:
                m = desempates[(desempates.nivel == nivel) & (desempates.chave == chave) & (desempates.dimensao == dim)]
                final = m["rotulo_final"].iloc[0] if len(m) else None
            reg = {"nivel": nivel, "chave": chave, "dimensao": dim, **dict(zip(avaliadores, linha))}
            (consenso if final else pendentes).append({**reg, "consenso": final} if final else reg)
    base = ["nivel", "chave", "dimensao"] + list(avaliadores)
    return (pd.DataFrame(kappas),
            pd.DataFrame(consenso, columns=base + ["consenso"]),
            pd.DataFrame(pendentes, columns=base))        # colunas fixas: CSV vazio mantém o cabeçalho


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config.yaml")
    args = ap.parse_args()
    cfg = carregar_config(args.config)
    longo = pd.concat([carregar_rotulos(cfg.rotulos_dir, cfg.avaliadores, n) for n in DIMENSOES])
    arq_des = os.path.join(cfg.rotulos_dir, "desempate_reuniao.csv")
    desempates = pd.read_csv(arq_des, dtype=str) if os.path.exists(arq_des) else None
    kappas, consenso, pendentes = analisar(longo, cfg.avaliadores, desempates)
    os.makedirs(cfg.saida_dir, exist_ok=True)
    kappas.to_csv(os.path.join(cfg.saida_dir, "kappa_fleiss.csv"), index=False)
    consenso.to_csv(os.path.join(cfg.rotulos_dir, "consenso.csv"), index=False)
    pendentes.to_csv(os.path.join(cfg.rotulos_dir, "consenso_pendentes.csv"), index=False)
    print(kappas.to_string(index=False))
    print(f"\nconsenso: {len(consenso)} itens | pendentes (1-1-1): {len(pendentes)}")


if __name__ == "__main__":
    main()
