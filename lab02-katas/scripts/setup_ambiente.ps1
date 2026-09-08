<#
    setup_ambiente.ps1 - prepara a maquina de um integrante para os trials do Lab02.

    Uso:
        .\scripts\setup_ambiente.ps1

    Instala as dependencias fixadas no package-lock.json e confere as versoes.
    Versoes identicas nas tres maquinas: ameaca a validade #8 (instrumentacao),
    ver docs\desenho-experimento.md.
#>
$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $PSScriptRoot
Push-Location $root
try {
    Write-Host '== Ambiente =='
    Write-Host ('node : ' + (& node -v))
    Write-Host ('npm  : ' + (& npm -v))

    Write-Host ''
    Write-Host '== Instalando dependencias =='
    if (Test-Path (Join-Path $root 'package-lock.json')) {
        & npm ci --no-audit --no-fund
    } else {
        & npm install --no-audit --no-fund
    }
    if ($LASTEXITCODE -ne 0) { Write-Error 'Falha ao instalar dependencias.' }

    Write-Host ''
    Write-Host '== Ferramentas =='
    foreach ($pacote in @('jest', 'ts-jest', 'jest-junit', 'jscpd', 'eslint', 'typescript')) {
        $pkg = Join-Path $root "node_modules\$pacote\package.json"
        if (Test-Path $pkg) {
            $versao = (Get-Content $pkg -Raw | ConvertFrom-Json).version
            Write-Host ("{0,-12} {1}" -f $pacote, $versao)
        } else {
            Write-Host ("{0,-12} AUSENTE" -f $pacote)
        }
    }

    Write-Host ''
    Write-Host 'Pronto. Teste com:'
    Write-Host '  .\scripts\run_tests.ps1 -Kata katas\kata-01-faixas'
}
finally {
    Pop-Location
}
