# K6 — Delimitadores balanceados com literais

> Time-box: **35 minutos**. Ao final do tempo o trial é encerrado com o código que existir.
> **Não edite nada em `test/`.** A suíte de aceitação é o critério do experimento.
> Implemente apenas `src/validadorDelimitadores.ts`.

## Contexto

Um editor precisa avisar quando os delimitadores de um trecho de código estão desbalanceados.
A complicação é que **trechos entre aspas são texto literal**: um `{` dentro de uma string não
abre bloco nenhum, e um validador que não souber disso vai reclamar do arquivo inteiro.

## Contrato

```ts
export function estaBalanceado(texto: string): boolean
```

## Regras

1. Delimitadores: `(` `)`, `[` `]`, `{` `}`. Cada um fecha com o par correspondente, e o
   fechamento respeita a ordem de abertura — `([)]` está errado, `([])` está certo.
2. **Aspas duplas (`"`) delimitam um literal.** Tudo entre um par de aspas é ignorado para
   efeito de balanceamento — inclusive delimitadores.
3. Uma aspa **aberta e não fechada** invalida o texto inteiro.
4. Qualquer outro caractere é ignorado.
5. Texto vazio é **válido**.
6. Não há caractere de escape: toda aspa dupla alterna entre "entrando" e "saindo" do literal.

## Exemplos

| Entrada | Saída | Por quê |
|---|---|---|
| `""` (vazio) | `true` | nada a balancear |
| `"([{}])"` | `true` | aninhamento correto |
| `"([)]"` | `false` | ordem de fechamento errada |
| `"("` | `false` | abre e não fecha |
| `")("` | `false` | fecha antes de abrir |
| `'("[")'` | `true` | o `[` está dentro do literal, é ignorado |
| `'(")'` | `false` | aspa aberta e nunca fechada |
| `'x = "{" ;'` | `true` | a chave está no literal; não sobra delimitador |

## Como rodar os testes

```powershell
.\scripts\run_tests.ps1 -Kata katas\kata-06-delimitadores
```
