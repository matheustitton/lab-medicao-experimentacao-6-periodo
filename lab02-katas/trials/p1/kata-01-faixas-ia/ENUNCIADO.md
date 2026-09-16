# K1 — Compressor de faixas

> Time-box: **35 minutos**. Ao final do tempo o trial é encerrado com o código que existir.
> **Não edite nada em `test/`.** A suíte de aceitação é o critério do experimento.
> Implemente apenas `src/compressorDeFaixas.ts`.

## Contexto

Um relatório lista códigos de leitura em ordem crescente. Para deixar o relatório curto,
sequências de códigos consecutivos são escritas de forma comprimida.

## Contrato

```ts
export function comprimir(valores: number[]): string
```

- `valores` vem em ordem **não decrescente** (pode conter repetições).
- Os itens da saída são separados por vírgula, **sem espaços**.

## Regras

1. Uma sequência de **3 ou mais** inteiros consecutivos vira `primeiro..ultimo`
   (dois pontos como separador — atenção, não é hífen).
2. Uma sequência de exatamente **2** consecutivos é escrita normalmente: `5,6`.
3. Valores **repetidos são colapsados** antes de qualquer análise: `3,3,3` é um valor só,
   e `1,2,2,3,4` é a sequência consecutiva de `1` a `4`.
4. Entrada vazia → string vazia `""`.
5. Valores negativos são válidos, inclusive faixas que atravessam o zero.

## Exemplos

| Entrada | Saída |
|---|---|
| `[]` | `""` |
| `[7]` | `"7"` |
| `[1, 4, 9]` | `"1,4,9"` |
| `[1, 2, 3]` | `"1..3"` |
| `[5, 6]` | `"5,6"` |
| `[1, 2, 3, 4, 7, 9, 10, 11]` | `"1..4,7,9..11"` |
| `[-2, -1, 0, 1, 2]` | `"-2..2"` |

## Como rodar os testes

```powershell
.\scripts\run_tests.ps1 -Kata katas\kata-01-faixas
```
