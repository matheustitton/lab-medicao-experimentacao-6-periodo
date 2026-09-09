<#
    run_trial.ps1 - cronometra um trial do experimento (Issue #26).

    Mede a variavel dependente primaria da RQ1: o "time-to-green", isto e, o
    tempo entre o inicio do trial e a primeira execucao com a suite 100% verde.

    Uso:
        .\scripts\run_trial.ps1 -Integrante p1 -Kata kata-04-romanos -Tratamento IA -Ordem 4
        .\scripts\run_trial.ps1 -Integrante p2 -Kata kata-01-faixas -Tratamento MANUAL -Ordem 5 -Prompts 0

    O script:
      1. monta o workspace do trial em trials\<integrante>\<kata>-<tratamento>\
      2. cronometra, reexecutando a suite a cada mudanca em src\
      3. encerra no primeiro verde OU no estouro do time-box
      4. grava uma linha em data\trials.csv e arquiva o XML em data\junit\

    REGRA DE CENSURA (enunciado do Lab02): trial que atinge o time-box sem
    passar em todos os testes e registrado como CENSURADO no valor do time-box,
    e NUNCA descartado. Descartar os fracassos enviesaria a comparacao a favor
    do tratamento que falha mais.

    Formato de saida: ver secao "Cronometragem dos trials" no README.md.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$Integrante,
    [Parameter(Mandatory = $true)][string]$Kata,
    [Parameter(Mandatory = $true)][ValidateSet('IA', 'MANUAL')][string]$Tratamento,
    [Parameter(Mandatory = $true)][int]$Ordem,

    # 2100 s = 35 min, o time-box do enunciado. So pode ser reduzido, nunca aumentado.
    [int]$TimeBoxSegundos = 2100,
    [int]$IntervaloSegundos = 5,
    [int]$Prompts = -1,
    [string]$Observacoes = '',
    [string]$CsvPath
)

$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $PSScriptRoot
if ($TimeBoxSegundos -gt 2100) {
    Write-Error "Time-box maior que 2100 s (35 min). O enunciado permite reduzir, nunca aumentar."
}

$kataOrigem = Join-Path $root "katas\$Kata"
if (-not (Test-Path $kataOrigem)) {
    Write-Error "Kata nao encontrada: $kataOrigem"
}

$trialId  = "{0}-{1}-{2}" -f $Integrante, $Kata, $Tratamento.ToLower()
$workspace = Join-Path $root "trials\$Integrante\$Kata-$($Tratamento.ToLower())"
$reportsDir = Join-Path $root "data\reports\$trialId"
if (-not $CsvPath) { $CsvPath = Join-Path $root 'data\trials.csv' }

# --- 1. Workspace limpo -------------------------------------------------------
# Copia nova a cada trial: o participante nunca edita a kata-fonte, e a suite de
# aceitacao chega intacta. Se sobrasse codigo de uma tentativa anterior, o
# time-to-green mediria um trial que ja comecou resolvido.
if (Test-Path $workspace) {
    Write-Host "Workspace ja existe e sera recriado: $workspace" -ForegroundColor Yellow
    Remove-Item -Recurse -Force $workspace
}
New-Item -ItemType Directory -Force -Path $workspace | Out-Null
Copy-Item -Recurse (Join-Path $kataOrigem 'src') (Join-Path $workspace 'src')
Copy-Item -Recurse (Join-Path $kataOrigem 'test') (Join-Path $workspace 'test')
Copy-Item (Join-Path $kataOrigem 'ENUNCIADO.md') $workspace

$srcDir = Join-Path $workspace 'src'

Write-Host ''
Write-Host '=============================================================='
Write-Host " TRIAL: $trialId"
Write-Host " Tratamento : $Tratamento"
Write-Host " Time-box   : $TimeBoxSegundos s"
Write-Host " Edite      : $srcDir"
Write-Host " Enunciado  : $(Join-Path $workspace 'ENUNCIADO.md')"
Write-Host '--------------------------------------------------------------'
if ($Tratamento -eq 'MANUAL') {
    Write-Host ' SEM assistente de IA. Desligue Copilot/Cursor/autocomplete de IA.' -ForegroundColor Yellow
} else {
    Write-Host ' COM Claude (claude.ai). Salve o log da conversa ao final.' -ForegroundColor Cyan
}
Write-Host ' NAO edite nada em test\.'
Write-Host '=============================================================='
Write-Host ''

# --- 2. Cronometragem ---------------------------------------------------------
$inicio = Get-Date
$deadline = $inicio.AddSeconds($TimeBoxSegundos)
$censurado = $true
$timeToGreen = $TimeBoxSegundos
$ultimaAssinatura = ''
$jaRodouAlgumaVez = $false

while ($true) {
    $agora = Get-Date
    if ($agora -ge $deadline) { break }

    # So reexecuta se algo em src\ mudou: durante 35 minutos, rodar a suite em
    # laco cego competiria por CPU com o participante e poluiria a medicao.
    $assinatura = (Get-ChildItem -Recurse -File $srcDir |
                   Sort-Object FullName |
                   ForEach-Object { "$($_.FullName)|$($_.Length)|$($_.LastWriteTimeUtc.Ticks)" }) -join "`n"

    if ($assinatura -ne $ultimaAssinatura -or -not $jaRodouAlgumaVez) {
        $ultimaAssinatura = $assinatura
        $jaRodouAlgumaVez = $true

        & (Join-Path $PSScriptRoot 'run_tests.ps1') -Kata $workspace -ReportsDir $reportsDir -Quiet | Out-Null
        $codigo = $LASTEXITCODE

        if ($codigo -eq 3) {
            Write-Host ''
            Write-Host 'TRIAL ABORTADO: ambiente quebrado (run_tests.ps1 saiu com 3).' -ForegroundColor Red
            Write-Host 'Nenhuma linha foi gravada. Rode .\scripts\setup_ambiente.ps1 e refaca o trial.' -ForegroundColor Red
            exit 3
        }

        if ($codigo -eq 0) {
            $timeToGreen = [int][Math]::Round(((Get-Date) - $inicio).TotalSeconds)
            $censurado = $false
            break
        }
    }

    $restante = [int]($deadline - (Get-Date)).TotalSeconds
    Write-Host ("`r  vermelho - restam {0,5} s" -f $restante) -NoNewline
    if ($restante -le 0) { break }
    Start-Sleep -Seconds ([Math]::Min($IntervaloSegundos, [Math]::Max($restante, 1)))
}
Write-Host ''

$fim = Get-Date

# --- 3. RQ2 a partir do XML ---------------------------------------------------
$junitFile = Join-Path $reportsDir 'junit.xml'
$testesTotal = 0
$testesPassando = 0
if (Test-Path $junitFile) {
    $ts = ([xml](Get-Content $junitFile)).testsuites
    $testesTotal = [int]$ts.tests
    # `errors` entra na conta: o esqueleto lanca Error("TODO"), que o Jest
    # contabiliza como error e nao como failure.
    $testesPassando = $testesTotal - [int]$ts.failures - [int]$ts.errors
}
$taxa = if ($testesTotal -gt 0) { [Math]::Round($testesPassando / $testesTotal, 4) } else { 0 }

# --- 4. Persistencia ----------------------------------------------------------
$junitArquivo = Join-Path $root "data\junit\$trialId.xml"
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $junitArquivo) | Out-Null
if (Test-Path $junitFile) { Copy-Item $junitFile $junitArquivo -Force }

$cabecalho = 'trial_id,integrante,kata,tratamento,ordem,inicio_iso,fim_iso,time_to_green_s,censurado,testes_total,testes_passando,taxa_sucesso,n_prompts,observacoes'
if (-not (Test-Path $CsvPath)) {
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $CsvPath) | Out-Null
    Set-Content -Path $CsvPath -Value $cabecalho -Encoding utf8
}

$linha = @(
    $trialId
    $Integrante
    $Kata
    $Tratamento
    $Ordem
    $inicio.ToString('s')
    $fim.ToString('s')
    $timeToGreen
    $(if ($censurado) { 'true' } else { 'false' })
    $testesTotal
    $testesPassando
    $taxa
    $(if ($Prompts -ge 0) { $Prompts } else { '' })
    ('"' + ($Observacoes -replace '"', '""') + '"')
) -join ','
Add-Content -Path $CsvPath -Value $linha -Encoding utf8

# --- 5. Resumo ----------------------------------------------------------------
Write-Host ''
Write-Host '=============================================================='
if ($censurado) {
    Write-Host " CENSURADO em $TimeBoxSegundos s - time-box atingido" -ForegroundColor Yellow
    Write-Host ' O trial vale: registrado, nunca descartado.'
} else {
    Write-Host " VERDE em $timeToGreen s" -ForegroundColor Green
}
Write-Host " Testes    : $testesPassando/$testesTotal (taxa $taxa)"
Write-Host " Registro  : $CsvPath"
Write-Host " Evidencia : $junitArquivo"
Write-Host " Codigo    : $workspace"
if ($Tratamento -eq 'IA' -and $Prompts -lt 0) {
    Write-Host ' Falta o numero de prompts: preencha a coluna n_prompts no CSV.' -ForegroundColor Yellow
}
Write-Host '=============================================================='

exit 0
