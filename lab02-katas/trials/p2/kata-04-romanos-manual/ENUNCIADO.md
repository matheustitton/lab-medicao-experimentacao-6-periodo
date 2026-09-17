# K4 — Numeral romano com validação

> Time-box: **35 minutos**. Ao final do tempo o trial é encerrado com o código que existir.
> **Não edite nada em `test/`.** A suíte de aceitação é o critério do experimento.
> Implemente apenas `src/numeralRomano.ts`.

## Contexto

Um acervo digitaliza inscrições e recebe os números como texto em algarismos romanos. Muitas
inscrições estão desgastadas e chegam **malformadas**. Você deve criar um algoritmo que converta esses
algarismos em números indoarábicos (usados hoje no Ocidente). Considere que inscrições malformadas devem
ser rejeitadas.

## Contrato

```ts
export function paraDecimal(romano: string): number
```

Converte o numeral para inteiro, ou lança `RangeError` se o numeral for inválido.

## Valores dos símbolos

| I | V | X | L | C | D | M |
|---|---|---|---|---|---|---|
| 1 | 5 | 10 | 50 | 100 | 500 | 1000 |

## Regras de formação (é aqui que está o trabalho)

Um numeral só é válido se **todas** valerem:

1. Contém apenas os sete símbolos acima, em **maiúsculas**. String vazia é inválida.
2. `I`, `X`, `C` e `M` podem repetir **no máximo 3 vezes seguidas**. `IIII` é inválido.
3. `V`, `L` e `D` **nunca se repetem** — nem seguidas, nem separadas. `VIV` é inválido.
4. As únicas subtrações permitidas são **`IV`, `IX`, `XL`, `XC`, `CD`, `CM`**.
   Qualquer outro símbolo menor antes de um maior é inválido: `IL`, `IC`, `VX`, `XD` são inválidos.
5. Fora dos pares subtrativos, os símbolos aparecem em **ordem não crescente** de valor,
   e **depois de um par subtrativo só pode vir símbolo de valor menor** que o símbolo subtraído.
   `XIX` é válido (`X` + `IX`); `IXI` e `IXIX` são inválidos.

## Exemplos

| Entrada | Saída |
|---|---|
| `"I"` | `1` |
| `"IV"` | `4` |
| `"IX"` | `9` |
| `"XIV"` | `14` |
| `"MCMXCIV"` | `1994` |
| `"MMMCMXCIX"` | `3999` |
| `"IIII"` | `RangeError` |
| `"IL"` | `RangeError` |
| `"VIV"` | `RangeError` |
| `"abc"` | `RangeError` |

## Como rodar os testes

```powershell
.\scripts\run_tests.ps1 -Kata katas\kata-04-romanos
```
