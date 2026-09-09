<#
    run_metrics.ps1 - metricas estaticas da RQ3 (Issue #27).

    Mede, sobre o codigo final de cada trial:
      - complexidade ciclomatica de McCabe  (ESLint, regra `complexity`)
      - duplicacao de codigo                (jscpd)
      - LOC                                 (metrica de CONTROLE, obrigatoria)

    Uso:
        .\scripts\run_metrics.ps1 -Trial trials\p1\kata-01-faixas-ia
        .\scripts\run_metrics.ps1 -Todos
        .\scripts\run_metrics.ps1 -Trial katas\kata-01-faixas       # qualquer pasta com src\

    Por que nao CK nem PMD: o CK so analisa Java e a linguagem fixada foi
    TypeScript; o enunciado admite ferramenta equivalente nesse caso. Ver
    docs\desenho-experimento.md, secao "Ferramentas da RQ3".

    Saidas (dicionario das colunas no README.md):
        data\metrics.csv                      uma linha por trial
        data\metrics_duplicacao_pool.csv      duplicacao por (kata, tratamento)
#>
[CmdletBinding(DefaultParameterSetName = 'Um')]
param(
    [Parameter(Mandatory = $true, ParameterSetName = 'Um')][string]$Trial,
    [Parameter(Mandatory = $true, ParameterSetName = 'Todos')][switch]$Todos,
    [string]$CsvPath,
    [string]$CsvPoolPath,
    [switch]$Quiet
)

$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $PSScriptRoot
if (-not $CsvPath)     { $CsvPath     = Join-Path $root 'data\metrics.csv' }
if (-not $CsvPoolPath) { $CsvPoolPath = Join-Path $root 'data\metrics_duplicacao_pool.csv' }

$CABECALHO = 'trial_id,integrante,kata,tratamento,arquivos,loc,n_funcoes,cc_max,cc_soma,cc_media,cc_max_por_loc,cc_soma_por_loc,linhas_analisadas,linhas_duplicadas,pct_duplicado'
$CABECALHO_POOL = 'kata,tratamento,n_trials,linhas_analisadas,linhas_duplicadas,pct_duplicado,clones'

if (-not (Test-Path (Join-Path $root 'node_modules'))) {
    Write-Error "Dependencias ausentes. Rode .\scripts\setup_ambiente.ps1 primeiro."
}

# ------------------------------------------------------------------------------
# Escrita sem BOM.
# No PowerShell 5.1, Set-Content -Encoding utf8 e Out-File -Encoding utf8 SEMPRE
# gravam BOM. Um CSV com BOM faz o pandas ler a primeira coluna como
# "﻿trial_id", e o dashboard da S03 quebra com um KeyError obscuro.
# ------------------------------------------------------------------------------
function Num {
    # Formata numero com PONTO decimal, independente do locale da maquina.
    # Em pt-BR, "$([Math]::Round(0.5,4))" vira "0,5" e a virgula quebra o CSV
    # em colunas extras -- corrompendo silenciosamente o dataset.
    param($Valor)
    return [System.Convert]::ToDouble($Valor).ToString([System.Globalization.CultureInfo]::InvariantCulture)
}

function Escreve-LinhaCsv {
    param([string]$Caminho, [string]$Cabecalho, [string]$Linha)

    $utf8SemBom = New-Object System.Text.UTF8Encoding $false
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $Caminho) | Out-Null
    if (-not (Test-Path $Caminho)) {
        [System.IO.File]::WriteAllLines($Caminho, [string[]]@($Cabecalho, $Linha), $utf8SemBom)
    } else {
        [System.IO.File]::AppendAllLines($Caminho, [string[]]@($Linha), $utf8SemBom)
    }
}

# ------------------------------------------------------------------------------
# LOC - linhas nao vazias e nao comentadas. Mesma definicao usada na calibracao
# das katas (docs\katas.md), para os numeros serem comparaveis.
# ------------------------------------------------------------------------------
function Conta-Loc {
    param([string[]]$Arquivos)

    $total = 0
    foreach ($arq in $Arquivos) {
        foreach ($linha in (Get-Content -LiteralPath $arq)) {
            if ($linha.Trim() -eq '') { continue }
            if ($linha -match '^\s*(//|/\*|\*)') { continue }
            $total++
        }
    }
    return $total
}

# ------------------------------------------------------------------------------
# Complexidade ciclomatica por funcao, via regra `complexity` do ESLint.
# O limite 0 no eslint.complexity.config.mjs faz TODA funcao violar a regra e,
# portanto, aparecer no relatorio com o seu valor.
# ------------------------------------------------------------------------------
function Mede-Complexidade {
    param([string]$SrcDir)

    $config = Join-Path $root 'eslint.complexity.config.mjs'
    Push-Location $root
    try {
        $saida = & npx eslint --config $config --no-config-lookup --format json "$SrcDir/**/*.ts"
    }
    finally {
        Pop-Location
    }

    $relatorio = ($saida -join "`n") | ConvertFrom-Json
    $valores = @()
    foreach ($arquivo in $relatorio) {
        foreach ($msg in $arquivo.messages) {
            if ($msg.message -match 'complexity of (\d+)') {
                $valores += [int]$Matches[1]
            }
        }
    }

    if ($valores.Count -eq 0) {
        return [pscustomobject]@{ NFuncoes = 0; Max = 0; Soma = 0; Media = 0 }
    }
    $soma = ($valores | Measure-Object -Sum).Sum
    return [pscustomobject]@{
        NFuncoes = $valores.Count
        Max      = ($valores | Measure-Object -Maximum).Maximum
        Soma     = $soma
        Media    = [Math]::Round($soma / $valores.Count, 2)
    }
}

# ------------------------------------------------------------------------------
# Duplicacao via jscpd. Flags explicitas para a medicao nao depender do que
# estiver no .jscpd.json.
# ------------------------------------------------------------------------------
function Mede-Duplicacao {
    param([string]$Alvo)

    $saidaDir = Join-Path $env:TEMP ("jscpd-" + [Guid]::NewGuid().ToString('N'))
    # Barra normal: o jscpd trata o caminho como glob, e a barra invertida do
    # Windows vira escape -- o resultado e "0 arquivos analisados", em silencio.
    $alvoGlob = $Alvo -replace '\\', '/'
    try {
        Push-Location $root
        try {
            & npx jscpd $alvoGlob --min-tokens 25 --min-lines 3 --format typescript `
                --reporters json --output $saidaDir --silent | Out-Null
        }
        finally {
            Pop-Location
        }

        $arquivoJson = Join-Path $saidaDir 'jscpd-report.json'
        if (-not (Test-Path $arquivoJson)) {
            return [pscustomobject]@{ Linhas = 0; Duplicadas = 0; Percentual = 0; Clones = 0 }
        }
        $total = (Get-Content -Raw $arquivoJson | ConvertFrom-Json).statistics.total
        return [pscustomobject]@{
            Linhas     = [int]$total.lines
            Duplicadas = [int]$total.duplicatedLines
            Percentual = [Math]::Round([double]$total.percentage, 2)
            Clones     = [int]$total.clones
        }
    }
    finally {
        Remove-Item -Recurse -Force $saidaDir -ErrorAction SilentlyContinue
    }
}

# ------------------------------------------------------------------------------
# trials\<integrante>\<kata>-<tratamento>\  ->  mesma chave do data\trials.csv,
# para a S03 juntar os dois CSVs num merge por trial_id.
# ------------------------------------------------------------------------------
function Interpreta-Caminho {
    param([string]$Dir)

    $nome = Split-Path -Leaf $Dir
    $pai = Split-Path -Leaf (Split-Path -Parent $Dir)

    if ($nome -match '^(?<kata>.+)-(?<trat>ia|manual)$') {
        return [pscustomobject]@{
            TrialId     = "$pai-$($Matches['kata'])-$($Matches['trat'])"
            Integrante  = $pai
            Kata        = $Matches['kata']
            Tratamento  = $Matches['trat'].ToUpper()
        }
    }
    # Pasta fora do padrao de trial (uma kata, por exemplo): mede assim mesmo,
    # sem inventar integrante nem tratamento.
    return [pscustomobject]@{ TrialId = $nome; Integrante = ''; Kata = $nome; Tratamento = '' }
}

function Mede-Trial {
    param([string]$Dir)

    $srcDir = Join-Path $Dir 'src'
    if (-not (Test-Path $srcDir)) {
        Write-Warning "sem src\, ignorando: $Dir"
        return $null
    }
    $arquivos = @(Get-ChildItem -Recurse -File -Filter *.ts $srcDir | ForEach-Object { $_.FullName })
    if ($arquivos.Count -eq 0) {
        Write-Warning "nenhum .ts em src\, ignorando: $Dir"
        return $null
    }

    $id = Interpreta-Caminho -Dir $Dir
    $loc = Conta-Loc -Arquivos $arquivos
    $cc = Mede-Complexidade -SrcDir ($srcDir -replace '\\', '/')
    $dup = Mede-Duplicacao -Alvo $srcDir

    $ccMaxPorLoc  = if ($loc -gt 0) { [Math]::Round($cc.Max / $loc, 4) } else { 0 }
    $ccSomaPorLoc = if ($loc -gt 0) { [Math]::Round($cc.Soma / $loc, 4) } else { 0 }

    $linha = @(
        $id.TrialId, $id.Integrante, $id.Kata, $id.Tratamento,
        $arquivos.Count, $loc,
        $cc.NFuncoes, $cc.Max, $cc.Soma, (Num $cc.Media),
        (Num $ccMaxPorLoc), (Num $ccSomaPorLoc),
        $dup.Linhas, $dup.Duplicadas, (Num $dup.Percentual)
    ) -join ','

    Escreve-LinhaCsv -Caminho $CsvPath -Cabecalho $CABECALHO -Linha $linha

    if (-not $Quiet) {
        Write-Host ("  {0,-34} loc={1,-4} cc_max={2,-3} cc_soma={3,-3} funcoes={4,-3} dup={5}%" -f `
            $id.TrialId, $loc, $cc.Max, $cc.Soma, $cc.NFuncoes, $dup.Percentual)
    }
    return [pscustomobject]@{ Dir = $Dir; Id = $id }
}

# ------------------------------------------------------------------------------
# Duplicacao por pool (kata, tratamento) - metrica EXPLORATORIA.
# Numa kata de ~25 linhas, o jscpd por arquivo isolado da 0% em quase todo
# trial. Comparar as solucoes dos tres integrantes da mesma (kata, tratamento)
# responde outra pergunta, e essa tem sinal: o assistente entrega praticamente
# a mesma solucao para todo mundo?
# ------------------------------------------------------------------------------
function Mede-Pools {
    param([object[]]$Medidos)

    $grupos = $Medidos |
        Where-Object { $_.Id.Tratamento -ne '' } |
        Group-Object { "$($_.Id.Kata)|$($_.Id.Tratamento)" }

    foreach ($grupo in $grupos) {
        $kata, $trat = $grupo.Name -split '\|'
        $tmp = Join-Path $env:TEMP ("pool-" + [Guid]::NewGuid().ToString('N'))
        New-Item -ItemType Directory -Force -Path $tmp | Out-Null
        try {
            foreach ($item in $grupo.Group) {
                $destino = Join-Path $tmp $item.Id.Integrante
                New-Item -ItemType Directory -Force -Path $destino | Out-Null
                Copy-Item -Recurse (Join-Path $item.Dir 'src\*') $destino
            }
            $dup = Mede-Duplicacao -Alvo $tmp
            $linha = @($kata, $trat, $grupo.Count, $dup.Linhas, $dup.Duplicadas, (Num $dup.Percentual), $dup.Clones) -join ','
            Escreve-LinhaCsv -Caminho $CsvPoolPath -Cabecalho $CABECALHO_POOL -Linha $linha
            if (-not $Quiet) {
                Write-Host ("  pool {0,-24} {1,-7} trials={2} dup={3}% clones={4}" -f `
                    $kata, $trat, $grupo.Count, $dup.Percentual, $dup.Clones)
            }
        }
        finally {
            Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue
        }
    }
}

# ------------------------------------------------------------------------------
# Execucao
# ------------------------------------------------------------------------------
if (-not $Quiet) { Write-Host '' ; Write-Host 'Metricas estaticas da RQ3' ; Write-Host '' }

$medidos = @()
if ($Todos) {
    $dirTrials = Join-Path $root 'trials'
    $candidatos = @(Get-ChildItem -Directory $dirTrials -ErrorAction SilentlyContinue |
                    ForEach-Object { Get-ChildItem -Directory $_.FullName })
    if ($candidatos.Count -eq 0) {
        Write-Warning "Nenhum trial em $dirTrials. Rode os trials com .\scripts\run_trial.ps1 antes."
        exit 0
    }
    foreach ($c in $candidatos) {
        $r = Mede-Trial -Dir $c.FullName
        if ($null -ne $r) { $medidos += $r }
    }
    if (-not $Quiet) { Write-Host '' }
    Mede-Pools -Medidos $medidos
} else {
    if (-not (Test-Path $Trial)) { Write-Error "Pasta nao encontrada: $Trial" }
    $r = Mede-Trial -Dir (Resolve-Path $Trial).Path
    if ($null -eq $r) { exit 1 }
    $medidos += $r
}

if (-not $Quiet) {
    Write-Host ''
    Write-Host "Registro : $CsvPath"
    if ($Todos) { Write-Host "Pool     : $CsvPoolPath" }
}

exit 0
