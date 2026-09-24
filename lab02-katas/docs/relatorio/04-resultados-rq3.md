<!-- Parte 4 de 6 do relatorio final. Dono: Pedro (frente RQ3 - metricas estaticas).
     Numeros extraidos de docs/resultados/rq3.md e data/resultados_rq3.csv,
     gerados por analise/rq3.py. Nenhum valor foi recalculado a mao. -->

## 4. Resultados - RQ3 (estrutura do codigo)

**H0:** mediana(metrica_IA) = mediana(metrica_MANUAL) | **H1:** as medianas **diferem**
(bicaudal, alfa = 0,05)

A RQ3 e bicaudal por decisao do desenho, tomada antes da coleta: havia argumento plausivel tanto
para a IA produzir codigo mais verboso e duplicado quanto mais enxuto. Metricas: complexidade
ciclomatica media por funcao (ESLint `complexity`), percentual de linhas duplicadas (jscpd) e LOC
como controle obrigatorio. O `data/metrics.csv` bruto tem 42 linhas porque o `run_metrics.ps1` foi
rodado mais de uma vez; o `rq3.py` mantem a ultima medicao de cada trial e confere que os 18
trials do `trials_consolidado.csv` estao presentes.

### 4.1 Complexidade ciclomatica

| tratamento | n | mediana | Q1 | Q3 | IQR | min | max |
|---|---|---|---|---|---|---|---|
| `IA` | 9 | **8** | 6 | 12 | 6 | 3 | 23 |
| `MANUAL` | 9 | **13** | 9 | 14 | 5 | 3 | 18 |

![RQ3 - complexidade por tratamento](figuras/fig04-rq3-complexidade.png)

Na mediana dos trials, o codigo com IA foi menos complexo (8 contra 13). Mas as distribuicoes se
sobrepoem quase inteiras - os dois tratamentos vao de 3 a pelo menos 18 - e o trial mais complexo
do experimento inteiro e de IA (`p3-kata-04-romanos-ia`, CC 23).

#### Medianas por kata - os blocos do Wilcoxon

| kata | `IA` | `MANUAL` | diferenca (IA - MANUAL) | forma par? |
|---|---|---|---|---|
| kata-01-faixas | 4 | - | - | **nao** |
| kata-02-espiral | 11 | 14 | -3 | sim |
| kata-03-duracao | 7,5 | 3 | +4,5 | sim |
| kata-04-romanos | 23 | 16 | +7 | sim |
| kata-05-rainha | 13 | 14 | -1 | sim |
| kata-06-delimitadores | - | 9 | - | **nao** |

![RQ3 - complexidade por kata](figuras/fig06-rq3-complexidade-por-kata.png)

**Esta tabela e o ponto central da RQ3.** Quando a comparacao e feita dentro da mesma kata -
que e o que o desenho define como comparacao justa, porque isola a dificuldade da kata - a
direcao **se divide**: a IA foi menos complexa em K2 e K5, e mais complexa em K3 e K4, com as
duas maiores diferencas absolutas justamente no sentido contrario ao da mediana geral.

| teste | n | estatistica | p-valor | tamanho de efeito | decisao |
|---|---|---|---|---|---|
| Wilcoxon pareado por kata | 4 | W = 3,0 | 0,6250 | rank-biserial = +0,400 (direcao mista) | nao rejeita H0 |
| Mann-Whitney U | 18 (9 x 9) | U = 25,5 | 0,1988 | Cliff's delta = -0,370 (medio) | nao rejeita H0 |

Os dois testes nao rejeitam H0, e **os dois tamanhos de efeito apontam em sentidos opostos**: o
Mann-Whitney, que ignora a kata, sugere IA menos complexa (delta -0,37); o Wilcoxon, que pareia
por kata, sugere o contrario (rank-biserial +0,40). A mediana geral mais baixa da IA e, pelo
menos em parte, efeito de **quais** katas cada tratamento recebeu, nao do tratamento. Diferente
da RQ1, aqui nao e so falta de poder: nem a direcao observada e estavel.

Sobre o poder: como na RQ1, sobram 4 pares, e no teste bicaudal o menor p-valor alcancavel com 4
pares e 0,125 - o Wilcoxon nao rejeitaria H0 nem com as quatro diferencas no mesmo sentido.

#### Complexidade normalizada por tamanho

O desenho (secao B, decisao 2) registra que a media por funcao depende de estilo - callbacks de
`.filter()`/`.map()` contam como funcoes e baixam a media. Por isso a comparacao tambem e feita
com a complexidade somada dividida por LOC:

| tratamento | mediana | Q1 | Q3 |
|---|---|---|---|
| `IA` | 0,26 | 0,23 | 0,29 |
| `MANUAL` | 0,37 | 0,25 | 0,39 |

| teste | n | p-valor | tamanho de efeito | decisao |
|---|---|---|---|---|
| Wilcoxon pareado por kata | 4 | 0,2500 | rank-biserial = -0,800 | nao rejeita H0 |
| Mann-Whitney U | 18 | 0,1575 | Cliff's delta = -0,407 (medio) | nao rejeita H0 |

Normalizada por tamanho, a direcao fica mais consistente: IA menos complexa por linha em 3 das
4 katas pareadas (a excecao, K3, e uma diferenca de 0,01). Ainda sem significancia. Na pratica,
neste experimento a ressalva do desenho pesou pouco: a mediana de funcoes por trial e 1 nos dois
tratamentos, entao media, maximo e soma quase coincidem.

### 4.2 LOC (controle)

| tratamento | n | mediana | Q1 | Q3 | IQR | min | max |
|---|---|---|---|---|---|---|---|
| `IA` | 9 | **33** | 27 | 42 | 15 | 21 | 89 |
| `MANUAL` | 9 | **36** | 35 | 41 | 6 | 29 | 61 |

| teste | n | estatistica | p-valor | tamanho de efeito | decisao |
|---|---|---|---|---|---|
| Wilcoxon pareado por kata | 4 | W = 3,0 | 0,6250 | rank-biserial = +0,400 | nao rejeita H0 |
| Mann-Whitney U | 18 | U = 30,5 | 0,4003 | Cliff's delta = -0,247 (pequeno) | nao rejeita H0 |

![RQ3 - LOC por tratamento](figuras/fig05-rq3-loc.png)

LOC nao mostra diferenca relevante entre tratamentos: medianas de 33 e 36 linhas, efeito pequeno.
O risco que o enunciado aponta - codigo de IA sistematicamente mais verboso - **nao apareceu** na
tendencia central. O que aparece e mais **dispersao** na IA (IQR 15 contra 6), puxada por um
unico trial.

### 4.3 Duplicacao

| tratamento | mediana | trials com duplicacao |
|---|---|---|
| `IA` | 0 % | 1 de 9 |
| `MANUAL` | 0 % | 0 de 9 |

So 1 dos 18 trials tem duplicacao detectada pelo jscpd: `p3-kata-04-romanos-ia`, com 2,44% (3
linhas). Os testes foram registrados como **nao aplicaveis**: com 17 zeros, nao ha variancia
para ordenar, e trocar de teste depois de ver os dados violaria o plano. Katas curtas (21 a 89
LOC) com uma funcao so deixam pouco espaco para duplicacao com `minTokens: 25`.

### 4.4 O trial `p3-kata-04-romanos-ia`

Esse trial merece leitura separada porque concentra, sozinho, tres extremos da RQ3: o maior LOC
do experimento (89, contra 49 do segundo maior trial com IA e 61 do maior manual), a maior
complexidade (CC 23) e a unica duplicacao. E tambem ele que produz a maior diferenca por kata
em complexidade (K4, +7) e em LOC (+35,5). **Antes de qualquer generalizacao, o codigo desse
trial precisa ser inspecionado manualmente** - um unico trial nao sustenta afirmacao sobre "o
codigo da IA", e o N desta RQ nao absorve um outlier desse tamanho.

### 4.5 Analise de sensibilidade (complexidade media)

| escopo | Wilcoxon por kata (n, p, rank-biserial) | Mann-Whitney (n, p, Cliff's delta) |
|---|---|---|
| completo | 4, 0,6250, +0,400 | 18, 0,1988, -0,370 |
| sem P1 (ameaca #5) | 4, 0,5000, +0,667 | 12, 0,6279, -0,194 |
| sem P2 | 4, 0,6250, +0,400 | 12, 0,4217, -0,306 |
| sem P3 | nao aplicavel - 0 pares | 12, 0,0538, -0,694 (grande) |

Nenhum recorte rejeita H0. O recorte "sem P3" nao tem Wilcoxon porque P1 e P2 receberam a mesma
alocacao (IA em K1, K3, K5): sem P3, nenhuma kata tem os dois tratamentos. Esse mesmo recorte e o
unico em que o Mann-Whitney chega perto de alfa (p = 0,054) - mas ele compara katas diferentes
entre tratamentos, entao o efeito "grande" ali mistura tratamento e dificuldade da kata, e nao
deve ser lido como evidencia.

### 4.6 Sintese da RQ3

| metrica | Teste | n | p-valor | Tamanho de efeito | Decisao (alfa = 0,05) |
|---|---|---|---|---|---|
| CC media | Wilcoxon pareado por kata | 4 | 0,6250 | rank-biserial = +0,400 | nao rejeita H0 (sem poder) |
| CC media | Mann-Whitney U | 18 | 0,1988 | Cliff's delta = -0,370 | nao rejeita H0 |
| CC soma / LOC | Wilcoxon pareado por kata | 4 | 0,2500 | rank-biserial = -0,800 | nao rejeita H0 (sem poder) |
| CC soma / LOC | Mann-Whitney U | 18 | 0,1575 | Cliff's delta = -0,407 | nao rejeita H0 |
| LOC | Wilcoxon pareado por kata | 4 | 0,6250 | rank-biserial = +0,400 | nao rejeita H0 (sem poder) |
| LOC | Mann-Whitney U | 18 | 0,4003 | Cliff's delta = -0,247 | nao rejeita H0 |
| % duplicado | ambos | - | nao aplicavel | - | 1 de 18 trials com duplicacao |

**Resposta da RQ3:** o experimento **nao mostra** que o assistente altera a complexidade ou a
duplicacao do codigo. A mediana de complexidade foi menor com IA (8 contra 13), mas nenhum dos
dois testes e significativo e, dentro da mesma kata, a direcao se divide meio a meio. LOC nao
difere entre tratamentos, e duplicacao praticamente nao ocorreu. Diferente da RQ1 - onde o efeito
foi maximo e so o Wilcoxon nao tinha poder -, na RQ3 nao ha efeito consistente a relatar.
