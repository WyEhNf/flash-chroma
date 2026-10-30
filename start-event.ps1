param(
    [ValidateSet('studio', 'doctor', 'init', 'fit', 'run')][string]$Mode = 'doctor',
    [string]$Config = (Join-Path $PSScriptRoot 'event-config.json'),
    [string]$Output,
    [string]$Library,
    [string]$Manifest,
    [string]$Images,
    [string]$ImageRoot,
    [Alias('Profile')][string]$ModelProfile,
    [int]$Limit,
    [double]$Threshold,
    [ValidateRange(0, 65535)][int]$Port = 8765,
    [switch]$NoBrowser
)
$ErrorActionPreference = 'Stop'
$projectRoot = [IO.Path]::GetFullPath($PSScriptRoot)

function Resolve-EventPath([string]$value) {
    if ([string]::IsNullOrWhiteSpace($value)) { throw '路径不能为空。' }
    if ([IO.Path]::IsPathRooted($value)) { return [IO.Path]::GetFullPath($value) }
    return [IO.Path]::GetFullPath((Join-Path (Get-Location) $value))
}

# Studio沿用同一隐藏后台服务和源码/原生库身份核对，不创建第二套服务器。
if ($Mode -eq 'studio') {
    $oldLibrary = $env:FLASH_CHROMA_LIBRARY
    try {
        if ($Library) { $env:FLASH_CHROMA_LIBRARY = Resolve-EventPath $Library }
        & (Join-Path $projectRoot 'start-gui.ps1') -Port $Port -NoBrowser:$NoBrowser
    } finally { $env:FLASH_CHROMA_LIBRARY = $oldLibrary }
    return
}

foreach ($name in @('Port', 'NoBrowser')) {
    if ($PSBoundParameters.ContainsKey($name)) { throw "-$name 仅用于 -Mode studio。" }
}
foreach ($name in @('Manifest', 'Images', 'ImageRoot')) {
    if ($PSBoundParameters.ContainsKey($name) -and $Mode -ne 'init') {
        throw "-$name 仅用于 -Mode init；正式输入请修改 -Config 指定的配置文件。"
    }
}
if ($ModelProfile -and $Mode -notin @('init', 'run')) { throw '-Profile 仅用于 init 或 run。' }
foreach ($name in @('Limit', 'Threshold')) {
    if ($PSBoundParameters.ContainsKey($name) -and $Mode -ne 'run') { throw "-$name 仅用于 -Mode run。" }
}
if ($PSBoundParameters.ContainsKey('Limit') -and $Limit -lt 1) { throw '-Limit 必须大于0；不提供此参数时处理完整图片列表。' }
if ($PSBoundParameters.ContainsKey('Threshold') -and ([double]::IsNaN($Threshold) -or [double]::IsInfinity($Threshold) -or $Threshold -le 0)) {
    throw '-Threshold 必须是大于0的有限数值。'
}
if ($Mode -in @('fit', 'run') -and [string]::IsNullOrWhiteSpace($Output)) {
    throw 'fit/run必须通过 -Output 指定一个新的输出目录，已有结果不会覆盖。'
}
$eventScript = Join-Path $projectRoot 'scripts/p16_event.py'
if (-not (Test-Path -LiteralPath $eventScript -PathType Leaf)) { throw '缺少 scripts/p16_event.py，请先同步完整的赛前工具版本。' }

$primaryRoot = $projectRoot
try {
    $commonDirectory = (& git -C $projectRoot rev-parse --path-format=absolute --git-common-dir 2>$null | Select-Object -First 1)
    if ($LASTEXITCODE -eq 0 -and $commonDirectory) {
        $primaryRoot = [IO.Path]::GetDirectoryName([IO.Path]::GetFullPath([string]$commonDirectory))
    }
} catch { }
$pythonCandidates = @()
# 离线同机包可显式复用已经安装依赖的Python；此候选在共享环境与PATH之前。
if ($env:FLASH_CHROMA_PYTHON) {
    $explicitPython = if ([IO.Path]::IsPathRooted($env:FLASH_CHROMA_PYTHON)) {
        [IO.Path]::GetFullPath($env:FLASH_CHROMA_PYTHON)
    } else { [IO.Path]::GetFullPath((Join-Path $projectRoot $env:FLASH_CHROMA_PYTHON)) }
    if (-not (Test-Path -LiteralPath $explicitPython -PathType Leaf)) {
        throw "FLASH_CHROMA_PYTHON指定的Python不存在：$explicitPython"
    }
    $pythonCandidates += $explicitPython
}
foreach ($environment in @('error-study-py312', 'camera-raw-env-v1')) {
    foreach ($root in @($projectRoot, $primaryRoot) | Select-Object -Unique) {
        $candidate = Join-Path $root "artifacts/$environment/Scripts/python.exe"
        if (Test-Path -LiteralPath $candidate -PathType Leaf) { $pythonCandidates += $candidate }
    }
}
try { $pythonCandidates += (Get-Command python -ErrorAction Stop).Source } catch { }
$pythonExecutable = $null
$failures = @()
foreach ($candidate in $pythonCandidates | Select-Object -Unique) {
    try {
        $probe = & $candidate '-X' 'utf8' '-c' 'import sys, numpy, PIL; print(sys.executable)' 2>&1
        if ($LASTEXITCODE -ne 0) { throw (($probe | Select-Object -Last 2) -join ' ') }
        $pythonExecutable = $candidate
        break
    } catch { $failures += "${candidate}：$($_.Exception.Message)" }
}
if (-not $pythonExecutable) {
    throw ("没有找到能够导入NumPy/Pillow的Python；请先安装项目依赖。`n" + ($failures -join "`n"))
}

$eventArguments = @('-X', 'utf8', $eventScript, $Mode)
if ($Mode -eq 'init') {
    # init生成配置JSON；未指定Output时，生成到Config路径。不会自动填充Cinema输入。
    $destination = if ($Output) { Resolve-EventPath $Output } else { Resolve-EventPath $Config }
    $eventArguments += @('--output', $destination)
    if ($Manifest) { $eventArguments += @('--manifest', (Resolve-EventPath $Manifest)) }
    if ($Images) { $eventArguments += @('--images', (Resolve-EventPath $Images)) }
    if ($ImageRoot) { $eventArguments += @('--image-root', (Resolve-EventPath $ImageRoot)) }
} else {
    $eventArguments += @('--config', (Resolve-EventPath $Config))
    if ($Output) { $eventArguments += @('--output', (Resolve-EventPath $Output)) }
}
# 只有明确给定Library才覆盖配置；其余交给CLI核对配置库或探测同版单头库。
if ($Library) { $eventArguments += @('--library', (Resolve-EventPath $Library)) }
if ($ModelProfile) { $eventArguments += @('--profile', $ModelProfile) }
if ($PSBoundParameters.ContainsKey('Limit')) { $eventArguments += @('--limit', [string]$Limit) }
if ($PSBoundParameters.ContainsKey('Threshold')) {
    $eventArguments += @('--threshold', $Threshold.ToString('R', [Globalization.CultureInfo]::InvariantCulture))
}
& $pythonExecutable @eventArguments
exit $LASTEXITCODE
