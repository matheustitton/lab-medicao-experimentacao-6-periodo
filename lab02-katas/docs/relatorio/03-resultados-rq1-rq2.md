<!-- Parte 3 de 6 do relatorio final. Dono: Matheus (frente de testes estatisticos RQ1/RQ2).
     Numeros extraidos de docs/resultados/rq1-rq2.md e data/resultados_rq1_rq2.csv,
     gerados por analise/rq1_rq2.py. Nenhum valor foi recalculado a mao. -->

## 3. Resultados - RQ1 (tempo) e RQ2 (defeitos)

### 3.1 RQ1 - tempo de resolucao

**H0:** mediana(tempo_IA) = mediana(tempo_MANUAL) | **H1:** IA < MANUAL (unicaudal, alfa = 0,05)

#### Descritiva

| tratamento | n | mediana (s) | Q1 | Q3 | IQR | min | max |
|---|---|---|---|---|---|---|---|
| `IA` | 9 | **47** | 6 | 91 | 85 | 5 | 143 |
| `MANUAL` | 9 | **541** | 441 | 643 | 202 | 374 | 679 |

**Nenhum trial foi censurado** - os 18 chegaram ao verde dentro do time-box de 2100 s, nos dois
tratamentos. A mediana com IA e **91% menor** que a manual.

O dado mais forte da RQ1 nao e a mediana, e a **separacao completa das distribuicoes**: o trial
com IA mais lento (143 s) foi mais rapido que o trial manual mais rapido (374 s). Nao ha um unico
par de trials em que o manual tenha vencido - o que, com n = 9 por grupo, e o cenario extremo do
teste de postos.

![RQ1 - tempo por tratamento](figuras/fig01-rq1-tempo-por-tratamento.png)

#### Medianas por kata - os blocos do Wilcoxon

| kata | `IA` (s) | `MANUAL` (s) | diferenca (IA - MANUAL) | forma par? |
|---|---|---|---|---|
| kata-01-faixas | 50 | - | - | **nao** |
| kata-02-espiral | 116 | 510 | -394 | sim |
| kata-03-duracao | 26 | 664 | -638 | sim |
| kata-04-romanos | 91 | 661 | -570 | sim |
| kata-05-rainha | 22 | 541 | -519 | sim |
| kata-06-delimitadores | - | 440 | - | **nao** |

![RQ1 - mediana por kata](figuras/fig02-rq1-mediana-por-kata.png)

#### Teste principal - Wilcoxon pareado por kata

| n de pares | W | p-valor | rank-biserial pareado | decisao |
|---|---|---|---|---|
| 4 | 0,0 | 0,0625 | -1,000 | nao rejeita H0 |

**Esta linha precisa ser lida com cuidado, porque ela nao significa o que parece.** O plano previa
6 pares - um por kata. Como a kata-01 so recebeu `IA` e a kata-06 so recebeu `MANUAL` (secao 2.4),
sobraram 4 pares. Com 4 pares, o menor p-valor que o teste exato unicaudal consegue produzir e
**exatamente 0,0625**, que e o valor observado: as quatro diferencas sao negativas, ou seja, o
resultado e o **maximo efeito que o teste consegue representar** neste N.

Em outras palavras: **com 4 pares o Wilcoxon nao podia rejeitar H0 nem em principio**, por maior
que fosse a diferenca. Reportar "nao rejeita H0" aqui sem essa ressalva seria descrever como
ausencia de efeito o que e, na verdade, ausencia de poder. O rank-biserial de -1,000 confirma que
a direcao e consistente em **todos** os blocos.

#### Teste secundario - Mann-Whitney U

| n | U | p-valor | Cliff's delta | decisao |
|---|---|---|---|---|
| 18 (9 x 9) | 0,0 | **0,0002** | -1,000 (grande) | **rejeita H0** |

O Mann-Whitney ja estava previsto no plano de analise como teste secundario, justamente porque o
n do Wilcoxon seria pequeno - nao e um teste escolhido depois de ver os dados. Com os 18 trials
individuais, U = 0 significa que **nenhum** trial manual foi mais rapido que qualquer trial com
IA, e Cliff's delta = -1,00 e o tamanho de efeito maximo da escala.

#### Analise de sensibilidade

| escopo | n | U | p-valor | Cliff's delta | decisao |
|---|---|---|---|---|---|
| completo | 18 | 0,0 | 0,0002 | -1,000 | rejeita H0 |
| sem os trials de P1 (ameaca #5) | 12 | 0,0 | 0,0025 | -1,000 | rejeita H0 |
| sem os trials de cronometragem suspeita (ameaca #12) | 15 | 0,0 | 0,0002 | -1,000 | rejeita H0 |

A conclusao **nao muda** em nenhum dos dois recortes. Retirar P1 - o integrante que escreveu as
katas e as suites, e que portanto conhecia os casos de borda com antecedencia - mantem a separacao
completa entre os tratamentos. Retirar os tres trials `IA` cuja cronometragem e curta demais para
ser resolucao (5 s, 6 s e 6 s; ver `docs/resultados/00-consolidacao.md`, secao 5) tambem mantem,
inclusive com o mesmo p-valor: os seis trials `IA` restantes, com tempos de 38 s a 143 s,
continuam integralmente abaixo do minimo manual.

No Wilcoxon pareado, os tres escopos dao o mesmo resultado (W = 0, p = 0,0625, rank-biserial
-1,000), pela mesma limitacao de n descrita acima.

#### Metrica exploratoria - numero de prompts

Nos nove trials `IA`, a mediana foi de **1 prompt** (IQR 0; minimo 1, maximo 2). Ou seja: na
maioria dos trials, **uma unica interacao com o assistente ja produziu codigo que passou nos 12
testes**. E metrica exploratoria e nao sustenta conclusao, mas contextualiza o tamanho do efeito
da RQ1 e alimenta a discussao sobre memorizacao (ameaca #1).

### 3.2 RQ2 - qualidade funcional

**H0:** mediana(sucesso_IA) = mediana(sucesso_MANUAL) | **H1:** IA > MANUAL (unicaudal, alfa = 0,05)

| tratamento | n | mediana | IQR | min | max |
|---|---|---|---|---|---|
| `IA` | 9 | 1,00 | 0,00 | 1,00 | 1,00 |
| `MANUAL` | 9 | 1,00 | 0,00 | 1,00 | 1,00 |

**Os 18 trials terminaram com 12 de 12 testes passando - taxa de sucesso de 100% - e nenhum foi
censurado.**

| teste | resultado |
|---|---|
| Wilcoxon pareado por kata | **nao aplicavel** - diferenca zero em todos os pares |
| Mann-Whitney U | **nao aplicavel** - variancia zero nos dois grupos |

A variavel dependente e **constante**. Nenhum teste estatistico detecta diferenca numa variavel
sem variancia: nao existe p-valor a ser calculado, e o script reporta "nao aplicavel" em vez de
produzir um numero sem significado. Formalmente, H0 nao e rejeitada.

O que isso quer dizer, na pratica: **nao se pode concluir nada sobre defeitos a partir deste
experimento.** O resultado e um **efeito teto** - a variavel saturou no valor maximo para todo
mundo - e a explicacao mais provavel esta no desenho, nao no tratamento:

1. as katas sao curtas (solucoes de 21 a 89 LOC) e com especificacao completa;
2. a suite de aceitacao fica visivel para o participante durante o trial, o que transforma a
   tarefa num ciclo de feedback imediato;
3. o time-box de 35 minutos foi folgado - a mediana manual foi de 541 s, menos de um terco do
   limite.

Com esses tres fatores juntos, qualquer participante competente chega a 100% nos dois tratamentos,
e a RQ2 perde a capacidade de discriminar. Isso vai para a discussao como limitacao de desenho e
para trabalhos futuros.

![RQ2 - taxa de sucesso](figuras/fig03-rq2-taxa-sucesso.png)

### 3.3 Sintese das RQ1 e RQ2

| RQ | Teste | n | Estatistica | p-valor | Tamanho de efeito | Decisao (alfa = 0,05) |
|---|---|---|---|---|---|---|
| RQ1 | Wilcoxon pareado por kata | 4 | W = 0,0 | 0,0625 | rank-biserial = -1,000 | nao rejeita H0 (sem poder) |
| RQ1 | Mann-Whitney U | 18 | U = 0,0 | 0,0002 | Cliff's delta = -1,000 | **rejeita H0** |
| RQ1 | Mann-Whitney U (sem P1) | 12 | U = 0,0 | 0,0025 | Cliff's delta = -1,000 | **rejeita H0** |
| RQ1 | Mann-Whitney U (sem cronometro suspeito) | 15 | U = 0,0 | 0,0002 | Cliff's delta = -1,000 | **rejeita H0** |
| RQ2 | Wilcoxon pareado por kata | 4 | - | nao aplicavel | - | efeito teto |
| RQ2 | Mann-Whitney U | 18 | - | nao aplicavel | - | efeito teto |

**Resposta da RQ1:** ha evidencia forte de que o uso do assistente reduziu o tempo de resolucao
neste contexto - mediana de 47 s contra 541 s, separacao completa entre as distribuicoes,
p = 0,0002 e o maior tamanho de efeito possivel, resultado estavel nas duas analises de
sensibilidade.

**Resposta da RQ2:** o experimento **nao consegue responder**. Com todos os trials em 100% de
sucesso, nao ha variancia para testar, e o resultado diz respeito ao desenho das katas, nao ao
efeito do assistente.
