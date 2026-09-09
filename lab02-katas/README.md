# lab02-katas

Laboratório 02 — **Assistentes de IA vs. codificação manual: um experimento controlado**.
Katas, suítes de aceitação, scripts de medição e dados dos trials.

O desenho completo do experimento está em
[docs/desenho-experimento.md](docs/desenho-experimento.md).

## Requisitos

- Node.js 20+ (validado em 23.11) e npm 10+
- Assistente de IA do tratamento: **Claude (claude.ai, plano gratuito)**

## Setup

```powershell
.\scripts\setup_ambiente.ps1
```

Instala as dependências fixadas no `package-lock.json` e imprime as versões. As três máquinas devem
mostrar as mesmas versões — instrumentação idêntica é a mitigação da ameaça à validade #8.

## Rodando uma kata

```powershell
.\scripts\run_tests.ps1 -Kata katas\kata-01-faixas
```

## Contrato do script de testes

O cronômetro do trial (Issue S01-B) consome este contrato — mudá-lo quebra a coleta:

| Saída | Significado |
|---|---|
| `exit 0` | suíte verde — o *time-to-green* foi atingido |
| `exit 1` | suíte vermelha — há teste falhando |
| `exit 3` | **ambiente quebrado** — o Jest não executou nenhum teste |
| `<ReportsDir>\junit.xml` | relatório JUnit XML do Jest (via `jest-junit`) |

`exit 3` existe porque uma suíte que **não rodou** também sai com código 1. Sem essa distinção, uma
dependência faltando seria registrada como "0 de 12 testes passando" e um defeito de ambiente viraria
dado da RQ2. Trial que sair com 3 é **refeito**, nunca registrado.

Do XML saem as métricas da RQ2, lidas do elemento raiz
`<testsuites tests="N" failures="F" errors="E">`:

```
testes_passando = tests - failures - errors
taxa_de_sucesso = testes_passando / tests
```

`errors` **precisa** entrar na conta: o esqueleto lança `Error("TODO")`, e um trial sem nenhuma linha
escrita não pode aparecer com 100% de sucesso.

> **Nunca redirecione o stderr ao chamar o script** (`2>&1`, `2>$null`). O Jest escreve o resumo da
> suíte no stderr, e no PowerShell 5.1 capturar stderr de executável nativo empacota cada linha em
> `ErrorRecord` e corrompe o código de saída — o cronômetro passaria a ler `exit` errado.

## Cronometragem dos trials

`run_trial.ps1` é o que transforma "rodar uma kata" em "executar um trial registrado". Ele produz a
variável dependente primária da RQ1 — o *time-to-green*.

```powershell
.\scripts\run_trial.ps1 -Integrante p1 -Kata kata-04-romanos -Tratamento IA -Ordem 4
```

| Parâmetro | |
|---|---|
| `-Integrante` | `p1`, `p2`, `p3` — quem está resolvendo |
| `-Kata` | nome da pasta em `katas/` |
| `-Tratamento` | `IA` ou `MANUAL` |
| `-Ordem` | posição do trial na sequência do integrante (ver contrabalanceamento) |
| `-TimeBoxSegundos` | default `2100` (35 min). **Só pode ser reduzido** — o script recusa valor maior |
| `-IntervaloSegundos` | de quanto em quanto tempo verifica, default `5` |
| `-Prompts` | nº de interações com o Claude; opcional, pode ser preenchido no CSV depois |
| `-Observacoes` | texto livre |

O que ele faz:

1. Cria o workspace do trial em `trials/<integrante>/<kata>-<tratamento>/`, com cópia nova de `src/`,
   `test/` e do enunciado. **Você edita só `src/`.** A kata-fonte nunca é tocada.
2. Cronometra, reexecutando a suíte **a cada mudança em `src/`** — não em laço cego, para não
   competir por CPU com você durante os 35 minutos.
3. Encerra no primeiro verde, ou no estouro do time-box.
4. Grava uma linha em `data/trials.csv` e arquiva o XML final em `data/junit/<trial_id>.xml`.

### Regra de censura

Trial que atinge o time-box sem passar em todos os testes é registrado com
`censurado = true` e `time_to_green_s = <time-box>` — **e nunca descartado**. Descartar os fracassos
enviesaria a comparação a favor do tratamento que falha mais. É o que o enunciado do Lab02 exige.

Se o `run_tests.ps1` sair com **3** (ambiente quebrado, nenhum teste executado), o trial é **abortado
sem gravar linha**: defeito de infraestrutura não pode virar "0% de sucesso" na RQ2.

### Formato de saída — `data/trials.csv`

| Coluna | Conteúdo |
|---|---|
| `trial_id` | `<integrante>-<kata>-<tratamento>`, também o nome do XML em `data/junit/` |
| `integrante` | `p1` / `p2` / `p3` |
| `kata` | pasta da kata |
| `tratamento` | `IA` / `MANUAL` |
| `ordem` | posição na sequência do integrante |
| `inicio_iso`, `fim_iso` | timestamps ISO 8601 |
| `time_to_green_s` | **RQ1** — segundos até o primeiro verde, ou o time-box se censurado |
| `censurado` | `true` / `false` |
| `testes_total` | nº de testes da suíte (12 em todas as katas) |
| `testes_passando` | `tests − failures − errors` do XML |
| `taxa_sucesso` | **RQ2** — `testes_passando / testes_total` |
| `n_prompts` | métrica exploratória da RQ1; vazio quando não informado |
| `observacoes` | texto livre, entre aspas |

### Autoteste

```powershell
.\scripts\test_run_trial.ps1
```

Verifica os três comportamentos que, se quebrarem, corrompem os dados do experimento: censura no
time-box, trial verde, e ambiente quebrado não virando dado. Sai com `0` se tudo passar. Escreve num
CSV temporário — não encosta no `data/trials.csv`.

## Métricas estáticas da RQ3

`run_metrics.ps1` mede o código final de cada trial e produz as três variáveis da RQ3:
**complexidade ciclomática**, **duplicação** e **LOC** (controle obrigatório).

```powershell
.\scripts\run_metrics.ps1 -Trial trials\p1\kata-01-faixas-ia   # um trial
.\scripts\run_metrics.ps1 -Todos                                # varre trials\ inteiro
.\scripts\run_metrics.ps1 -Trial katas\kata-01-faixas           # qualquer pasta com src\
```

Mede apenas o que está em `src/`; a suíte de aceitação em `test/` fica de fora (`.jscpd.json`).

### `data/metrics.csv` — uma linha por trial

| Coluna | Conteúdo |
|---|---|
| `trial_id` | `<integrante>-<kata>-<tratamento>` — **mesma chave do `data/trials.csv`**, para a S03 juntar os dois com um merge |
| `integrante`, `kata`, `tratamento` | derivados do caminho do trial |
| `arquivos` | nº de arquivos `.ts` medidos |
| `loc` | linhas não vazias e não comentadas — **métrica de controle obrigatória** |
| `n_funcoes` | quantas funções o ESLint encontrou |
| `cc_max` | maior complexidade ciclomática entre as funções |
| `cc_soma` | soma das complexidades |
| `cc_media` | média por função |
| `cc_max_por_loc`, `cc_soma_por_loc` | complexidade normalizada por LOC |
| `linhas_analisadas` | linhas que o jscpd considerou |
| `linhas_duplicadas`, `pct_duplicado` | duplicação dentro do código daquele trial |

**Por que quatro variantes de complexidade.** O ESLint conta cada callback de `.filter()`/`.map()`
como uma função. Uma solução escrita com array methods ganha média por função artificialmente baixa;
a mesma solução escrita com laço, alta. Como código gerado por IA tende a usar mais array methods,
usar só `cc_media` produziria um resultado de RQ3 que mede **estilo**, não complexidade. Por isso
`cc_max` e `cc_soma` saem junto, e a comparação entre tratamentos é feita normalizada por LOC.
Detalhes em [docs/desenho-experimento.md](docs/desenho-experimento.md), seção "Ferramentas da RQ3".

### `data/metrics_duplicacao_pool.csv` — métrica exploratória

Gerado por `-Todos`. Numa kata de ~25 linhas, o jscpd sobre um arquivo isolado dá 0% em quase todo
trial — a coluna `pct_duplicado` de `metrics.csv` tende a ser toda zero, e metade da RQ3 ficaria sem
sinal.

Este segundo CSV roda o jscpd sobre o **pool de trials da mesma `(kata, tratamento)`**, ou seja,
compara as soluções dos três integrantes entre si:

| Coluna | Conteúdo |
|---|---|
| `kata`, `tratamento` | o bloco medido |
| `n_trials` | quantas soluções entraram no pool |
| `linhas_analisadas`, `linhas_duplicadas`, `pct_duplicado` | duplicação dentro do pool |
| `clones` | nº de trechos clonados encontrados |

Se o pool `IA` for muito mais duplicado que o `MANUAL`, o achado é **"o assistente entrega
praticamente a mesma solução para todo mundo"** — relevante para a discussão da ameaça #1
(memorização). É uma métrica **exploratória**: a primária da RQ3 continua sendo o `pct_duplicado`
por trial.

### Autoteste

```powershell
.\scripts\test_run_metrics.ps1
```

25 verificações sobre código sintético com valores **contados à mão**: uma função com 4 ramos tem que
dar `cc_max = 5`; um arquivo de 9 linhas tem que dar `loc = 9`; dois corpos idênticos têm que acusar
duplicação; o CSV tem que sair sem BOM e com 15 campos por linha. Se uma atualização de ferramenta
mudar o comportamento, o autoteste acusa antes de a S02 gerar dados errados.

### Por que não CK nem PMD

O CK só analisa Java, e a linguagem escolhida foi TypeScript. O enunciado admite ferramenta
equivalente nesse caso.

| Métrica | Ferramenta | Substitui |
|---|---|---|
| Complexidade ciclomática (McCabe) | ESLint, regra `complexity` | `CK wmc` / `radon cc` |
| Duplicação | jscpd, `--min-tokens 25` | PMD CPD |
| LOC | contagem própria | métrica de controle |

O `ts-complex` (o análogo mais próximo do Radon) foi testado e **descartado por medir errado** —
detalhes em [docs/desenho-experimento.md](docs/desenho-experimento.md), seção "Ferramentas da RQ3".

### Nota sobre CSV no PowerShell 5.1

Os dois CSVs são gravados via `[System.IO.File]::WriteAllLines` com `UTF8Encoding($false)`, e os
números via `CultureInfo::InvariantCulture`. Não é preciosismo:

- `Set-Content -Encoding utf8` grava **BOM**, e o `pandas.read_csv` passa a ler a primeira coluna
  como `﻿trial_id` — `KeyError` obscuro no dashboard da S03.
- Em máquina com locale pt-BR, `"$([Math]::Round(0.5,4))"` vira `"0,5"`, e a vírgula **quebra a linha
  do CSV em colunas extras**, corrompendo o dataset em silêncio.

Quem for escrever outro script que gere CSV neste projeto: use os mesmos dois cuidados.

## Contrabalanceamento dos trials

Cada integrante resolve as 6 katas, 3 com IA e 3 sem, em ordem diferente — 18 trials no total:

| Integrante | 1º | 2º | 3º | 4º | 5º | 6º |
|---|---|---|---|---|---|---|
| **P1** | K1 · `IA` | K2 · `MANUAL` | K3 · `IA` | K4 · `MANUAL` | K5 · `IA` | K6 · `MANUAL` |
| **P2** | K3 · `MANUAL` | K4 · `IA` | K5 · `MANUAL` | K6 · `IA` | K1 · `MANUAL` | K2 · `IA` |
| **P3** | K5 · `IA` | K6 · `MANUAL` | K1 · `MANUAL` | K2 · `IA` | K3 · `MANUAL` | K4 · `IA` |

| # | Kata | Pasta |
|---|---|---|
| K1 | Compressor de faixas | `katas/kata-01-faixas` |
| K2 | Leitura em espiral | `katas/kata-02-espiral` |
| K3 | Duração legível | `katas/kata-03-duracao` |
| K4 | Numeral romano | `katas/kata-04-romanos` |
| K5 | Alcance da rainha | `katas/kata-05-rainha` |
| K6 | Delimitadores balanceados | `katas/kata-06-delimitadores` |

Time-box de **35 minutos por trial**. Ao final do tempo o trial é encerrado com o código que existir,
e o tempo é registrado como **censurado em 2100 s** — nunca descartado.

## Estrutura

```
docs/       desenho do experimento e catálogo das katas
katas/      os 6 objetos experimentais (enunciado + esqueleto + suíte)
scripts/    setup do ambiente e execução das suítes
trials/     workspace de cada trial, um por kata/tratamento (preenchido na S02)
data/       trials.csv (RQ1/RQ2), metrics.csv (RQ3) e junit/ (XML de cada trial, evidência bruta)
```

## Documentação

| Documento | Conteúdo |
|---|---|
| [docs/desenho-experimento.md](docs/desenho-experimento.md) | Hipóteses, variáveis, tratamentos, contrabalanceamento, plano estatístico, ameaças à validade |
| [docs/katas.md](docs/katas.md) | Origem das katas, o que foi reescrito, evidência de calibração |

## Convenções do grupo

Herdadas do Lab01, mesmo board (GitHub Projects #2):

- Cada cartão do board é uma **Issue** real, com **Assignee**.
- **Todo commit referencia o número da Issue**: `#31 desenho do experimento e katas`.
- Cada trial da S02 é uma **Issue individual** (uma por kata/tratamento), atribuída ao integrante
  responsável.
- Limite de WIP na coluna `Doing`: 3.
