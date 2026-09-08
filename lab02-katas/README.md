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

## Métricas estáticas da RQ3

Comandos já verificados nas soluções de referência. Falta empacotá-los no
`scripts/run_metrics.ps1` (Issue S01-C):

```powershell
# Complexidade ciclomatica (McCabe) por funcao - substitui o CK/Radon, ver desenho
npx eslint --config eslint.complexity.config.mjs --no-config-lookup --format json "<dir>/**/src/*.ts"
# cada mensagem: "Function 'nome' has a complexity of N. Maximum allowed is 0."

# Duplicacao - substitui o PMD CPD
npx jscpd <dir> --min-tokens 25 --min-lines 3 --format typescript --reporters json --output <saida>
# statistics.total.percentage = % de linhas duplicadas
```

Por que não CK nem PMD: o CK só analisa Java, e a linguagem escolhida foi TypeScript. O enunciado
admite ferramenta equivalente nesse caso. O `ts-complex` (o análogo mais próximo do Radon) foi
testado e **descartado por medir errado** — detalhes em
[docs/desenho-experimento.md](docs/desenho-experimento.md), seção "Ferramentas da RQ3".

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
trials/     workspace de cada trial (preenchido na S02)
data/       CSVs de resultado (preenchido na S02)
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
