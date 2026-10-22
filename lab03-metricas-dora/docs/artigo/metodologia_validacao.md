# Metodologia — validação manual e heurística de release corretiva

> Texto da seção 2 do artigo (parte da validação), com os resultados reais de `data/saida/kappa_fleiss.csv`, `data/saida/avaliacao_heuristica.csv`, `data/saida/validacao_cruzada_heuristica.csv` e `docs/HISTORICO_HEURISTICA.md`.

## 2.6 Amostra-ouro

A heurística automática de release corretiva pode errar, e a única forma de medir o quanto é comparar com o julgamento de pessoas. Para isso, sorteamos 60 repositórios da amostra final com semente fixa (`df.sample(n=60, random_state=42)`) e, em cada um, 5 releases principais que têm release anterior (sorteio reprodutível com semente derivada de `42:repositório`). A planilha de cada avaliador traz links diretos para a página da release e para a comparação entre releases, e **não** contém a saída da heurística.

## 2.7 Rotulagem independente

Os três autores rotularam, cada um sozinho e sem consultar os demais, três dimensões:

1. **tipo do projeto**: biblioteca/framework, aplicação/serviço, ferramenta CLI ou outro (usado na RQ06);
2. **as releases representam entregas reais ao usuário?** sim, não ou incerto;
3. **a release é corretiva?** sim ou não, lendo as notas da release e a lista de commits (60 repositórios × 5 releases = 300 releases).

## 2.8 Concordância entre avaliadores

Calculamos o kappa de Fleiss por dimensão (`statsmodels`: `aggregate_raters` e `fleiss_kappa`) e a concordância bruta, e interpretamos o kappa pela escala de Landis e Koch (1977). O kappa corrige a concordância esperada por acaso, por isso é mais informativo que a porcentagem de acordos.

| Dimensão | n de itens | Kappa de Fleiss | Interpretação | Concordância bruta |
|---|---|---|---|---|
| tipo do projeto | 60 | 0,849 | quase perfeita | 85,0% |
| releases são entregas reais | 60 | 0,122 | leve | 83,3% |
| release corretiva | 300 | 0,739 | substancial | 80,7% |

O kappa de "entregas reais" é baixo apesar de 83% de concordância bruta por causa da distribuição muito desbalanceada dos rótulos: no consenso, 58 dos 60 repositórios são "sim", um é "não" e um é "incerto". Quando quase tudo é "sim", o acordo esperado por acaso é altíssimo e qualquer divergência derruba o kappa (o chamado paradoxo do kappa). Por isso essa dimensão não discrimina repositórios e não entra nas análises; o resultado indica que, para os avaliadores, praticamente todas as releases dos repositórios amostrados representam entregas. Para "release corretiva", houve unanimidade em 242 das 300 releases (81%), e a divergência é um pouco maior nas releases com 20 commits ou mais (22%) do que nas menores (17%), o que é compatível com releases que misturam correções e novidades, mas a diferença é pequena. Para tipo do projeto, houve unanimidade em 51 dos 60 repositórios.

## 2.9 Consenso e protocolo de desempate

O rótulo de consenso é a **maioria simples (2 de 3)**. Casos sem maioria (1-1-1) são decididos em reunião dos três autores e registrados em `rotulos/desempate_reuniao.csv`. Houve **um** caso de desempate: o repositório `zephyrproject-rtos/zephyr` (tipo do projeto), decidido em reunião como `outro`. Os demais 59 repositórios e as 300 releases tiveram maioria de 2 em 3.

## 2.10 Heurística de release corretiva (RQ03 b)

Testamos cinco versões, todas aplicadas a uma release R, sua release anterior e os commits entre elas:

| Versão | Regra |
|---|---|
| v1 (baseline do enunciado) | bump de *patch* (mesmo MAJOR.MINOR da anterior e PATCH maior) **ou** algum commit com `revert`, `hotfix` ou `fix` na mensagem (palavras inteiras: `prefix` não conta) |
| v2 (conservadora) | bump de *patch* **e** pelo menos um commit com essas palavras |
| v3 | bump de *patch* com até 5 commits ou com commit de correção; releases *minor/major* só se pelo menos 50% dos commits forem de correção |
| v4 (refinada) | ignora commits de *merge* e de dependência (`bump`, `deps`, `dependabot`); corretiva se for *patch* com correção (ou com até 2 commits úteis) ou se pelo menos 30% dos commits úteis forem de correção |
| v5 (refinada) | v4, ou release com commit de correção publicada em até 2 dias depois da release anterior |

Cada versão foi comparada com o consenso por precisão, recall e F1 (`scikit-learn`, `precision_recall_fscore_support`, classe positiva = corretiva). A meta era F1 ≥ 0,70.

| Versão | Precisão | Recall | F1 | Observação |
|---|---|---|---|---|
| v1 | 0,469 | 0,970 | 0,633 | marca 277 de 300 releases como corretivas |
| v2 | 0,643 | 0,687 | 0,664 | |
| v3 | 0,594 | 0,754 | 0,664 | |
| v4 | 0,600 | 0,806 | 0,688 | |
| v5 | 0,600 | 0,851 | **0,704** | versão adotada |

Nenhuma das versões do enunciado (v1 a v3) atingiu 0,70. Na v1, a palavra `fix` aparece em quase toda release (inclusive em `fix(deps)` de atualização automática de dependência), então a heurística marca 92% das releases e tem precisão de 0,47. A v4 remove esse ruído e passa a exigir uma fração de commits de correção, e a v5 acrescenta o intervalo curto desde a release anterior, que no consenso é um sinal de correção (53% das releases publicadas em até 1 dia depois da anterior são corretivas, contra 36% quando o intervalo passa de 14 dias).

Como os limiares da v4 e da v5 foram escolhidos nos mesmos 300 rótulos em que a F1 é medida, repetimos a escolha dentro de uma validação cruzada por repositório (5 dobras): a F1 da v5 fora da amostra é **0,697**, ou seja, a meta de 0,70 é atingida na amostra-ouro mas não de forma robusta. A precisão de 0,60 significa que 4 em cada 10 releases marcadas como corretivas não são; o CFR (b) e o *rework rate* são, portanto, limites superiores, e isso é tratado como ameaça à validade da RQ03 (b). A heurística só enxerga as mensagens de commit e os números de versão, enquanto os avaliadores leram as notas das releases, o que sugere que esse é o teto com esses sinais.

A versão adotada no dataset final foi a **v5** (F1 = 0,704 na amostra-ouro; 0,697 em validação cruzada). A classificação DORA mudou pouco entre versões da heurística (2% a 13% dos repositórios mudam de categoria; kappa ponderado de 0,79 a 0,97), como mostra a análise de sensibilidade.
