# Resultados — RQ05 a RQ08

> Texto da seção 3 do artigo. Números de `data/saida/analise/` (`python -m analise.rq05`, `rq06`, `rq07`, `rq08`), 270 repositórios.

## 3.7 RQ05: frequência de deploy × taxa de falha

| Variante do CFR | n | ρ de Spearman | p | Força |
|---|---|---|---|---|
| (a) CI | 270 | 0,25 | 2,2 × 10⁻⁵ | fraca, positiva |
| (b) entrega (v5) | 270 | 0,73 | 1,8 × 10⁻⁴⁵ | forte, positiva |

![Dispersão frequência × CFR](../../data/saida/analise/rq05_dispersao.png)

Nas duas variantes, **quanto maior a frequência de deploy, maior o CFR**, o oposto do que o DORA sugere. A relação com o CFR (a) é fraca (ρ = 0,25). Com o CFR (b) é forte (ρ = 0,73) e em parte **mecânica**: o CFR (b) conta uma release como falha se outra release corretiva sai em até 7 dias, e quem publica com mais frequência tem mais chance de ter alguma release no intervalo de 7 dias. O gráfico mostra isso nos repositórios de baixa frequência, que ficam em degraus (poucas releases, CFR em frações simples como 0, 1/6 ou 1/3). A correlação positiva aparece com todas as versões da heurística: ρ = 0,75 (v1), 0,52 (v2), 0,67 (v3), 0,68 (v4) e 0,73 (v5). Como a medida (b) tem esse viés, o resultado que deve sustentar a discussão é o da variante (a). Correlação não é causalidade: repositórios com mais releases também têm mais CI, mais contribuidores e mais mudanças em cada janela.

## 3.8 RQ06: características associadas ao desempenho

Cinco fatores (linguagem principal, popularidade, contribuidores, idade, tipo do projeto) contra seis métricas (RQ01 a RQ04 com as duas variantes de lead time e de CFR) deram **30 testes** (Kruskal-Wallis, com ε² como tamanho de efeito), com correção de Holm. Popularidade, contribuidores e idade foram divididos em quartis (68, 67, 67 e 68 repositórios); linguagens com menos de 15 repositórios foram agrupadas em "Outras"; o tipo do projeto existe só para os 60 repositórios da amostra-ouro.

**Nove dos 30 testes continuam significativos depois de Holm (p ajustado < 0,05):**

| Fator | Métrica | ε² | Magnitude | p (Holm) |
|---|---|---|---|---|
| idade | lead time (a) | 0,28 | grande | < 0,001 |
| idade | CFR (b) | 0,26 | grande | < 0,001 |
| idade | lead time (b) | 0,24 | grande | < 0,001 |
| idade | frequência de deploy | 0,16 | grande | < 0,001 |
| contribuidores | lead time (b) | 0,13 | médio | < 0,001 |
| contribuidores | lead time (a) | 0,11 | médio | < 0,001 |
| linguagem | lead time (b) | 0,09 | médio | 0,016 |
| linguagem | lead time (a) | 0,08 | médio | 0,033 |
| idade | tempo de recuperação | 0,06 | pequeno | 0,036 |

Popularidade (estrelas) e tipo do projeto não ficaram significativos em nenhuma métrica. Nos 21 testes restantes os tamanhos de efeito são quase todos desprezíveis ou pequenos. As exceções são a linguagem em relação à frequência (ε² = 0,07, médio) e o tipo do projeto (quatro testes médios e um grande: CFR (a), ε² = 0,18, p = 0,012 antes de Holm e 0,25 depois), que não alcançam significância ajustada, o que é esperado com 60 repositórios em 4 grupos.

**Pós-teste de extremos (Q4 contra Q1, Cliff's δ, Holm).** Os repositórios mais velhos (Q4) têm frequência de deploy menor (mediana de 0,27 contra 0,81 releases/semana; δ = −0,61, grande), lead time (a) maior (733 contra 27 horas; δ = 0,79, grande) e CFR (b) menor (0,23 contra 0,74; δ = −0,75, grande). Os repositórios com mais contribuidores têm lead time maior (693 contra 93 horas no lead time (a); δ = 0,52, grande), mas **não** publicam com mais frequência (δ = 0,00). Por tipo do projeto, aplicações/serviços e CLIs têm mediana de 0,48 e 0,52 releases/semana, contra 0,26 das bibliotecas/frameworks, mas essa diferença não é significativa (p = 0,15 antes de Holm).

**Robustez da idade.** A idade limita o lead time dos repositórios jovens, porque um commit não pode ser mais antigo que o repositório. Há 40 repositórios com menos de um ano de idade (lead time (a) mediano de 20 horas contra 321 horas nos demais). Refazendo o Spearman só com os 230 repositórios de pelo menos um ano, a associação diminui mas persiste: ρ = −0,34 (frequência), +0,38 (lead time (a)), +0,36 (lead time (b)) e −0,28 (CFR (b)). A associação com o tempo de recuperação não persiste (ρ = 0,12, p = 0,083).

![Frequência de deploy por quartil de contribuidores](../../data/saida/analise/rq06_contribuidores_frequencia.png)

## 3.9 RQ07: sensibilidade à definição operacional

Usamos quatro combinações. A combinação com **tags** do exemplo do enunciado não pôde ser calculada porque a coleta não baixou as tags; ela foi substituída por C3.

| Combinação | Unidade de deploy | Lead time | CFR |
|---|---|---|---|
| C1 (referência) | release | (a) | (a) CI |
| C2 | release + pré-release | (b) | (b) entrega |
| C3 | release | (b) | (a) CI |
| C4 | release | (a) | (b) entrega |

Distribuição da classe geral: C1 tem 21 Elite, 108 High, 117 Medium e 24 Low; C2 tem 4, 75, 160 e 31; C3 tem 23, 112, 114 e 21; C4 tem 2, 65, 168 e 35.

| Par | Mudaram de categoria | κ ponderado (linear) | Interpretação |
|---|---|---|---|
| C1 × C2 | 44,8% (121) | 0,37 | razoável |
| C1 × C3 | 18,9% (51) | 0,76 | substancial |
| C1 × C4 | 35,6% (96) | 0,54 | moderada |
| C2 × C3 | 36,7% (99) | 0,52 | moderada |
| C2 × C4 | 22,6% (61) | 0,64 | substancial |
| C3 × C4 | 41,5% (112) | 0,44 | moderada |

Entre 19% e 45% dos repositórios mudam de categoria conforme a definição. A escolha que mais pesa é a variante do CFR: as combinações que usam o CFR (b) (C2 e C4) classificam muito mais repositórios como Medium ou Low do que as que usam o CFR (a). Trocar só o lead time de (a) para (b) (C1 × C3) é a mudança que menos altera a classificação (19%). Já a **ordem relativa** dos repositórios é mais estável do que as faixas: o Spearman entre as pontuações vai de 0,53 (C1 × C2) a 0,82 (C1 × C3). A **frequência de deploy** (RQ01) é pouco sensível à unidade de deploy: contar também as pré-releases (4.119 em 98 repositórios) eleva a mediana de 0,38 para 0,46 releases por semana, e só 21 repositórios (7,8%) mudam de faixa de frequência. A classificação é pouco sensível à versão da heurística de release corretiva: entre v1 e v5, 2% a 13% dos repositórios mudam de categoria (κ ponderado de 0,79 a 0,97).

## 3.10 RQ08 (bônus): rework rate

O *rework rate* é a proporção de releases corretivas sobre todas as releases publicadas. Com a v5, a mediana é de 70% (IQR de 49% a 89%), contra 40% do CFR (b) do mesmo repositório (ρ = 0,36 entre eles). O número é alto porque a heurística marca mais releases como corretivas do que o consenso (63% contra 45% nas 300 releases rotuladas) e porque a v1, a mais usada na literatura, marca quase todas (mediana de 98%). A diferença para o CFR (b) é conceitual: o CFR (b) conta a release que **falhou** (a que é seguida por uma correção), enquanto o *rework rate* conta a release **corretiva** em si; um repositório com várias correções seguidas tem *rework rate* alto e CFR (b) que depende de como elas se agrupam.
