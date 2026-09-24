# Notas de consolidacao das tres RQs (insumo para introducao/discussao)

Rascunho de trabalho da Issue do dashboard - **nao** e parte numerada do relatorio (o
`montar_relatorio.py` so junta `NN-*.md`). Serve para quem escrever a introducao e a discussao
do relatorio final. Numeros de `python analise/dashboard.py`, que le os CSVs das RQs.

| RQ | mediana IA | mediana MANUAL | Wilcoxon por kata (n=4) | Mann-Whitney (18) | leitura |
|---|---|---|---|---|---|
| RQ1 tempo | 47 s | 541 s | p = 0,0625, r = -1,000 | p = 0,0002, delta = -1,000 | efeito maximo, estavel na sensibilidade |
| RQ2 sucesso | 100 % | 100 % | nao aplicavel | nao aplicavel | efeito teto |
| RQ3 CC media | 8 | 13 | p = 0,6250, r = +0,400 | p = 0,1988, delta = -0,370 | sem efeito consistente; direcao se divide por kata |
| RQ3 LOC | 33 | 36 | p = 0,6250, r = +0,400 | p = 0,4003, delta = -0,247 | sem diferenca |
| RQ3 duplicacao | 0 % | 0 % | nao aplicavel | nao aplicavel | 1 de 18 trials |

## O que se repete nas tres RQs

1. **O Wilcoxon por kata nunca pode rejeitar H0.** Duas katas receberam um tratamento so (K1 so
   IA, K6 so MANUAL), sobram 4 pares, e o menor p possivel e 0,0625 (unicaudal) / 0,125
   (bicaudal). Vale para as tres RQs - e limitacao da alocacao, nao do dado. Deve aparecer uma
   vez, com destaque, na secao de metodo/limitacoes, e ser so referenciada nos resultados.
2. **P1 e P2 tem a mesma alocacao.** Consequencia: o recorte "sem P3" nao tem nenhum par por
   kata, e o recorte "sem P1" depende inteiro de P2 e P3. Mesma raiz do item 1.
3. **Katas pequenas e com suite visivel saturam as metricas.** RQ2 em 100% para todos, duplicacao
   em 0% para 17 de 18, uma funcao por trial na mediana. O desenho discrimina tempo, mas nao
   qualidade nem estrutura.
4. **Direcao do efeito: so a RQ1 tem uma.** Tempo: IA mais rapida em todos os blocos e todos os
   trials. Complexidade: IA menor na mediana geral, mas maior em 2 das 4 katas pareadas. Nao
   da para escrever "IA mais rapida e com codigo mais simples" - so a primeira metade tem suporte.
5. **N = 3 integrantes em todas.** Nenhuma conclusao generaliza para alem deste grupo e destas
   katas; a ameaca de memorizacao (#1) pesa sobre as tres - tempo mediano de 47 s com 1 prompt
   e compativel com recuperacao de solucao conhecida.

## Pontos em aberto para a discussao

- Inspecionar manualmente `p3-kata-04-romanos-ia` (89 LOC, CC 23, unica duplicacao) antes de
  qualquer frase sobre "o codigo gerado pela IA".
- Trabalho futuro: alocacao que de os dois tratamentos a todas as katas (6 pares) e katas maiores
  ou com suite oculta, para tirar RQ2 e RQ3 do teto.
