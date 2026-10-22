# Resultados — RQ01 a RQ04 e classificação DORA de referência

> Texto da seção 3 do artigo. Números de `data/saida/analise/` (gerados por `python -m analise.rq01_04`), 270 repositórios, CFR (b) com a heurística v5. Em todas as RQs: mediana e IQR (Q1–Q3).

## 3.1 Visão geral

| RQ | Métrica | n | Mediana | Q1–Q3 |
|---|---|---|---|---|
| RQ01 | Frequência de deploy (releases/semana) | 270 | 0,38 | 0,21–0,88 |
| RQ02 (a) | Lead time por release (horas) | 270 | 235,6 (9,8 dias) | 60,2–890,2 |
| RQ02 (b) | Lead time por commit (horas) | 270 | 212,8 (8,9 dias) | 55,2–706,7 |
| RQ03 (a) | CFR de CI | 270 | 5,3% | 1,7%–12,2% |
| RQ03 (b) | CFR de entrega (v5) | 270 | 40,0% | 14,6%–66,7% |
| RQ04 | Tempo de recuperação (horas) | 248 | 3,2 | 0,9–15,4 |

![Distribuições das métricas](../../data/saida/analise/rq01_04_distribuicoes.png)

## 3.2 RQ01: frequência de deploy

A mediana é de 0,38 releases por semana (cerca de uma release a cada 18 dias), com IQR de 0,21 a 0,88. A distribuição é assimétrica: o máximo é de 18,1 por semana e só 22% dos repositórios publicam pelo menos uma release por semana. Pelos cortes da disciplina, 3 repositórios (1,1%) são Elite, 56 (20,7%) High, 138 (51,1%) Medium e 73 (27,0%) Low.

## 3.3 RQ02: lead time

A mediana por release (a) é de 9,8 dias e a por commit (b) é de 8,9 dias. As duas variantes divergem, mas menos do que esperávamos: (a) é maior que (b) em 63% dos repositórios, e a razão mediana entre elas é de 1,28 (Wilcoxon pareado, p = 1,7 × 10⁻⁴). Entre repositórios, as duas se correlacionam fortemente (Spearman ρ = 0,77). Repositórios que publicam com mais frequência esperam menos: ρ = −0,59 entre frequência e lead time (a) e −0,50 com o (b), em parte por efeito mecânico (com releases mais próximas, os commits têm menos tempo para esperar). Pela variante (a), 50 repositórios (18,5%) são Elite, 65 (24,1%) High, 75 (27,8%) Medium e 80 (29,6%) Low; pela (b), 40 (14,8%), 84 (31,1%), 79 (29,3%) e 67 (24,8%).

**Por que as variantes divergem.** A variante (a) olha só o commit mais antigo de cada release, então um único commit "esquecido" a infla. A variante (b) dá um valor a cada commit, e as releases com muitos commits dominam a mediana. Os dois efeitos se compensam em parte, o que explica a razão de apenas 1,28.

**O que ficou de fora do lead time.** Das 13.664 releases publicadas, 58 são a primeira da história do repositório, 12 tiveram o `compare` indisponível e 1.659 (12%) não trouxeram commits novos. Em 22 repositórios há commits com data posterior à release (efeito de *rebase* ou *squash*), mantidos nos cálculos.

## 3.4 RQ03: taxa de falha

A variante (a), de CI, tem mediana de 5,3% (1,7% a 12,2%): 81,5% dos repositórios são Elite nessa variante (CFR ≤ 15%). A variante (b), de entrega, tem mediana de 40,0% (14,6% a 66,7%) e só 25,2% de Elite, contra 43,0% de Low (CFR > 45%). A (b) é maior que a (a) em 78% dos repositórios, e as duas se correlacionam pouco (ρ = 0,24).

As duas variantes medem coisas diferentes: (a) mede falha de pipeline, e uma falha de CI não chega ao usuário; (b) mede releases seguidas de uma correção em até 7 dias, e depende da heurística de release corretiva (F1 = 0,70, precisão de 0,60). Como a heurística marca mais releases como corretivas do que o consenso humano (63% contra 45% na amostra-ouro), o CFR (b) é um limite superior. As releases dos últimos 7 dias da janela (310 no total) ficaram fora do denominador.

## 3.5 RQ04: tempo de recuperação

A mediana por repositório é de 3,2 horas (0,9 a 15,4), calculada sobre 248 repositórios: 22 não tiveram nenhum episódio de falha seguido de sucesso e ficam sem valor (não são tratados como zero). Foram 20.956 episódios, dos quais 140 (0,7%) foram censurados por não se recuperarem até o fim da janela; eles aparecem em 71 repositórios, mas em só 19 (7%) a censura atinge 10% ou mais dos episódios (máximo de 50%). A mediana que inclui os censurados como limite inferior é igual à mediana dos concluídos (3,2 horas). Pelos cortes da disciplina, 66 repositórios (26,6%) são Elite, 140 (56,5%) High, 33 (13,3%) Medium e 9 (3,6%) Low.

## 3.6 Classificação DORA de referência (combinação C1)

A combinação C1 usa release como unidade de deploy, lead time (a) e CFR (a). A classe geral é a mediana dos pontos das quatro métricas, arredondada para baixo.

| Classe | Repositórios | % |
|---|---|---|
| Elite | 21 | 7,8 |
| High | 108 | 40,0 |
| Medium | 117 | 43,3 |
| Low | 24 | 8,9 |

![Classe DORA por métrica](../../data/saida/analise/rq01_04_classe_dora.png)

As métricas puxam a classificação em direções opostas: a frequência de deploy é a métrica mais baixa (só 22% chegam a High ou Elite) e o CFR (a) é a mais alta (91% em High ou Elite). Por isso a classe geral se concentra em High e Medium.
