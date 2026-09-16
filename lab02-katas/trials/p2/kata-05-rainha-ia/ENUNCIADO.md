# K5 — Alcance da rainha com obstáculos

> Time-box: **35 minutos**. Ao final do tempo o trial é encerrado com o código que existir.
> **Não edite nada em `test/`.** A suíte de aceitação é o critério do experimento.
> Implemente apenas `src/alcanceDaRainha.ts`.

## Contexto

Depois de perder para o Deep Blue, Garry Kasparov resolveu reformular o jogo de xadrez, o transformando em um tabuleiro **retangular** e bloqueando algumas casas. Dada a posição da rainha, conte quantas casas ela alcança em **um único movimento**.

## Contrato

```ts
export function casasAlcancaveis(
  linhas: number,
  colunas: number,
  rainha: [number, number],
  bloqueadas: [number, number][]
): number
```

- Coordenadas são `[linha, coluna]`, ambas **base 0**.
- `rainha` é a casa de partida; `bloqueadas` pode vir vazio e **fora de ordem**.

## Regras

1. A rainha move nas **8 direções**: 4 ortogonais e 4 diagonais.
2. Ela desliza quantas casas quiser numa direção, mas **para antes de uma casa bloqueada** —
   a casa bloqueada **não** é contada, e nada além dela naquela direção é contado.
3. O tabuleiro tem borda: sair dele encerra a direção.
4. A casa da própria rainha **não** entra na contagem.
5. Uma casa bloqueada pode aparecer **repetida** na lista; isso não muda o resultado.

## Regras de borda

- Tabuleiro `1 x 1` → a rainha não tem para onde ir, resultado `0`.
- Se a lista de bloqueadas contiver a casa da própria rainha, **ignore essa entrada**
  (a rainha está lá, e isso não a impede de se mover).
- Bloqueadas fora dos limites do tabuleiro são **ignoradas**.

## Exemplos

Tabuleiro `3 x 3`, rainha no centro `[1,1]`, sem bloqueios → **8** (alcança todas as outras casas).

Tabuleiro `3 x 3`, rainha em `[0,0]`, sem bloqueios → **6**
(`[0,1]`, `[0,2]` à direita; `[1,0]`, `[2,0]` abaixo; `[1,1]`, `[2,2]` na diagonal — total 6).

| linhas × colunas | rainha | bloqueadas | Saída |
|---|---|---|---|
| `1 x 1` | `[0,0]` | `[]` | `0` |
| `3 x 3` | `[1,1]` | `[]` | `8` |
| `3 x 3` | `[1,1]` | `[[0,0]]` | `7` |
| `1 x 5` | `[0,0]` | `[]` | `4` |

## Como rodar os testes

```powershell
.\scripts\run_tests.ps1 -Kata katas\kata-05-rainha
```
