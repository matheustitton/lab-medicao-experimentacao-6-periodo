# S03 - Resultados da RQ3 (estrutura do codigo)

Gerado por `analise/rq3.py` a partir de `data/metrics_consolidado.csv`.
Nao editar a mao - o texto interpretativo vai em `docs/relatorio/`.

H0: mediana(metrica_IA) = mediana(metrica_MANUAL) | H1: as medianas **diferem** (bicaudal, alfa = 0,05)

## cc_media - complexidade ciclomatica media por funcao

### Descritiva

| tratamento | n | mediana | Q1 | Q3 | IQR | min | max |
|---|---|---|---|---|---|---|---|
| IA | 9 | 8,00 | 6,00 | 12,00 | 6,00 | 3,00 | 23,00 |
| MANUAL | 9 | 13,00 | 9,00 | 14,00 | 5,00 | 3,00 | 18,00 |

### Medianas por kata (os blocos do Wilcoxon)

| kata | IA | MANUAL | diferenca (IA - MANUAL) | par completo |
|---|---|---|---|---|
| kata-01-faixas | 4,00 | n/a | n/a | **nao** |
| kata-02-espiral | 11,00 | 14,00 | -3,00 | sim |
| kata-03-duracao | 7,50 | 3,00 | 4,50 | sim |
| kata-04-romanos | 23,00 | 16,00 | 7,00 | sim |
| kata-05-rainha | 13,00 | 14,00 | -1,00 | sim |
| kata-06-delimitadores | n/a | 9,00 | n/a | **nao** |

### Testes

| teste | n | estatistica | p-valor | efeito | decisao (alfa = 0,05) |
|---|---|---|---|---|---|
| Wilcoxon pareado por kata | 4 | 3,0 | 0,6250 | rank-biserial pareado = 0,400 (direcao mista) | nao rejeita H0 |
| Mann-Whitney U | 18 | 25,5 | 0,1988 | Cliff's delta = -0,370 (medio) | nao rejeita H0 |

- **Wilcoxon pareado por kata**: n=4: o menor p alcancavel pelo teste exato e 0,1250, acima de alfa=0.05 - o teste nao pode rejeitar H0 neste N. katas sem par excluidas: kata-01-faixas, kata-06-delimitadores

## loc - LOC (controle)

### Descritiva

| tratamento | n | mediana | Q1 | Q3 | IQR | min | max |
|---|---|---|---|---|---|---|---|
| IA | 9 | 33,00 | 27,00 | 42,00 | 15,00 | 21,00 | 89,00 |
| MANUAL | 9 | 36,00 | 35,00 | 41,00 | 6,00 | 29,00 | 61,00 |

### Medianas por kata (os blocos do Wilcoxon)

| kata | IA | MANUAL | diferenca (IA - MANUAL) | par completo |
|---|---|---|---|---|
| kata-01-faixas | 25,00 | n/a | n/a | **nao** |
| kata-02-espiral | 33,00 | 35,00 | -2,00 | sim |
| kata-03-duracao | 33,00 | 41,00 | -8,00 | sim |
| kata-04-romanos | 89,00 | 53,50 | 35,50 | sim |
| kata-05-rainha | 45,50 | 37,00 | 8,50 | sim |
| kata-06-delimitadores | n/a | 31,00 | n/a | **nao** |

### Testes

| teste | n | estatistica | p-valor | efeito | decisao (alfa = 0,05) |
|---|---|---|---|---|---|
| Wilcoxon pareado por kata | 4 | 3,0 | 0,6250 | rank-biserial pareado = 0,400 (direcao mista) | nao rejeita H0 |
| Mann-Whitney U | 18 | 30,5 | 0,4003 | Cliff's delta = -0,247 (pequeno) | nao rejeita H0 |

- **Wilcoxon pareado por kata**: n=4: o menor p alcancavel pelo teste exato e 0,1250, acima de alfa=0.05 - o teste nao pode rejeitar H0 neste N. katas sem par excluidas: kata-01-faixas, kata-06-delimitadores

## pct_duplicado - % de linhas duplicadas (jscpd)

### Descritiva

| tratamento | n | mediana | Q1 | Q3 | IQR | min | max |
|---|---|---|---|---|---|---|---|
| IA | 9 | 0,00 | 0,00 | 0,00 | 0,00 | 0,00 | 2,44 |
| MANUAL | 9 | 0,00 | 0,00 | 0,00 | 0,00 | 0,00 | 0,00 |

| teste | n | estatistica | p-valor | efeito | decisao (alfa = 0,05) |
|---|---|---|---|---|---|
| Wilcoxon pareado por kata | n/a | n/a | n/a | rank-biserial pareado = n/a (indefinido) | nao aplicavel |
| Mann-Whitney U | n/a | n/a | n/a | Cliff's delta = n/a (indefinido) | nao aplicavel |

- **Wilcoxon pareado por kata**: so 1 de 18 trials com duplicacao (p3-kata-04-romanos-ia (2,44%)) - variancia quase nula, teste degenerado
- **Mann-Whitney U**: so 1 de 18 trials com duplicacao (p3-kata-04-romanos-ia (2,44%)) - variancia quase nula, teste degenerado

## cc_soma_por_loc - complexidade normalizada por tamanho

Leitura complementar exigida pelo desenho (secao B, decisao 2): a media por funcao
depende do estilo (laco vs. array method), a soma por LOC nao.

### Descritiva

| tratamento | n | mediana | Q1 | Q3 | IQR | min | max |
|---|---|---|---|---|---|---|---|
| IA | 9 | 0,26 | 0,23 | 0,29 | 0,06 | 0,22 | 0,38 |
| MANUAL | 9 | 0,37 | 0,25 | 0,39 | 0,14 | 0,22 | 0,43 |

### Testes

| teste | n | estatistica | p-valor | efeito | decisao (alfa = 0,05) |
|---|---|---|---|---|---|
| Wilcoxon pareado por kata | 4 | 1,0 | 0,2500 | rank-biserial pareado = -0,800 (direcao mista) | nao rejeita H0 |
| Mann-Whitney U | 18 | 24,0 | 0,1575 | Cliff's delta = -0,407 (medio) | nao rejeita H0 |

- **Wilcoxon pareado por kata**: n=4: o menor p alcancavel pelo teste exato e 0,1250, acima de alfa=0.05 - o teste nao pode rejeitar H0 neste N. katas sem par excluidas: kata-01-faixas, kata-06-delimitadores

## Demais metricas de complexidade (so descritiva)

**cc_max** - complexidade ciclomatica maxima

| tratamento | n | mediana | Q1 | Q3 | IQR | min | max |
|---|---|---|---|---|---|---|---|
| IA | 9 | 8,00 | 6,00 | 12,00 | 6,00 | 4,00 | 23,00 |
| MANUAL | 9 | 13,00 | 9,00 | 14,00 | 5,00 | 4,00 | 18,00 |

**cc_soma** - complexidade ciclomatica somada

| tratamento | n | mediana | Q1 | Q3 | IQR | min | max |
|---|---|---|---|---|---|---|---|
| IA | 9 | 8,00 | 7,00 | 12,00 | 5,00 | 6,00 | 23,00 |
| MANUAL | 9 | 13,00 | 9,00 | 14,00 | 5,00 | 9,00 | 18,00 |

**n_funcoes** - numero de funcoes

| tratamento | n | mediana | Q1 | Q3 | IQR | min | max |
|---|---|---|---|---|---|---|---|
| IA | 9 | 1,00 | 1,00 | 1,00 | 0,00 | 1,00 | 2,00 |
| MANUAL | 9 | 1,00 | 1,00 | 1,00 | 0,00 | 1,00 | 3,00 |

## Analise de sensibilidade - cc_media sem cada integrante

Previsto no plano sem P1 (ameaca #5, contaminacao do autor das katas); repetido
sem P2 e sem P3 para mostrar se algum integrante sozinho carrega o resultado.

**Sem os trials de P1:**

| teste | n | estatistica | p-valor | efeito | decisao (alfa = 0,05) |
|---|---|---|---|---|---|
| Wilcoxon pareado por kata | 4 | 1,0 | 0,5000 | rank-biserial pareado = 0,667 (direcao mista) | nao rejeita H0 |
| Mann-Whitney U | 12 | 14,5 | 0,6279 | Cliff's delta = -0,194 (pequeno) | nao rejeita H0 |

- **Wilcoxon pareado por kata**: n=4: o menor p alcancavel pelo teste exato e 0,1250, acima de alfa=0.05 - o teste nao pode rejeitar H0 neste N. katas sem par excluidas: kata-01-faixas, kata-06-delimitadores

**Sem os trials de P2:**

| teste | n | estatistica | p-valor | efeito | decisao (alfa = 0,05) |
|---|---|---|---|---|---|
| Wilcoxon pareado por kata | 4 | 3,0 | 0,6250 | rank-biserial pareado = 0,400 (direcao mista) | nao rejeita H0 |
| Mann-Whitney U | 12 | 12,5 | 0,4217 | Cliff's delta = -0,306 (pequeno) | nao rejeita H0 |

- **Wilcoxon pareado por kata**: n=4: o menor p alcancavel pelo teste exato e 0,1250, acima de alfa=0.05 - o teste nao pode rejeitar H0 neste N. katas sem par excluidas: kata-01-faixas, kata-06-delimitadores

**Sem os trials de P3:**

| teste | n | estatistica | p-valor | efeito | decisao (alfa = 0,05) |
|---|---|---|---|---|---|
| Wilcoxon pareado por kata | 0 | n/a | n/a | rank-biserial pareado = n/a (indefinido) | nao aplicavel |
| Mann-Whitney U | 12 | 5,5 | 0,0538 | Cliff's delta = -0,694 (grande) | nao rejeita H0 |

- **Wilcoxon pareado por kata**: apenas 0 pares completos; katas sem par: kata-01-faixas, kata-02-espiral, kata-03-duracao, kata-04-romanos, kata-05-rainha, kata-06-delimitadores

## Trials por metrica (dado bruto consolidado)

| trial | tratamento | loc | cc_media | cc_max | cc_soma_por_loc | pct_duplicado |
|---|---|---|---|---|---|---|
| p1-kata-01-faixas-ia | IA | 21 | 4,00 | 6 | 0,3810 | 0,00 |
| p2-kata-01-faixas-ia | IA | 27 | 6,00 | 6 | 0,2222 | 0,00 |
| p3-kata-01-faixas-ia | IA | 25 | 3,00 | 4 | 0,2400 | 0,00 |
| p3-kata-02-espiral-ia | IA | 33 | 11,00 | 11 | 0,3333 | 0,00 |
| p1-kata-03-duracao-ia | IA | 31 | 7,00 | 7 | 0,2258 | 0,00 |
| p2-kata-03-duracao-ia | IA | 35 | 8,00 | 8 | 0,2286 | 0,00 |
| p3-kata-04-romanos-ia | IA | 89 | 23,00 | 23 | 0,2584 | 2,44 |
| p1-kata-05-rainha-ia | IA | 42 | 12,00 | 12 | 0,2857 | 0,00 |
| p2-kata-05-rainha-ia | IA | 49 | 14,00 | 14 | 0,2857 | 0,00 |
| p1-kata-02-espiral-manual | MANUAL | 35 | 13,00 | 13 | 0,3714 | 0,00 |
| p2-kata-02-espiral-manual | MANUAL | 35 | 15,00 | 15 | 0,4286 | 0,00 |
| p3-kata-03-duracao-manual | MANUAL | 41 | 3,00 | 4 | 0,2195 | 0,00 |
| p1-kata-04-romanos-manual | MANUAL | 46 | 18,00 | 18 | 0,3913 | 0,00 |
| p2-kata-04-romanos-manual | MANUAL | 61 | 14,00 | 14 | 0,2295 | 0,00 |
| p3-kata-05-rainha-manual | MANUAL | 37 | 14,00 | 14 | 0,3784 | 0,00 |
| p1-kata-06-delimitadores-manual | MANUAL | 29 | 9,00 | 9 | 0,3103 | 0,00 |
| p2-kata-06-delimitadores-manual | MANUAL | 36 | 9,00 | 9 | 0,2500 | 0,00 |
| p3-kata-06-delimitadores-manual | MANUAL | 31 | 13,00 | 13 | 0,4194 | 0,00 |
