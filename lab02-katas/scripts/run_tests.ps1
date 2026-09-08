<#
    run_tests.ps1 - roda a suite de aceitacao de uma kata (ou de um trial).

    Uso:
        .\scripts\run_tests.ps1 -Kata katas\kata-01-faixas
        .\scripts\run_tests.ps1 -Kata trials\p1\k01-ia -ReportsDir data\reports\p1-k01-ia -Quiet

    Contrato com o cronometro (Issue S01-B):
        exit 0 -> suite verde (time-to-green atingido)
        exit 1 -> suite vermelha (ha teste falhando)
        exit 3 -> AMBIENTE QUEBRADO: o Jest nao chegou a executar nenhum teste
                  (dependencia faltando, config invalida, arquivo de teste sumido).
                  NAO e o mesmo que suite vermelha: um trial nesta condicao tem
                  que ser refeito, e nunca registrado como 0% de sucesso.
        Relatorio JUnit XML em <ReportsDir>\junit.xml, com o elemento raiz
        <testsuites tests="N" failures="F" errors="E">, de onde sai a RQ2:
            testes_passando = tests - failures - errors
            taxa_de_sucesso = testes_passando / tests
        `errors` PRECISA entrar na conta: o esqueleto lanca Error("TODO"), e um
        trial sem nenhuma linha escrita nao pode aparecer com 100% de sucesso.

    NUNCA redirecione o stderr deste script ("2>&1", "2>$null"). No PowerShell 5.1
    isso empacota cada linha do executavel nativo em ErrorRecord e corrompe o
    codigo de saida -- o Jest escreve o resumo da suite no stderr.
#>
param(
    [Parameter(Mandatory = $true)][string]$Kata,
    [string]$ReportsDir,
    [switch]$Quiet
)

$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $PSScriptRoot

if (-not (Test-Path (Join-Path $root 'node_modules'))) {
    Write-Error "Dependencias ausentes. Rode .\scripts\setup_ambiente.ps1 primeiro."
}
if (-not (Test-Path $Kata)) {
    Write-Error "Kata nao encontrada: $Kata"
}

$kataPath = (Resolve-Path $Kata).Path
if (-not $ReportsDir) { $ReportsDir = Join-Path $kataPath 'reports' }
New-Item -ItemType Directory -Force -Path $ReportsDir | Out-Null

# O jest.config.js vive na raiz do projeto: o Jest precisa ser invocado de la,
# com `--roots` apontando para a pasta alvo desta execucao.
Push-Location $root
try {
    # O jest-junit le o destino do XML destas variaveis de ambiente.
    $env:JEST_JUNIT_OUTPUT_DIR = (Resolve-Path $ReportsDir).Path
    $env:JEST_JUNIT_OUTPUT_NAME = 'junit.xml'

    $jestArgs = @('jest', '--roots', $kataPath)
    if ($Quiet) { $jestArgs += @('--reporters', 'jest-junit') }

    & npx @jestArgs
    $code = $LASTEXITCODE
}
finally {
    Pop-Location
}

# Guarda de integridade dos dados: uma suite que nao rodou tambem sai com exit 1,
# e sem esta checagem o cronometro registraria "0 de 12 testes passando" -- um
# defeito de ambiente viraria dado de RQ2.
$junitFile = Join-Path (Resolve-Path $ReportsDir).Path 'junit.xml'
$totalTestes = 0
if (Test-Path $junitFile) {
    $totalTestes = [int]([xml](Get-Content $junitFile)).testsuites.tests
}
if ($totalTestes -eq 0) {
    Write-Host ''
    Write-Host 'ERRO: nenhum teste foi executado. Isto e falha de ambiente, nao suite vermelha.' -ForegroundColor Red
    Write-Host 'Rode .\scripts\setup_ambiente.ps1 e refaca o trial.' -ForegroundColor Red
    exit 3
}

exit $code
