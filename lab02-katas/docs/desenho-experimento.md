# Lab02 — Desenho do experimento (Passo 1)

Experimento controlado comparando a resolução de katas de programação **com** e **sem**
assistente de IA generativa.

- **Grupo:** trio · **Disciplina:** Laboratório de Experimentação de Software
- **Sprint:** Lab02S01 · **Issue:** `#<preencher>`
- **Repositório / GitHub Projects:** `<preencher — mesmo board do Lab01, Projects #2>`

## Goal (GQM)

> Analisar **o uso de assistentes de IA generativa na resolução de tarefas de programação**,
> com o propósito de **comparar seu efeito frente à codificação manual**,
> com respeito a **tempo de resolução, qualidade funcional (defeitos) e qualidade estrutural
> do código produzido**,
> do ponto de vista do **grupo pesquisador**,
> no contexto de **katas de dificuldade equivalente resolvidos por estudantes de graduação sob
> condições controladas (crossover within-subject, time-boxed em 35 minutos)**.

---

## (A) Hipóteses

Direção declarada **antes** da coleta, para que a S03 não escolha o teste depois de ver os dados.
Nível de significância **α = 0,05** em todas as RQs.

| RQ | H₀ (nula) | H₁ (alternativa) | Cauda |
|---|---|---|---|
| **RQ1** — tempo | mediana(tempo_IA) = mediana(tempo_MANUAL) | mediana(tempo_IA) **<** mediana(tempo_MANUAL) | unicaudal |
| **RQ2** — defeitos | mediana(sucesso_IA) = mediana(sucesso_MANUAL) | mediana(sucesso_IA) **>** mediana(sucesso_MANUAL) | unicaudal |
| **RQ3** — estrutura | mediana(métrica_IA) = mediana(métrica_MANUAL), para complexidade e para duplicação | as medianas **diferem** | bicaudal |

RQ1 e RQ2 são unicaudais porque a alegação corrente sobre assistentes de IA é direcional
("resolve mais rápido e com menos erro") — é exatamente essa alegação que o experimento testa.
RQ3 é bicaudal porque não há direção consensual: há argumento plausível tanto para a IA produzir
código mais verboso e duplicado quanto para produzir código mais idiomático e enxuto.

## (B) Variáveis dependentes

Escolha entre as métricas candidatas do GQM, com a justificativa exigida pelo enunciado:

| RQ | Métrica | Papel | Por que esta |
|---|---|---|---|
| RQ1 | **time-to-green** — segundos entre o início do trial e a primeira execução com a suíte 100% verde | primária | métrica primária recomendada pelo enunciado. Trial que atinge o time-box sem sucesso é registrado **censurado em 2100 s**, nunca descartado |
| RQ1 | nº de prompts enviados ao assistente | exploratória | não obrigatória; serve à discussão qualitativa. O uso de um chatbot (e não de autocomplete) torna a contagem auditável — o log da conversa é anexado ao trial |
| RQ2 | **taxa de sucesso** — % de testes de aceitação passando ao fim do time-box | primária | normaliza katas com números diferentes de testes |
| RQ2 | nº absoluto de testes falhando | complementar | leitura direta, mais simples de reportar |
| RQ3 | **complexidade ciclomática (McCabe) por função** — regra `complexity` do ESLint | primária | é a métrica que a RQ3 pede; ver "Ferramentas da RQ3" abaixo |
| RQ3 | **% de linhas duplicadas** — jscpd | primária | o enunciado nomeia o jscpd como equivalente ao PMD CPD fora do Java |
| RQ3 | **LOC** | **controle obrigatório** | código gerado por IA tende a ser mais verboso; complexidade e duplicação sem normalizar por LOC podem enganar |

**Cálculo da taxa de sucesso**, a partir do XML do Jest
(`<testsuites tests="N" failures="F" errors="E">`):

```
testes_passando = tests - failures - errors
taxa_de_sucesso = testes_passando / tests
```

`errors` **precisa** entrar na conta: o esqueleto lança `Error("TODO")`. Ignorar `errors` faria um
trial sem nenhuma linha escrita aparecer com 100% de sucesso.

### Ferramentas da RQ3 e por que não é o CK

O enunciado pede CK ou PMD, "ou ferramenta equivalente, como Radon, se a linguagem escolhida não for
Java". A linguagem escolhida foi **TypeScript**, então o CK está fora por construção (só analisa
Java). O equivalente adotado:

| Métrica | Ferramenta | Papel do CK/Radon que substitui |
|---|---|---|
| Complexidade ciclomática por função | **ESLint**, regra `complexity` (McCabe) | `CK wmc` / `radon cc` |
| Duplicação | **jscpd** (`minTokens: 25`) | `PMD CPD` |
| LOC | contagem de linhas não vazias e não comentadas | métrica de controle |

Duas decisões registradas aqui para não parecerem omissão:

1. **`ts-complex` foi testado e descartado.** É a biblioteca npm que mais se aproxima do `radon`
   (dá CC, Halstead e Índice de Manutenibilidade), mas na verificação retornou `{}` para um arquivo
   com duas funções e CC = 2 para uma função com 5 ramos. Medida errada é pior que medida ausente.
   Como consequência, o **Índice de Manutenibilidade fica fora** — ele era item opcional do GQM,
   e nenhuma ferramenta confiável para TS foi encontrada.
2. **Complexidade será reportada como máximo e soma por arquivo, não só como média por função.**
   Na verificação, a solução de referência da K1 apareceu com 3 "funções" e CC `[5, 1, 1]`,
   média 2,33 — porque os callbacks de `.filter()` e `.sort()` contam como funções para o ESLint.
   Uma solução equivalente escrita com laços teria 1 função e CC 5. Ou seja: **a média por função
   pune quem usa laço e premia quem usa array method**, e código gerado por IA tende a usar mais
   array methods. Usar só a média produziria um resultado de RQ3 que mede estilo, não complexidade.
   Por isso a RQ3 reporta, por trial: **CC máximo**, **CC somado**, **nº de funções** e **CC médio**,
   todos normalizados por LOC quando comparados entre tratamentos.

## (C) Variável independente

**Uso do assistente de IA** — fator único, dois níveis (`IA`, `MANUAL`).

## (D) Tratamentos

| Nível | Permitido | Proibido |
|---|---|---|
| **`IA`** | **Claude (claude.ai, plano gratuito)**; documentação oficial; busca na web | outro assistente que não o Claude |
| **`MANUAL`** | documentação oficial (MDN, TypeScript Handbook); busca na web | qualquer assistente de IA, **incluindo autocomplete de IA na IDE** (Copilot, Cursor, IntelliSense com IA, Tabnine) — desligar antes do trial |

A documentação oficial fica liberada nos **dois** tratamentos de propósito: o contraste que interessa
é "com IA vs. codificação manual", não "com IA vs. sem nenhum recurso". Liberar documentação só no
tratamento `IA` transformaria o efeito medido numa mistura de dois fatores.

O mesmo assistente é usado em **todos** os trials do grupo, como exige o enunciado, para que o
tratamento seja comparável dentro do próprio experimento.

## (E) Objetos experimentais

**Seis** katas, o limite superior admitido pelo enunciado ("4 ou 6", número par), com suíte de
aceitação automatizada em Jest. Todas seguem o mesmo formato — função pura, determinística, sobre
tipos básicos, sem I/O, sem concorrência e sem estrutura de dados avançada — para que a variação
entre katas seja de raciocínio, e não de andaime. Catálogo, origem e evidência de calibração em
[katas.md](katas.md).

| # | Kata | Núcleo | Origem |
|---|---|---|---|
| K1 | Compressor de faixas | agrupar inteiros consecutivos em faixas | Codewars |
| K2 | Leitura em espiral | percorrer matriz retangular em espiral anti-horária | Codewars |
| K3 | Duração legível | decompor segundos em unidades, com plural e conectores | Codewars |
| K4 | Numeral romano | converter e **validar** numeral malformado | LeetCode #13 |
| K5 | Alcance da rainha | contar casas alcançáveis com obstáculos | clássico de entrevista |
| K6 | Delimitadores balanceados | pilha de delimitadores com literais entre aspas | LeetCode #20 |

Seis em vez de quatro eleva o Wilcoxon pareado por kata de n = 4 para **n = 6 pares** e o total de
trials de 12 para **18**, ao custo de 3h30 de trial por integrante.

## (F) Tipo de projeto experimental

**Crossover within-subject contrabalanceado.** Cada integrante resolve as 6 katas: 3 com IA e 3 sem.
Cada integrante é seu próprio controle, o que neutraliza a maior fonte de variação num N deste
tamanho — a diferença de habilidade entre pessoas.

Quadrado latino adaptado (3 sujeitos × 6 katas × 2 tratamentos):

| Integrante | 1º | 2º | 3º | 4º | 5º | 6º |
|---|---|---|---|---|---|---|
| **P1** | K1 · `IA` | K2 · `MANUAL` | K3 · `IA` | K4 · `MANUAL` | K5 · `IA` | K6 · `MANUAL` |
| **P2** | K3 · `MANUAL` | K4 · `IA` | K5 · `MANUAL` | K6 · `IA` | K1 · `MANUAL` | K2 · `IA` |
| **P3** | K5 · `IA` | K6 · `MANUAL` | K1 · `MANUAL` | K2 · `IA` | K3 · `MANUAL` | K4 · `IA` |

Propriedades garantidas por esta alocação:

1. Cada integrante faz **exatamente 3 `IA` e 3 `MANUAL`** — o balanço within-subject é exato.
2. **Nenhuma kata é resolvida duas vezes pela mesma pessoa** — elimina a forma mais grave do efeito
   de aprendizado.
3. Cada kata recebe os **dois** tratamentos ao longo do grupo (2–1 ou 1–2, já que 3 sujeitos não
   dividem em dois de forma exata).
4. A **posição na sequência** varia entre integrantes: nenhuma kata é sempre a primeira nem sempre a
   última, o que dilui efeito de ordem e de fadiga.
5. O total fica **9 trials `IA` e 9 trials `MANUAL`**.
6. Como a dificuldade das katas não é idêntica (ver [katas.md](katas.md)), esta alocação também
   garante que **nenhum integrante concentre as katas mais pesadas num só tratamento**.

## (G) Quantidade de medições

**18 trials** = 3 integrantes × 6 katas. Time-box de **35 minutos por trial**, o limite do enunciado —
o grupo optou por **não** reduzi-lo, para manter comparabilidade com os demais grupos da turma.
Intervalo mínimo de **10 minutos** entre trials consecutivos do mesmo integrante.

Registro por trial: `integrante`, `kata`, `tratamento`, `ordem`, `time_to_green_s`, `censurado`,
`testes_total`, `testes_passando`, `taxa_sucesso`, `n_prompts`, e o código final, que alimenta o
ESLint e o jscpd.

## Plano de análise estatística

Fixado **agora**, antes da coleta, para impedir escolha de teste após ver os dados.

1. **Teste principal — Wilcoxon signed-rank pareado por kata.** Para cada kata, a mediana dos trials
   `IA` contra a mediana dos trials `MANUAL` → **n = 6 pares**. É o pareamento natural deste desenho:
   a kata é o bloco, e parear por integrante é impossível, porque um integrante nunca resolve a mesma
   kata nos dois tratamentos. O bloco por kata é também o que absorve a diferença de dificuldade
   entre elas: uma kata mais pesada desloca os dois tratamentos e sai na diferença.
2. **Teste secundário — Mann-Whitney U** sobre os 18 trials individuais (9 `IA` × 9 `MANUAL`),
   reportado junto, porque n = 6 no Wilcoxon ainda tem poder baixo.
3. **Estatística descritiva — mediana e IQR**, nunca média e desvio-padrão, em toda tabela e todo
   gráfico, dado o N pequeno e a sensibilidade da média a outliers e a valores censurados.
4. **Tamanho de efeito** reportado junto de todo p-valor.
5. **Análise de sensibilidade** repetindo os testes sem os trials de P1 (ver ameaça #5).
6. **Interpretação:** com este N, "não rejeitamos H₀" **não** significa "não há efeito" — significa
   que o experimento não tem poder para detectá-lo. Isso será dito explicitamente na discussão do
   relatório final, e nenhuma conclusão causal será tirada de um resultado não significativo.

## (H) Ameaças à validade

### 1. Memorização / vazamento de solução — **a ameaça principal**

As seis katas derivam de exercícios públicos: três do Codewars (K1, K2, K3) e três de clássicos de
entrevista técnica (K4 = LeetCode #13, K5 = alcance da rainha, K6 = LeetCode #20). É provável que o
Claude tenha visto as soluções canônicas no treinamento, então o tratamento `IA` pode estar medindo
**recuperação de memória** em vez de assistência efetiva. O grupo escolheu conscientemente partir de
exercícios conhecidos, em vez de inventar katas do zero, e assume o custo dessa decisão.

*Mitigações aplicadas:* toda kata foi **reescrita** para que a solução canônica não passe direto na
suíte —

- **K1** troca o separador de faixa de `-` para `..` e admite valores repetidos na entrada;
- **K2** inverte o sentido para **anti-horário** e passa a exigir matriz **retangular**;
- **K3** muda a saída para português com concordância e troca as unidades (semana entra, ano sai);
- **K4** deixa de garantir entrada válida — o grosso do trabalho vira **rejeitar numeral malformado**;
- **K5** troca o 8×8 livre por tabuleiro **retangular com casas bloqueadas**;
- **K6** introduz **literais entre aspas** cujos delimitadores devem ser ignorados.

Cada suíte é **autoral** e testa justamente essas regras novas. O log de cada conversa com o Claude
fica arquivado junto do trial, permitindo inspecionar depois quanto da resposta veio pronta e quanto
teve de ser adaptado — é essa a evidência que sustenta a discussão qualitativa da ameaça.

*Risco residual:* **assumido e declarado**, e maior em K4 e K6, que na forma canônica estão entre os
exercícios mais indexados que existem. Esta é a limitação principal do experimento e será apresentada
como tal no relatório final.

### 2. Efeito de aprendizado e de ordem

Resolver uma kata ensina padrões que ajudam na seguinte, e a fadiga ao longo da sessão piora o
desempenho tardio. *Mitigação:* contrabalanceamento (F) — ordem diferente por integrante, nenhuma
kata repetida por pessoa, e intervalo mínimo de 10 minutos entre trials.

### 3. Familiaridade prévia com a ferramenta de IA

Quem já usa o Claude diariamente extrai mais dele do que quem nunca usou. *Mitigação:* assistente
**fixo** para os 3 integrantes; cada um declara no relatório sua frequência de uso prévia, que entra
como variável de contexto na discussão.

### 4. Variação de habilidade individual

*Mitigação:* é exatamente o que o desenho within-subject controla — cada integrante é seu próprio
controle, e as comparações são internas a cada pessoa antes de serem agregadas.

### 5. Contaminação do autor das katas

O integrante que escreveu os enunciados e as suítes (P1) conhece os casos de borda com antecedência
assimétrica em relação aos outros dois. *Mitigações:* as soluções de referência usadas para validar
as suítes ficam em `solucoes-referencia/`, diretório **não versionado** (ver `.gitignore`); os
esqueletos entregues não contêm nenhuma lógica; e a S03 executa uma **análise de sensibilidade**
refazendo os testes sem os trials de P1. Ameaça **declarada**, não eliminada.

### 6. Validade externa

3 estudantes, 6 katas algorítmicas curtas, tarefas isoladas com especificação completa e testes
prontos. Nada disso se parece com manutenção de uma base de código real, onde o valor de um
assistente pode ser maior (navegar código desconhecido) ou menor (contexto que não cabe no prompt).
Os resultados **não generalizam** para além do contexto descrito no Goal.

### 7. Efeito do time-box

O corte em 35 minutos comprime a cauda superior da distribuição de tempo: um trial que levaria
50 minutos e outro que levaria 3 horas são registrados com o mesmo valor. Isso **subestima** a
diferença real entre tratamentos. *Mitigação:* censura explícita (nunca descarte), uso da mediana em
vez da média, e relato do número de trials censurados em cada tratamento junto de todo resultado
de RQ1.

### 8. Instrumentação

Diferenças de máquina, IDE ou versão de ferramenta viram ruído no tempo medido. *Mitigação:* versões
fixadas no `package-lock.json` e instaladas com `npm ci` pelo `scripts/setup_ambiente.ps1`, e o mesmo
`scripts/run_tests.ps1` em todas as máquinas. O ciclo salvar-testar leva cerca de 1 segundo, então a
latência da ferramenta não compete com a variável dependente principal.

### 9. Efeito de expectativa dos participantes

Os participantes são os próprios pesquisadores e sabem qual hipótese está sendo testada, o que pode
enviesar o esforço aplicado em cada tratamento. Cegamento é impossível aqui — a pessoa obviamente
sabe se está usando IA. *Mitigação parcial:* o time-box e a suíte automatizada são critérios
objetivos, fora do controle do participante; não há espaço para julgamento subjetivo no desfecho.

### 10. Calibração das katas não validada com humanos

A equivalência de dificuldade entre as 6 katas está sustentada por evidência **estrutural**
(LOC, complexidade e nº de testes da solução de referência — ver [katas.md](katas.md)), não por um
piloto cronometrado com pessoas. Se uma kata for na prática muito mais difícil que as outras, ela
vira ruído no bloco correspondente do Wilcoxon. *Mitigação recomendada antes da S02:* um piloto com
alguém de fora do trio, ou o relato honesto desta limitação no relatório final.
