# Fonte dos dados reais

- **Repositório:** [`formbricks/formbricks`](https://github.com/formbricks/formbricks)
- **Bot de revisão:** CodeRabbit (`coderabbitai[bot]`)
- **Coleta:** 05/11/2026, com `python -m lab04.coleta` (API de busca do GitHub, sem token)
- **Arquivo:** `prs_reais.csv`, com 30 PRs por grupo, congelado no repositório
- **Medida:** horas entre `created_at` e `merged_at` de cada PR

## Como as janelas foram escolhidas

A cobertura do bot foi medida **antes** de olhar os tempos de merge, para que a janela não fosse escolhida pelo resultado.

| PRs criados em | PRs mergeados | Com comentário do bot | Cobertura |
|---|---|---:|---:|
| 06/2024 | 87 | 0 | 0% |
| 07/2024 | 63 | 0 | 0% |
| 01 a 18/08/2024 | 56 | 0 | 0% |
| 19 a 31/08/2024 | 33 | 2 | 6% |
| 09/2024 | 71 | 33 | 46% |
| 10/2024 | 140 | 139 | 99% |
| 11/2024 | 85 | 85 | 100% |
| 12/2024 | 74 | 73 | 99% |
| 01/2025 | 75 | 72 | 96% |
| 02/2025 | 79 | 73 | 92% |

Os totais excluem PRs de `dependabot` e `renovate`.

- **`sem_bot`:** os 30 PRs mergeados mais recentes criados até 18/08/2024, sem comentário do bot.
- **`com_bot`:** os 30 primeiros PRs mergeados criados a partir de 01/11/2024, com comentário do bot.

**Por que excluir a transição (19/08 a 31/10/2024):**

- Em agosto e setembro, o bot comentava só em parte dos PRs. Um PR que fica mais tempo aberto tem mais chance de receber comentário, então comparar nesse período favorece a conclusão de que o bot atrasa o merge. No piloto, que usava essa fase, a mediana com bot foi 72,3 h; na janela limpa, foi 11,2 h.
- Em outubro, o volume de PRs dobrou. O mês coincide com o Hacktoberfest, então os PRs podem ser atípicos.

## Consultas

```
repo:formbricks/formbricks is:pr is:merged created:<=2024-08-18 -commenter:coderabbitai[bot]   (mais recentes primeiro)
repo:formbricks/formbricks is:pr is:merged created:>=2024-11-01 commenter:coderabbitai[bot]    (mais antigos primeiro)
```

PRs de autores do tipo `Bot` ou com login terminado em `[bot]` são removidos antes de contar os 30.

## Limitações

- **Antes e depois, sem grupo de controle:** o estudo é observacional. Outras mudanças entre agosto e novembro de 2024 (equipe, processo, tipo de PR) ficam misturadas ao efeito do bot.
- **Só PRs mergeados:** PRs fechados sem merge ficam de fora.
- **Janelas curtas:** cada grupo cobre cerca de 10 dias, o que evita mudanças de longo prazo, mas pode refletir um momento específico do projeto.
- **Automações não identificadas:** contas de automação registradas como usuário comum não são detectadas pelo filtro de bots.
