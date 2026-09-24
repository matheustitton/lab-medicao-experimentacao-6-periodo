# S03 - Resultados da RQ1 (tempo) e da RQ2 (defeitos)

Gerado por `analise/rq1_rq2.py` a partir de `data/trials_consolidado.csv`.
Nao editar a mao - o texto interpretativo vai em `docs/relatorio/`.

## RQ1 - Tempo de resolucao (time-to-green, em segundos)

H0: mediana(tempo_IA) = mediana(tempo_MANUAL) | H1: **IA < MANUAL** (unicaudal, alfa = 0,05)

### Descritiva

| tratamento | n | mediana | Q1 | Q3 | IQR | min | max |
|---|---|---|---|---|---|---|---|
| IA | 9 | 47,00 | 6,00 | 91,00 | 85,00 | 5,00 | 143,00 |
| MANUAL | 9 | 541,00 | 441,00 | 643,00 | 202,00 | 374,00 | 679,00 |

Trials censurados (atingiram o time-box de 2100s): IA = 0, MANUAL = 0.

### Medianas por kata (os blocos do Wilcoxon)

| kata | IA | MANUAL | diferenca (IA - MANUAL) | par completo |
|---|---|---|---|---|
| kata-01-faixas | 50,00 | n/a | n/a | **nao** |
| kata-02-espiral | 116,00 | 510,00 | -394,00 | sim |
| kata-03-duracao | 26,00 | 664,00 | -638,00 | sim |
| kata-04-romanos | 91,00 | 661,00 | -570,00 | sim |
| kata-05-rainha | 22,00 | 541,00 | -519,00 | sim |
| kata-06-delimitadores | n/a | 440,00 | n/a | **nao** |

**4 de 6 pares completos.**

### Testes

| teste | n | estatistica | p-valor | efeito | decisao (alfa = 0,05) |
|---|---|---|---|---|---|
| Wilcoxon pareado por kata | 4 | 0,0 | 0,0625 | rank-biserial pareado = -1,000 (direcao consistente) | nao rejeita H0 |
| Mann-Whitney U | 18 | 0,0 | 0,0002 | Cliff's delta = -1,000 (grande) | rejeita H0 |

- **Wilcoxon pareado por kata**: n=4: o menor p alcancavel pelo teste exato e 0,0625, acima de alfa=0.05 - o teste nao pode rejeitar H0 neste N. katas sem par excluidas: kata-01-faixas, kata-06-delimitadores

### Analise de sensibilidade

Previstas no plano (ameaca #5, contaminacao do autor das katas) e acrescentada a
exclusao dos trials com cronometragem implausivel (ver `00-consolidacao.md`).

**Sem os trials de P1:**

| teste | n | estatistica | p-valor | efeito | decisao (alfa = 0,05) |
|---|---|---|---|---|---|
| Wilcoxon pareado por kata | 4 | 0,0 | 0,0625 | rank-biserial pareado = -1,000 (direcao consistente) | nao rejeita H0 |
| Mann-Whitney U | 12 | 0,0 | 0,0025 | Cliff's delta = -1,000 (grande) | rejeita H0 |

- **Wilcoxon pareado por kata**: n=4: o menor p alcancavel pelo teste exato e 0,0625, acima de alfa=0.05 - o teste nao pode rejeitar H0 neste N. katas sem par excluidas: kata-01-faixas, kata-06-delimitadores

**Sem os trials com cronometro suspeito:**

| teste | n | estatistica | p-valor | efeito | decisao (alfa = 0,05) |
|---|---|---|---|---|---|
| Wilcoxon pareado por kata | 4 | 0,0 | 0,0625 | rank-biserial pareado = -1,000 (direcao consistente) | nao rejeita H0 |
| Mann-Whitney U | 15 | 0,0 | 0,0002 | Cliff's delta = -1,000 (grande) | rejeita H0 |

- **Wilcoxon pareado por kata**: n=4: o menor p alcancavel pelo teste exato e 0,0625, acima de alfa=0.05 - o teste nao pode rejeitar H0 neste N. katas sem par excluidas: kata-01-faixas, kata-06-delimitadores

## RQ2 - Qualidade funcional (taxa de sucesso dos testes de aceitacao)

H0: mediana(sucesso_IA) = mediana(sucesso_MANUAL) | H1: **IA > MANUAL** (unicaudal, alfa = 0,05)

### Descritiva

| tratamento | n | mediana | Q1 | Q3 | IQR | min | max |
|---|---|---|---|---|---|---|---|
| IA | 9 | 1,00 | 1,00 | 1,00 | 0,00 | 1,00 | 1,00 |
| MANUAL | 9 | 1,00 | 1,00 | 1,00 | 0,00 | 1,00 | 1,00 |

### Testes

| teste | n | estatistica | p-valor | efeito | decisao (alfa = 0,05) |
|---|---|---|---|---|---|
| Wilcoxon pareado por kata | 4 | n/a | n/a | rank-biserial pareado = 0,000 (nulo) | nao aplicavel |
| Mann-Whitney U | 18 | n/a | n/a | Cliff's delta = 0,000 (nulo) | nao aplicavel |

- **Wilcoxon pareado por kata**: diferenca zero em todos os pares - sem variancia para testar
- **Mann-Whitney U**: variancia zero nos dois grupos - nao ha o que ordenar

## Metrica exploratoria - numero de prompts (so tratamento IA)

| tratamento | n | mediana | Q1 | Q3 | IQR | min | max |
|---|---|---|---|---|---|---|---|
| IA | 9 | 1,00 | 1,00 | 1,00 | 0,00 | 1,00 | 2,00 |

