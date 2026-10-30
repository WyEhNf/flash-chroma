param(
    [switch]$BuildOnly,
    [string]$Data = '', [string]$GridSizes = '33',
    [ValidateSet('auto','sparse','direct_u8','direct_u16','direct_rgb24')][string]$Mode = 'auto',
    [ValidateSet('auto','scalar','avx2')][string]$Backend = 'auto',
    [ValidateSet('uniform','framework')][string]$Grid = 'uniform',
    [ValidateRange(1,100)][int]$Count = 4,
    [ValidateSet('sample','independent_ls','chain_ls')][string]$Fit = 'sample'
)
$ErrorActionPreference = 'Stop'
$config = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'build-config.json') -Raw | ConvertFrom-Json
if (-not $Data) { $Data = Join-Path $config.framework 'data' }
$compiler = $env:FLASH_CHROMA_CXX
if (-not $compiler -and $config.compiler -and (Test-Path -LiteralPath $config.compiler -PathType Leaf)) { $compiler = $config.compiler }
if (-not $compiler) { $compiler = (Get-Command g++ -ErrorAction Stop).Source }
$oldPath = $env:PATH
Push-Location -LiteralPath $PSScriptRoot
try {
    $env:PATH = (Split-Path -Parent $compiler) + ';' + $env:PATH
    & $compiler --version | Select-Object -First 1
    & $compiler '-O3' '-DNDEBUG' '-std=c++17' '-Wall' '-Wextra' '-static' '-DFLASH_CHROMA_ENABLE_OPENMP=0' 'main.cpp' '-o' 'main_flash_chroma.exe'
    if ($LASTEXITCODE -ne 0) { throw '编译失败，未运行旧程序。' }
    if (-not $BuildOnly) {
        $relativeData = Resolve-Path -LiteralPath $Data -Relative
        & '.\main_flash_chroma.exe' $relativeData $GridSizes $Mode $Backend $Grid $Count $Fit
        if ($LASTEXITCODE -ne 0) { throw "框架执行失败：$LASTEXITCODE" }
    }
} finally { $env:PATH = $oldPath; Pop-Location }
