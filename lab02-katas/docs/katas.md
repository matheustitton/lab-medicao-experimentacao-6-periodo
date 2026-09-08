# Katas do experimento — catálogo e calibração

Os seis objetos experimentais do Lab02. Ver [desenho-experimento.md](desenho-experimento.md),
item (E), para o papel deles no desenho.

## Critérios de seleção

Todas as katas obedecem ao mesmo molde, para que a variação entre elas seja de raciocínio e não de
andaime:

- uma única função exportada, **pura e determinística**;
- entrada e saída em **tipos básicos** (`number`, `string`, arrays deles);
- **sem** I/O, rede, data/hora do sistema, concorrência ou estrutura de dados avançada;
- resolvível em 15–30 minutos por quem conhece a linguagem, dentro do time-box de 35 min;
- **12 testes de aceitação** cada — número igual entre as seis, o que mantém comparável também a
  métrica complementar "nº absoluto de testes falhando", e não só a taxa percentual.

São **6** katas, o limite superior admitido pelo enunciado ("4 ou 6", número par). Seis em vez de
quatro eleva o Wilcoxon pareado por kata de n = 4 para **n = 6 pares** e o total de trials de 12 para
**18**, ao custo de 3h30 de trial por integrante.

## Origem e reescrita

Nenhuma das seis é inédita: três vêm do Codewars e três são clássicos de entrevista técnica. O
enunciado do laboratório recomenda exercícios pouco indexados justamente porque o assistente pode ter
memorizado a solução canônica — e essa é a **ameaça #1** do desenho. Como o grupo optou por partir de
exercícios conhecidos, **cada kata foi reescrita** para se afastar da versão original:

| # | Kata | Origem | O que foi alterado |
|---|---|---|---|
| K1 | Compressor de faixas | Codewars *Range Extraction* (4 kyu) | separador de faixa passa a ser `..` em vez de `-`; a entrada passa a admitir **valores repetidos**, que devem ser colapsados — o original garante entrada estritamente crescente |
| K2 | Leitura em espiral | Codewars *Snail Sort* (4 kyu) | sentido invertido para **anti-horário**, começando para baixo; matriz passa a ser **retangular `M × N`** em vez de quadrada `N × N` |
| K3 | Duração legível | Codewars *Human Readable Duration* (4 kyu) | saída em **português** com concordância de plural; unidades trocadas (**semana** entra, **ano** sai); entrada negativa passa a lançar `RangeError` — o original não define esse caso |
| K4 | Numeral romano | **LeetCode #13** *Roman to Integer* | o original **garante entrada válida**; aqui a maior parte do trabalho é **rejeitar numeral malformado** (repetição > 3, `V`/`L`/`D` repetidos, subtração fora da lista, ordem inválida após par subtrativo) |
| K5 | Alcance da rainha | clássico de xadrez / entrevista | tabuleiro **retangular** em vez de 8×8; **casas bloqueadas** que interrompem a direção; lista de pedras pode ter repetição, casa da própria rainha e coordenadas fora do tabuleiro, todas a serem ignoradas |
| K6 | Delimitadores balanceados | **LeetCode #20** *Valid Parentheses* | trechos entre **aspas duplas são literais** e os delimitadores dentro deles são ignorados; aspa não fechada invalida o texto — camada inexistente no original |

As suítes de aceitação são **autorais**: nenhuma foi copiada da fonte, e todas incluem os casos de
borda novos listados acima. Isso **não elimina** a ameaça de memorização — K4 e K6 são, na forma
canônica, dos exercícios mais indexados que existem — mas desloca o problema: a solução decorada
não passa na suíte sem ser adaptada.

## Evidência de calibração

Medida sobre a **solução de referência** de cada kata (a versão em `solucoes-referencia/`, escrita
para provar que a suíte é satisfazível), com as mesmas ferramentas que medirão os trials na RQ3.

| # | Kata | LOC | CC máx | CC somado | nº funções | testes |
|---|---|---|---|---|---|---|
| K1 | Compressor de faixas | 23 | 10 | 10 | 1 | 12 |
| K2 | Leitura em espiral | 23 | 10 | 10 | 1 | 12 |
| K3 | Duração legível | 23 | 7 | 7 | 1 | 12 |
| K4 | Numeral romano | 25 | 13 | 13 | 1 | 12 |
| K5 | Alcance da rainha | 30 | 7 | 14 | 4 | 12 |
| K6 | Delimitadores balanceados | 18 | 10 | 10 | 1 | 12 |
| | **faixa** | **18–30** | **7–13** | | | **12 em todas** |

- **LOC** — linhas não vazias e não comentadas.
- **CC** — complexidade ciclomática de McCabe pela regra `complexity` do ESLint.
- A K5 aparece com 4 funções porque os callbacks de `.filter()` e `.map()` contam como função para o
  ESLint — é o efeito discutido em [desenho-experimento.md](desenho-experimento.md), seção
  "Ferramentas da RQ3", e o motivo de a RQ3 reportar CC máximo e somado, e não apenas a média.

### Leitura honesta desta tabela

O conjunto **não é perfeitamente homogêneo**: a K4 é a mais pesada (CC 13, por causa das seis regras
de validação) e a K6 a mais leve (18 LOC). A faixa de LOC vai de 18 a 30 — um fator de ~1,7.

Isso incomoda menos do que parece, por causa do desenho: o Wilcoxon é **pareado por kata**, ou seja,
cada kata é um **bloco**, e `IA` é comparada com `MANUAL` *dentro* do bloco. Uma kata mais difícil
desloca os dois tratamentos daquele bloco na mesma direção e sai na diferença. O que a calibração
precisa garantir de fato é que **nenhum integrante receba uma carga sistematicamente pior**, e isso
quem resolve é o contrabalanceamento (item F do desenho), não a igualdade exata de dificuldade.

**Limitação declarada:** esta calibração é estrutural, não empírica. Nenhum piloto cronometrado com
pessoas foi executado — a solução de referência foi escrita por quem já conhecia o enunciado, então o
tempo gasto nela não estima o tempo de um participante. Registrado como **ameaça à validade #10**.

## Estrutura de uma kata

```
katas/kata-01-faixas/
  ENUNCIADO.md                        especificação entregue ao participante
  src/compressorDeFaixas.ts           esqueleto: assinatura + throw new Error("TODO")
  test/compressorDeFaixas.test.ts     suíte de aceitação — NÃO EDITAR durante o trial
```

O esqueleto não contém nenhuma lógica: na verificação, as 6 katas dão **12 testes, 12 falhas** antes
de qualquer linha ser escrita, e **12 testes, 0 falhas** com a solução de referência. Um teste que
passasse no esqueleto não mediria nada; uma suíte que nem a referência passasse mediria menos ainda.
