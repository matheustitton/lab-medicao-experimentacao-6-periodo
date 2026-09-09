<#
    test_run_metrics.ps1 - autoteste das metricas estaticas da RQ3 (Issue #27).

    Uso:
        .\scripts\test_run_metrics.ps1

    Todos os casos usam codigo sintetico com valores CONHECIDOS DE ANTEMAO -
    complexidade contada a mao, LOC contada a mao, duplicacao construida de
    proposito. Se a ferramenta mudar de comportamento numa atualizacao, o
    autoteste acusa antes de a S02 gerar dados errados.

    Escreve em CSV temporario: nao encosta em data\metrics.csv.
#>
$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $PSScriptRoot
$runMetrics = Join-Path $PSScriptRoot 'run_metrics.ps1'
$areaTeste = Join-Path $root 'data\.selftest-metrics'
$csvTeste = Join-Path $areaTeste 'metrics-teste.csv'
$csvPoolTeste = Join-Path $areaTeste 'pool-teste.csv'

$falhas = 0
function Confere {
    param([string]$Nome, [bool]$Condicao, [string]$Detalhe = '')
    if ($Condicao) {
        Write-Host "  [ok]    $Nome" -ForegroundColor Green
    } else {
        Write-Host "  [FALHA] $Nome $Detalhe" -ForegroundColor Red
        $script:falhas++
    }
}
function CriaAmostra {
    param([string]$Caminho, [string]$Conteudo)
    New-Item -ItemType Directory -Force -Path (Join-Path $Caminho 'src') | Out-Null
    [System.IO.File]::WriteAllText(
        (Join-Path $Caminho 'src\amostra.ts'), $Conteudo,
        (New-Object System.Text.UTF8Encoding $false))
}
function Linha {
    param([string]$TrialId)
    return (Import-Csv $csvTeste) | Where-Object { $_.trial_id -eq $TrialId }
}

if (Test-Path $areaTeste) { Remove-Item -Recurse -Force $areaTeste }
New-Item -ItemType Directory -Force -Path $areaTeste | Out-Null

# ==============================================================================
Write-Host ''
Write-Host 'CASO 1 - complexidade ciclomatica e LOC com valores conhecidos'
# ==============================================================================
# 1 funcao, 9 linhas de codigo, e 4 ramos alem do caminho base:
#   if, if, for, ternario  ->  CC = 1 + 4 = 5
$amostra1 = Join-Path $areaTeste 'cc-basico'
CriaAmostra -Caminho $amostra1 -Conteudo @'
export function alvo(n: number): string {
  if (n < 0) throw new Error("neg");
  if (n === 0) return "zero";
  let r = "";
  for (let i = 0; i < n; i++) {
    r += i % 2 === 0 ? "a" : "b";
  }
  return r;
}
'@

& $runMetrics -Trial $amostra1 -CsvPath $csvTeste -Quiet | Out-Null
$saida1 = $LASTEXITCODE
$l1 = Linha 'cc-basico'

Confere 'script termina com exit 0' ($saida1 -eq 0) "(exit=$saida1)"
Confere 'n_funcoes = 1' ($null -ne $l1 -and [int]$l1.n_funcoes -eq 1) "(valor='$($l1.n_funcoes)')"
Confere 'cc_max = 5 (1 + if + if + for + ternario)' ($null -ne $l1 -and [int]$l1.cc_max -eq 5) "(valor='$($l1.cc_max)')"
Confere 'cc_soma = 5' ($null -ne $l1 -and [int]$l1.cc_soma -eq 5) "(valor='$($l1.cc_soma)')"
Confere 'loc = 9' ($null -ne $l1 -and [int]$l1.loc -eq 9) "(valor='$($l1.loc)')"
Confere 'cc_max_por_loc com PONTO decimal' ($null -ne $l1 -and $l1.cc_max_por_loc -notmatch ',') "(valor='$($l1.cc_max_por_loc)')"
Confere 'sem duplicacao neste arquivo' ($null -ne $l1 -and [double]$l1.pct_duplicado -eq 0) "(valor='$($l1.pct_duplicado)')"
Confere 'jscpd realmente analisou linhas' ($null -ne $l1 -and [int]$l1.linhas_analisadas -gt 0) "(valor='$($l1.linhas_analisadas)')"

# ==============================================================================
Write-Host ''
Write-Host 'CASO 2 - callbacks de array method contam como funcao'
# ==============================================================================
# Trava o comportamento documentado em docs\desenho-experimento.md, secao
# "Ferramentas da RQ3": o ESLint conta cada arrow como funcao, entao a MEDIA por
# funcao premia quem usa array method e pune quem usa laco. E por isso que a RQ3
# reporta cc_max e cc_soma, e nao so a media.
$amostra2 = Join-Path $areaTeste 'cc-callbacks'
CriaAmostra -Caminho $amostra2 -Conteudo @'
export function filtrar(xs: number[], minimo: number): number[] {
  if (xs.length === 0) return [];
  return xs.filter((x) => x > minimo).sort((a, b) => a - b);
}
'@

& $runMetrics -Trial $amostra2 -CsvPath $csvTeste -Quiet | Out-Null
$l2 = Linha 'cc-callbacks'

Confere 'n_funcoes = 3 (a funcao + os 2 callbacks)' ($null -ne $l2 -and [int]$l2.n_funcoes -eq 3) "(valor='$($l2.n_funcoes)')"
Confere 'cc_max = 2 (a funcao externa)' ($null -ne $l2 -and [int]$l2.cc_max -eq 2) "(valor='$($l2.cc_max)')"
Confere 'cc_soma = 4' ($null -ne $l2 -and [int]$l2.cc_soma -eq 4) "(valor='$($l2.cc_soma)')"
Confere 'cc_media diluida pelos callbacks (< cc_max)' ($null -ne $l2 -and [double]$l2.cc_media -lt [double]$l2.cc_max) "(media='$($l2.cc_media)' max='$($l2.cc_max)')"

# ==============================================================================
Write-Host ''
Write-Host 'CASO 3 - duplicacao detectada'
# ==============================================================================
# Duas funcoes com corpo identico de 4 linhas, bem acima do limiar de 25 tokens.
$amostra3 = Join-Path $areaTeste 'duplicado'
CriaAmostra -Caminho $amostra3 -Conteudo @'
export function alfa(a: number, b: number, c: number): number {
  const soma = a + b + c;
  const media = soma / 3;
  const desvio = Math.abs(a - media) + Math.abs(b - media) + Math.abs(c - media);
  return soma + media + desvio;
}

export function beta(a: number, b: number, c: number): number {
  const soma = a + b + c;
  const media = soma / 3;
  const desvio = Math.abs(a - media) + Math.abs(b - media) + Math.abs(c - media);
  return soma + media + desvio;
}
'@

& $runMetrics -Trial $amostra3 -CsvPath $csvTeste -Quiet | Out-Null
$l3 = Linha 'duplicado'

Confere 'pct_duplicado > 0' ($null -ne $l3 -and [double]$l3.pct_duplicado -gt 0) "(valor='$($l3.pct_duplicado)')"
Confere 'linhas_duplicadas > 0' ($null -ne $l3 -and [int]$l3.linhas_duplicadas -gt 0) "(valor='$($l3.linhas_duplicadas)')"
Confere 'pct_duplicado com PONTO decimal' ($null -ne $l3 -and $l3.pct_duplicado -notmatch ',') "(valor='$($l3.pct_duplicado)')"

# ==============================================================================
Write-Host ''
Write-Host 'CASO 4 - integridade do CSV'
# ==============================================================================
$linhasBrutas = [System.IO.File]::ReadAllLines($csvTeste)
$bytes = [System.IO.File]::ReadAllBytes($csvTeste)
$temBom = ($bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF)

Confere 'cabecalho aparece uma unica vez' (@($linhasBrutas | Where-Object { $_ -like 'trial_id,*' }).Count -eq 1)
Confere 'uma linha por execucao (3)' ($linhasBrutas.Count -eq 4) "(linhas=$($linhasBrutas.Count))"
Confere 'toda linha tem 15 campos' (@($linhasBrutas | Where-Object { ($_ -split ',').Count -ne 15 }).Count -eq 0)
Confere 'CSV sem BOM (pandas leria "﻿trial_id")' (-not $temBom)

# ==============================================================================
Write-Host ''
Write-Host 'CASO 5 - duplicacao por pool (kata, tratamento)'
# ==============================================================================
# Dois "integrantes" entregam a mesma solucao para a mesma kata no mesmo
# tratamento: o pool tem que acusar duplicacao mesmo com cada arquivo isolado
# marcando 0%.
$corpoIgual = @'
export function repetida(a: number, b: number, c: number): number {
  const soma = a + b + c;
  const media = soma / 3;
  const desvio = Math.abs(a - media) + Math.abs(b - media) + Math.abs(c - media);
  return soma + media + desvio;
}
'@
foreach ($integrante in @('mtest1', 'mtest2')) {
    CriaAmostra -Caminho (Join-Path $root "trials\$integrante\kata-97-selftest-ia") -Conteudo $corpoIgual
}

try {
    & $runMetrics -Todos -CsvPath $csvTeste -CsvPoolPath $csvPoolTeste -Quiet | Out-Null
    $saida5 = $LASTEXITCODE
}
finally {
    Remove-Item -Recurse -Force (Join-Path $root 'trials\mtest1'), (Join-Path $root 'trials\mtest2') -ErrorAction SilentlyContinue
}

$pool = @(Import-Csv $csvPoolTeste) | Where-Object { $_.kata -eq 'kata-97-selftest' -and $_.tratamento -eq 'IA' }
$trialIndividual = (Import-Csv $csvTeste) | Where-Object { $_.trial_id -eq 'mtest1-kata-97-selftest-ia' }

Confere 'script termina com exit 0' ($saida5 -eq 0) "(exit=$saida5)"
Confere 'trial_id derivado do caminho (integrante-kata-tratamento)' ($null -ne $trialIndividual)
Confere 'tratamento IA reconhecido' ($null -ne $trialIndividual -and $trialIndividual.tratamento -eq 'IA') "(valor='$($trialIndividual.tratamento)')"
Confere 'pool agrupou os 2 trials' ($null -ne $pool -and [int]$pool.n_trials -eq 2) "(valor='$($pool.n_trials)')"
Confere 'pool acusa duplicacao entre solucoes iguais' ($null -ne $pool -and [double]$pool.pct_duplicado -gt 0) "(valor='$($pool.pct_duplicado)')"
Confere 'trial isolado marca 0% (por isso o pool existe)' ($null -ne $trialIndividual -and [double]$trialIndividual.pct_duplicado -eq 0) "(valor='$($trialIndividual.pct_duplicado)')"

# --- limpeza ------------------------------------------------------------------
Remove-Item -Recurse -Force $areaTeste -ErrorAction SilentlyContinue

Write-Host ''
if ($falhas -eq 0) {
    Write-Host 'AUTOTESTE OK - complexidade, LOC, duplicacao, CSV e pool conferidos.' -ForegroundColor Green
    exit 0
} else {
    Write-Host "AUTOTESTE FALHOU - $falhas verificacao(oes)." -ForegroundColor Red
    exit 1
}
