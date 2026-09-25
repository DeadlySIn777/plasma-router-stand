$ErrorActionPreference = 'Stop'
$controlRoot = $PSScriptRoot
$env:PLATFORMIO_CORE_DIR = Join-Path $controlRoot '.platformio'
$python = Join-Path $controlRoot '.venv/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $python)) {
    throw 'Create the workspace Python 3.12 venv and install PlatformIO 6.2.0 first; see README.md.'
}
Push-Location (Join-Path $controlRoot 'grblhal-h7')
try {
    & $python -m platformio run -c kraken.ini -e kraken_v11_hybrid 2>&1 | Tee-Object -FilePath (Join-Path $controlRoot 'build-hybrid.log')
    if ($LASTEXITCODE -ne 0) { throw "Firmware build failed: $LASTEXITCODE" }
    & $python (Join-Path $controlRoot 'verify_port.py')
    if ($LASTEXITCODE -ne 0) { throw "Static/image verification failed: $LASTEXITCODE" }
} finally { Pop-Location }
