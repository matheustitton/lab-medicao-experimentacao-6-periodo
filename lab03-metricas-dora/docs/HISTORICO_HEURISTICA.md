# Histórico das versões da heurística de release corretiva

Preencher após rodar `python -m validacao.avaliacao_heuristica` (uma linha por versão testada). Meta do enunciado: F1 ≥ 0,70; se nenhuma versão chegar lá, refinar em `metricas/heuristica.py` (acrescentar v4, v5... em `HEURISTICAS`), reavaliar e registrar **cada** versão aqui e no artigo.

| Versão | Regra (resumo) | Precisão | Recall | F1 | Observação |
|---|---|---|---|---|---|
| v1 | bump de patch **ou** commit com revert/hotfix/fix | | | | baseline do enunciado |
| v2 | bump de patch **e** commit de correção | | | | |
| v3 | patch pequeno/correção, ou maioria de commits de correção | | | | |

Versão adotada no dataset final: `____` (F1 = `____`).
