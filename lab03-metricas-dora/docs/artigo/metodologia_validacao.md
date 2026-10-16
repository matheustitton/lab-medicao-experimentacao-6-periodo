# Metodologia — validação manual e heurística de release corretiva (Pedro, issue #26)

> Rascunho para a seção 2 do artigo (parte da validação). Os trechos `[PREENCHER: ...]` dependem dos rótulos e dos resultados reais; use `data/saida/kappa_fleiss.csv`, `data/saida/avaliacao_heuristica.csv` e `docs/HISTORICO_HEURISTICA.md`.

## 2.6 Amostra-ouro

A heurística automática de release corretiva pode errar, e a única forma de medir o quanto é comparar com o julgamento de pessoas. Para isso, sorteamos 60 repositórios da amostra final com semente fixa (`df.sample(n=60, random_state=42)`) e, em cada um, 5 releases principais que têm release anterior (sorteio reprodutível com semente derivada de `42:repositório`). A planilha de cada avaliador traz links diretos para a página da release e para a comparação entre releases, e **não** contém a saída da heurística.

## 2.7 Rotulagem independente

Os três autores rotularam, cada um sozinho e sem consultar os demais, três dimensões:

1. **tipo do projeto**: biblioteca/framework, aplicação/serviço, ferramenta CLI ou outro (usado na RQ06);
2. **as releases representam entregas reais ao usuário?** sim, não ou incerto;
3. **a release é corretiva?** sim ou não, lendo as notas da release e a lista de commits (60 repositórios × 5 releases = `[PREENCHER: n de releases rotuladas]` releases).

## 2.8 Concordância entre avaliadores

Calculamos o kappa de Fleiss por dimensão (`statsmodels`: `aggregate_raters` e `fleiss_kappa`) e a concordância bruta, e interpretamos o kappa pela escala de Landis e Koch (1977). O kappa corrige a concordância esperada por acaso, por isso é mais informativo que a porcentagem de acordos.

| Dimensão | n de itens | Kappa de Fleiss | Interpretação | Concordância bruta |
|---|---|---|---|---|
| tipo do projeto | `[PREENCHER]` | `[PREENCHER]` | `[PREENCHER]` | `[PREENCHER]` |
| releases são entregas reais | `[PREENCHER]` | `[PREENCHER]` | `[PREENCHER]` | `[PREENCHER]` |
| release corretiva | `[PREENCHER]` | `[PREENCHER]` | `[PREENCHER]` | `[PREENCHER]` |

`[PREENCHER: se algum kappa ficou abaixo de 0,60, dizer que isso indica ambiguidade do critério e discutir um exemplo de divergência.]`

## 2.9 Consenso e protocolo de desempate

O rótulo de consenso é a **maioria simples (2 de 3)**. Casos sem maioria (1-1-1) são decididos em reunião dos três autores e registrados em `rotulos/desempate_reuniao.csv`. Foram `[PREENCHER: n]` casos de desempate.

## 2.10 Heurística de release corretiva (RQ03 b)

Testamos três versões, todas aplicadas a uma release R, sua release anterior e os commits entre elas:

| Versão | Regra |
|---|---|
| v1 (baseline do enunciado) | bump de *patch* (mesmo MAJOR.MINOR da anterior e PATCH maior) **ou** algum commit com `revert`, `hotfix` ou `fix` na mensagem (palavras inteiras: `prefix` não conta) |
| v2 (conservadora) | bump de *patch* **e** pelo menos um commit com essas palavras |
| v3 | bump de *patch* com até 5 commits ou com commit de correção; releases *minor/major* só se pelo menos 50% dos commits forem de correção |

Cada versão foi comparada com o consenso por precisão, recall e F1 (`scikit-learn`, `precision_recall_fscore_support`, classe positiva = corretiva). A meta era F1 ≥ 0,70.

| Versão | Precisão | Recall | F1 | Observação |
|---|---|---|---|---|
| v1 | `[PREENCHER]` | `[PREENCHER]` | `[PREENCHER]` | |
| v2 | `[PREENCHER]` | `[PREENCHER]` | `[PREENCHER]` | |
| v3 | `[PREENCHER]` | `[PREENCHER]` | `[PREENCHER]` | |

`[PREENCHER: se nenhuma versão atingiu 0,70, descrever cada refinamento tentado (v4, v5...) e seu F1, e a versão adotada no dataset final. Se mesmo assim ficou abaixo de 0,70, registrar como ameaça à validade da RQ03 (b).]`

A versão adotada no dataset final foi `[PREENCHER]` (F1 = `[PREENCHER]`).
