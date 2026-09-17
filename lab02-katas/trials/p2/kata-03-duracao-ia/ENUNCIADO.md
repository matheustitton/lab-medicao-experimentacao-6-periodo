# K3 — Duração legível

> Time-box: **35 minutos**. Ao final do tempo o trial é encerrado com o código que existir.
> **Não edite nada em `test/`.** A suíte de aceitação é o critério do experimento.
> Implemente apenas `src/duracaoLegivel.ts`.

## Contexto

Um painel mostra há quanto tempo um serviço está no ar. O valor bruto vem em segundos e
precisa virar um texto em português, legível por humanos.

## Contrato

```ts
export function formatar(segundos: number): string
```

## Regras

1. Unidades usadas, da maior para a menor: **semana** (7 dias), **dia** (24 horas),
   **hora**, **minuto**, **segundo**. Não existe "mês" nem "ano" nesta kata.
2. Unidades com valor **zero são omitidas** — `604801` é `"1 semana e 1 segundo"`,
   sem os dias, horas e minutos zerados.
3. Plural: `1 dia`, `2 dias`; `1 semana`, `2 semanas`; e assim por diante.
4. Junção: vírgula + espaço entre os itens, e **` e `** antes do último.
   Com um item só, não há conector.
5. `0` → `"agora"`.
6. Valor **negativo** → lançar `RangeError`.

## Exemplos

| Entrada | Saída |
|---|---|
| `0` | `"agora"` |
| `1` | `"1 segundo"` |
| `62` | `"1 minuto e 2 segundos"` |
| `3662` | `"1 hora, 1 minuto e 2 segundos"` |
| `86400` | `"1 dia"` |
| `604801` | `"1 semana e 1 segundo"` |
| `694861` | `"1 semana, 1 dia, 1 hora, 1 minuto e 1 segundo"` |

## Como rodar os testes

```powershell
.\scripts\run_tests.ps1 -Kata katas\kata-03-duracao
```
