<#
    test_run_trial.ps1 - autoteste do cronometro (Issue #26).

    Uso:
        .\scripts\test_run_trial.ps1

    Cobre os tres comportamentos que, se quebrarem, corrompem os dados do
    experimento inteiro:

      1. CENSURA   - trial que estoura o time-box e registrado com censurado=true
                     no valor do time-box, e a linha VAI para o CSV.
      2. VERDE     - trial que passa e registrado com censurado=false e tempo > 0.
      3. AMBIENTE  - run_tests.ps1 saindo com 3 (nenhum teste executado) aborta o
                     trial SEM gravar linha; um defeito de ambiente nao pode
                     virar "0% de sucesso" na RQ2.

    Escreve num CSV temporario e num workspace descartavel: nao encosta em
    data\trials.csv nem nos trials de verdade.
#>
$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $PSScriptRoot
$runTrial = Join-Path $PSScriptRoot 'run_trial.ps1'
$areaTeste = Join-Path $root 'data\.selftest'
$csvTeste = Join-Path $areaTeste 'trials-teste.csv'

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
function LinhasDoCsv {
    if (-not (Test-Path $csvTeste)) { return @() }
    return @(Import-Csv $csvTeste)
}

if (Test-Path $areaTeste) { Remove-Item -Recurse -Force $areaTeste }
New-Item -ItemType Directory -Force -Path $areaTeste | Out-Null

# ==============================================================================
Write-Host ''
Write-Host 'CASO 1 - censura no time-box (kata real, esqueleto sempre vermelho)'
# ==============================================================================
& $runTrial -Integrante selftest -Kata kata-06-delimitadores -Tratamento MANUAL `
            -Ordem 1 -TimeBoxSegundos 8 -IntervaloSegundos 2 -CsvPath $csvTeste | Out-Null
$saidaCaso1 = $LASTEXITCODE

$linhas = @(LinhasDoCsv)
$l1 = $linhas | Where-Object { $_.integrante -eq 'selftest' -and $_.kata -eq 'kata-06-delimitadores' }

Confere 'script termina com exit 0' ($saidaCaso1 -eq 0) "(exit=$saidaCaso1)"
Confere 'gravou exatamente uma linha' ($linhas.Count -eq 1) "(linhas=$($linhas.Count))"
Confere 'censurado = true' ($null -ne $l1 -and $l1.censurado -eq 'true') "(valor='$($l1.censurado)')"
Confere 'time_to_green_s = time-box (8)' ($null -ne $l1 -and [int]$l1.time_to_green_s -eq 8) "(valor='$($l1.time_to_green_s)')"
Confere 'registrou os 12 testes da kata' ($null -ne $l1 -and [int]$l1.testes_total -eq 12) "(valor='$($l1.testes_total)')"
Confere 'esqueleto passa 0 testes' ($null -ne $l1 -and [int]$l1.testes_passando -eq 0) "(valor='$($l1.testes_passando)')"
Confere 'taxa_sucesso = 0' ($null -ne $l1 -and [double]$l1.taxa_sucesso -eq 0) "(valor='$($l1.taxa_sucesso)')"
Confere 'tratamento preservado' ($null -ne $l1 -and $l1.tratamento -eq 'MANUAL') "(valor='$($l1.tratamento)')"

$wsCaso1 = Join-Path $root 'trials\selftest\kata-06-delimitadores-manual'
Confere 'workspace do trial foi criado' (Test-Path $wsCaso1)
Confere 'suite de aceitacao chegou intacta' (
    (Test-Path (Join-Path $wsCaso1 'test\validadorDelimitadores.test.ts')) -and
    -not (Compare-Object `
        (Get-Content (Join-Path $root 'katas\kata-06-delimitadores\test\validadorDelimitadores.test.ts')) `
        (Get-Content (Join-Path $wsCaso1 'test\validadorDelimitadores.test.ts')))
)
Confere 'enunciado copiado para o workspace' (Test-Path (Join-Path $wsCaso1 'ENUNCIADO.md'))
Confere 'XML arquivado como evidencia' (Test-Path (Join-Path $root 'data\junit\selftest-kata-06-delimitadores-manual.xml'))

# ==============================================================================
Write-Host ''
Write-Host 'CASO 2 - trial verde (kata sintetica que ja nasce resolvida)'
# ==============================================================================
# Kata sintetica em vez de solucao real: solucoes-referencia\ e ignorada pelo git
# e nao existe na maquina dos outros integrantes.
$kataSint = Join-Path $root 'katas\kata-99-selftest'
New-Item -ItemType Directory -Force -Path (Join-Path $kataSint 'src') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $kataSint 'test') | Out-Null
Set-Content -Path (Join-Path $kataSint 'ENUNCIADO.md') -Value '# Kata sintetica do autoteste' -Encoding utf8
Set-Content -Path (Join-Path $kataSint 'src\somar.ts') -Encoding utf8 -Value @'
export function somar(a: number, b: number): number {
  return a + b;
}
'@
Set-Content -Path (Join-Path $kataSint 'test\somar.test.ts') -Encoding utf8 -Value @'
import { somar } from "../src/somar";

describe("kata sintetica do autoteste", () => {
  it("soma dois numeros", () => {
    expect(somar(2, 3)).toBe(5);
  });
});
'@

try {
    & $runTrial -Integrante selftest -Kata kata-99-selftest -Tratamento IA `
                -Ordem 2 -TimeBoxSegundos 8 -IntervaloSegundos 1 -Prompts 3 -CsvPath $csvTeste | Out-Null
    $saidaCaso2 = $LASTEXITCODE
}
finally {
    Remove-Item -Recurse -Force $kataSint -ErrorAction SilentlyContinue
}

$linhas = @(LinhasDoCsv)
$l2 = $linhas | Where-Object { $_.kata -eq 'kata-99-selftest' }

Confere 'script termina com exit 0' ($saidaCaso2 -eq 0) "(exit=$saidaCaso2)"
Confere 'gravou a segunda linha' ($linhas.Count -eq 2) "(linhas=$($linhas.Count))"
Confere 'censurado = false' ($null -ne $l2 -and $l2.censurado -eq 'false') "(valor='$($l2.censurado)')"
Confere 'time_to_green_s dentro do time-box' ($null -ne $l2 -and [int]$l2.time_to_green_s -ge 0 -and [int]$l2.time_to_green_s -lt 8) "(valor='$($l2.time_to_green_s)')"
Confere 'taxa_sucesso = 1' ($null -ne $l2 -and [double]$l2.taxa_sucesso -eq 1) "(valor='$($l2.taxa_sucesso)')"
Confere 'n_prompts registrado' ($null -ne $l2 -and $l2.n_prompts -eq '3') "(valor='$($l2.n_prompts)')"

# ==============================================================================
Write-Host ''
Write-Host 'CASO 3 - ambiente quebrado nao vira dado'
# ==============================================================================
# Kata sem nenhum arquivo de teste: run_tests.ps1 sai com 3.
$kataVazia = Join-Path $root 'katas\kata-98-selftest'
New-Item -ItemType Directory -Force -Path (Join-Path $kataVazia 'src') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $kataVazia 'test') | Out-Null
Set-Content -Path (Join-Path $kataVazia 'ENUNCIADO.md') -Value '# sem testes' -Encoding utf8
Set-Content -Path (Join-Path $kataVazia 'src\nada.ts') -Value 'export const nada = 1;' -Encoding utf8

$antes = @(LinhasDoCsv).Count
try {
    & $runTrial -Integrante selftest -Kata kata-98-selftest -Tratamento MANUAL `
                -Ordem 3 -TimeBoxSegundos 8 -IntervaloSegundos 1 -CsvPath $csvTeste | Out-Null
    $saidaCaso3 = $LASTEXITCODE
}
finally {
    Remove-Item -Recurse -Force $kataVazia -ErrorAction SilentlyContinue
}
$depois = @(LinhasDoCsv).Count

Confere 'script aborta com exit 3' ($saidaCaso3 -eq 3) "(exit=$saidaCaso3)"
Confere 'NAO gravou linha no CSV' ($depois -eq $antes) "(antes=$antes depois=$depois)"

# --- limpeza ------------------------------------------------------------------
Remove-Item -Recurse -Force (Join-Path $root 'trials\selftest') -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force (Join-Path $root 'data\reports') -ErrorAction SilentlyContinue
Remove-Item -Force (Join-Path $root 'data\junit\selftest-kata-06-delimitadores-manual.xml') -ErrorAction SilentlyContinue
Remove-Item -Force (Join-Path $root 'data\junit\selftest-kata-99-selftest-ia.xml') -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force $areaTeste -ErrorAction SilentlyContinue

Write-Host ''
if ($falhas -eq 0) {
    Write-Host 'AUTOTESTE OK - censura, verde e ambiente quebrado conferidos.' -ForegroundColor Green
    exit 0
} else {
    Write-Host "AUTOTESTE FALHOU - $falhas verificacao(oes)." -ForegroundColor Red
    exit 1
}
