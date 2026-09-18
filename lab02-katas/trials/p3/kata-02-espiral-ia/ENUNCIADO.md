# K2 — Leitura em espiral anti-horária

> Time-box: **35 minutos**. Ao final do tempo o trial é encerrado com o código que existir.
> **Não edite nada em `test/`.** A suíte de aceitação é o critério do experimento.
> Implemente apenas `src/leitorEspiral.ts`.

## Contexto

Um sensor varre uma grade retangular de células e precisa reportar os valores lidos na
ordem em que percorreu a grade: em **espiral, no sentido anti-horário**, começando na
célula do canto superior esquerdo e **descendo** primeiro.

## Contrato

```ts
export function emEspiral(matriz: number[][]): number[]
```

- A matriz é **retangular** — `M` linhas por `N` colunas, com `M` e `N` independentes.
  Ela **não é necessariamente quadrada**.
- A saída tem exatamente `M * N` elementos, cada célula aparecendo uma única vez.

## Ordem do percurso

Anti-horário, partindo de `[0][0]`: **desce** a primeira coluna → **avança** pela última
linha → **sobe** a última coluna → **volta** pela primeira linha → repete no retângulo
interno restante, até não sobrar célula.

Para

```
1 2 3
4 5 6
7 8 9
```

o resultado é `[1, 4, 7, 8, 9, 6, 3, 2, 5]`.

## Regras de borda

1. Matriz vazia (`[]`) → array vazio.
2. Matriz `1 x 1` → o único elemento.
3. Matriz de **uma linha só** ou de **uma coluna só** — o percurso degenera numa varredura
   simples, sem repetir célula.
4. Os valores podem se repetir e podem ser negativos; isso não afeta a ordem.

## Exemplos

| Entrada | Saída |
|---|---|
| `[[1,2],[3,4]]` | `[1, 3, 4, 2]` |
| `[[1,2,3,4]]` | `[1, 2, 3, 4]` |
| `[[1],[2],[3]]` | `[1, 2, 3]` |
| `[[1,2,3,4],[5,6,7,8]]` | `[1, 5, 6, 7, 8, 4, 3, 2]` |

## Como rodar os testes

```powershell
.\scripts\run_tests.ps1 -Kata katas\kata-02-espiral
```
