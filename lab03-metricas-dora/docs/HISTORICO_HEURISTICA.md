# Histórico das versões da heurística de release corretiva

Todas as versões foram comparadas com o **consenso** da amostra-ouro (300 releases de 60 repositórios; 134 corretivas e 166 não corretivas) com `python -m validacao.avaliacao_heuristica`. Meta do enunciado: F1 ≥ 0,70. Saída completa em `data/saida/avaliacao_heuristica.csv`.

| Versão | Regra (resumo) | Precisão | Recall | F1 | Observação |
|---|---|---|---|---|---|
| v1 | bump de patch **ou** commit com revert/hotfix/fix | 0,469 | 0,970 | 0,633 | baseline do enunciado; marca 277 de 300 releases como corretivas (a palavra `fix` aparece em quase todo release) |
| v2 | bump de patch **e** commit de correção | 0,643 | 0,687 | 0,664 | conservadora: perde corretivas sem bump de patch |
| v3 | patch pequeno (≤ 5 commits) ou com correção; minor/major só se ≥ 50% dos commits forem de correção | 0,594 | 0,754 | 0,664 | |
| v4 | ignora commits de *merge* e de dependência (`bump`, `deps`, `dependabot`); corretiva se for patch com correção (ou com ≤ 2 commits úteis) **ou** se ≥ 30% dos commits úteis forem de correção | 0,600 | 0,806 | 0,688 | primeiro refinamento a partir da leitura dos erros da v1 |
| v5 | v4 **ou** release com algum commit de correção publicada em até 2 dias depois da release anterior | 0,600 | 0,851 | **0,704** | atinge a meta por pouco |

## Como a v4 e a v5 foram escolhidas

1. Lemos os falsos positivos e falsos negativos da v1. Os falsos positivos vinham de releases grandes em que um único commit `fix(deps): ...` bastava para marcar a release inteira. Os falsos negativos eram poucos (4 de 134).
2. A v4 trata esse ruído (merges e dependências) e passa a exigir uma **fração** de commits de correção nas releases que não são patch.
3. A v5 acrescenta o intervalo curto desde a release anterior: no consenso, releases publicadas em até 1 dia depois da anterior são corretivas em 53% dos casos (31 de 58) e, entre 1 e 14 dias, em 51% (58 de 113), contra 36% (41 de 114) quando o intervalo passa de 14 dias.
4. Os limiares (2 commits, 30%, 2 dias) foram escolhidos numa pequena grade (`validacao/validacao_cruzada.py`) **nos mesmos 300 rótulos** em que a F1 é medida. Para estimar o quanto disso é ajuste, `python -m validacao.validacao_cruzada` repete a escolha dos limiares só nos repositórios de treino e mede nos de teste (5 dobras, repositórios nunca divididos entre treino e teste).

| Medida da v5 | Precisão | Recall | F1 |
|---|---|---|---|
| Nos 300 rótulos (limiares ajustados neles) | 0,600 | 0,851 | 0,704 |
| Validação cruzada por repositório (5 dobras) | 0,591 | 0,851 | **0,697** |

A F1 fora da amostra (0,697) fica um pouco abaixo da meta. A margem é pequena demais para afirmar que a meta foi atingida de forma robusta, e isso entra como ameaça à validade da RQ03 (b).

## Limites que a heurística não resolve

- **Precisão baixa (0,60).** Seis em cada dez releases marcadas realmente são corretivas. Por isso o CFR (b) e o *rework rate* são limites superiores: a heurística marca 190 releases como corretivas onde o consenso marca 134 (63% contra 45%).
- **Falta o texto das release notes.** Os avaliadores leram as notas e os commits; a heurística só vê as mensagens dos commits e os números de versão. Testamos dezenas de combinações de limiares e árvores de decisão pequenas e nenhuma passou de ≈ 0,70 em validação cruzada, o que sugere que esse é o teto com esses dois sinais.

## Versão adotada no dataset final

`v5` (F1 = 0,704 na amostra-ouro; 0,697 em validação cruzada). O `config.yaml` usa `heuristica: v5`. O CFR (b) das versões v1 a v4 continua disponível em `data/saida/dataset_sensibilidade.csv` (colunas `cfr_b_v1` a `cfr_b_v5`) para a análise de sensibilidade da RQ07.
