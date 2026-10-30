param(
    [switch]$BuildOnly,
    [string]$Data = '', [string]$GridSizes = '33',
    [ValidateSet('auto','sparse','direct_u8','direct_u16','direct_rgb24')][string]$Mode = 'auto',
    [ValidateSet('auto','scalar','avx2')][string]$Backend = 'auto',
    [ValidateSet('uniform','framework')][string]$Grid = 'uniform',
    [ValidateRange(1,100)][int]$Count = 4,
    [ValidateSet('sample','independent_ls','chain_ls','history')][string]$Fit = 'sample',
    [string]$Preference = '',
    [string]$CandidateSizes = '17;25;33',
    [string]$CandidateModes = 'sparse,direct_rgb24',
    [Nullable[double]]$MaxMeanError = $null,
    [Nullable[double]]$MaxPixelError = $null,
    [Nullable[double]]$MaxMsPerMP = $null,
    [Nullable[double]]$MaxRuntimeMiB = $null,
    [Nullable[double]]$MaxWorkspaceMiB = $null,
    [ValidateRange(3,31)][int]$CalibrationReps = 5,
    [switch]$AllowUnstableTime,
    [string]$SelectionReport = ''
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
        $runArguments = @($relativeData, $GridSizes, $Mode, $Backend, $Grid, [string]$Count, $Fit)
        $preferenceKeys = @('CandidateSizes','CandidateModes','MaxMeanError','MaxPixelError','MaxMsPerMP','MaxRuntimeMiB','MaxWorkspaceMiB','CalibrationReps','AllowUnstableTime','SelectionReport')
        if (-not $Preference) {
            foreach ($key in $preferenceKeys) {
                if ($PSBoundParameters.ContainsKey($key)) { throw "-$key 须与-Preference同时使用" }
            }
        } else {
            $runArguments += @('--preference', $Preference, '--candidate-sizes', $CandidateSizes, '--candidate-modes', $CandidateModes, '--calibration-reps', [string]$CalibrationReps)
            $budgets = @{'--max-mean-error'=$MaxMeanError; '--max-pixel-error'=$MaxPixelError; '--max-ms-per-mp'=$MaxMsPerMP; '--max-runtime-mib'=$MaxRuntimeMiB; '--max-workspace-mib'=$MaxWorkspaceMiB}
            foreach ($key in $budgets.Keys) {
                if ($null -ne $budgets[$key]) { $runArguments += @($key, ([double]$budgets[$key]).ToString('R', [System.Globalization.CultureInfo]::InvariantCulture)) }
            }
            if ($AllowUnstableTime) { $runArguments += '--allow-unstable-time' }
            if ($SelectionReport) { $runArguments += @('--selection-report', $SelectionReport) }
        }
        & '.\main_flash_chroma.exe' @runArguments
        if ($LASTEXITCODE -ne 0) { throw "框架执行失败：$LASTEXITCODE" }
    }
} finally { $env:PATH = $oldPath; Pop-Location }
