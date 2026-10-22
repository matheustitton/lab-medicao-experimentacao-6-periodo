# Dicionário de dados: `data/saida/dataset_sensibilidade.csv`

Uma linha por repositório (270). Gerado por `python -m analise.sensibilidade_dataset` a partir de `data/estado.sqlite`. Mesma janela e mesmas regras de `dataset_dora.csv`.

| Coluna | Tipo | Unidade | Origem / fórmula |
|---|---|---|---|
| `repo` | texto | | `owner/nome` |
| `n_prereleases` | inteiro | releases | pré-releases publicadas na janela |
| `freq_release` | decimal | releases/semana | só releases (`prerelease = false`) ÷ semanas da janela |
| `freq_release_pre` | decimal | releases/semana | releases + pré-releases ÷ semanas da janela |
| `lead_a_h` | decimal | horas | lead time (a): mediana por release |
| `lead_b_h` | decimal | horas | lead time (b): mediana por commit |
| `cfr_a` | decimal | proporção | falhas ÷ (falhas + sucessos) dos workflow runs |
| `recuperacao_h` | decimal | horas | mediana dos episódios concluídos (vazio se não houve episódio) |
| `cfr_b_v1` ... `cfr_b_v5` | decimal | proporção | CFR (b) com cada versão da heurística, só releases |
| `cfr_b_pre_v1` ... `cfr_b_pre_v5` | decimal | proporção | CFR (b) com as pré-releases tratadas como releases na sequência |
| `rework_v1` ... `rework_v5` | decimal | proporção | RQ08: releases corretivas ÷ releases publicadas (sem pré-releases) |
| `n_corretivas_v1` ... `n_corretivas_v5` | inteiro | releases | numerador do `rework_vN` |
| `classe_C1` | texto | Elite/High/Medium/Low | release; lead (a); CFR (a) |
| `classe_C2` | texto | Elite/High/Medium/Low | release + pré-release; lead (b); CFR (b) com a heurística do `config.yaml` |
| `classe_C3` | texto | Elite/High/Medium/Low | release; lead (b); CFR (a) |
| `classe_C4` | texto | Elite/High/Medium/Low | release; lead (a); CFR (b) com a heurística do `config.yaml` |
| `classe_C4_v1` ... `classe_C4_v5` | texto | Elite/High/Medium/Low | C4 com cada versão da heurística |

**Limitações.** (1) As tags não foram coletadas, então não há combinação com tag como unidade de deploy. (2) As pré-releases não têm commits coletados: contam na frequência e na sequência do CFR (b), mas não no lead time. (3) Em todas as combinações, o tempo de recuperação e a regra de classificação (mediana dos pontos, arredondada para baixo) são os mesmos.
