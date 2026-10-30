param([ValidateRange(0, 65535)][int]$Port = 8765, [switch]$NoBrowser)
$ErrorActionPreference = 'Stop'
$projectRoot = [IO.Path]::GetFullPath($PSScriptRoot)
$taskDirectory = Join-Path $projectRoot 'artifacts/gui-jobs'
$serverScript = Join-Path $projectRoot 'gui/server.py'
New-Item -ItemType Directory -Force -Path $taskDirectory | Out-Null
$serviceRecord = Join-Path $taskDirectory 'server.json'

function Get-StudioPrimaryRoot {
    try {
        $commonDirectory = (& git -C $projectRoot rev-parse --path-format=absolute --git-common-dir 2>$null | Select-Object -First 1)
        if ($LASTEXITCODE -eq 0 -and $commonDirectory) {
            return [IO.Path]::GetDirectoryName([IO.Path]::GetFullPath([string]$commonDirectory))
        }
    } catch { }
    return $projectRoot
}

$primaryRoot = Get-StudioPrimaryRoot
$sourceHashes = @{}
foreach ($source in @('server.py', 'studio.py', 'studio_catalog.json')) {
    $path = Join-Path (Join-Path $projectRoot 'gui') $source
    if (Test-Path -LiteralPath $path -PathType Leaf) {
        $sourceHashes[$source] = (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()
    }
}

$libraryCandidates = @()
if ($env:FLASH_CHROMA_LIBRARY) {
    $libraryPath = if ([IO.Path]::IsPathRooted($env:FLASH_CHROMA_LIBRARY)) {
        [IO.Path]::GetFullPath($env:FLASH_CHROMA_LIBRARY)
    } else { [IO.Path]::GetFullPath((Join-Path $projectRoot $env:FLASH_CHROMA_LIBRARY)) }
    if (-not (Test-Path -LiteralPath $libraryPath -PathType Leaf)) {
        throw "FLASH_CHROMA_LIBRARY 指定的运行库不存在：$libraryPath"
    }
    $libraryCandidates += $libraryPath
} else {
    foreach ($root in @($projectRoot, $primaryRoot) | Select-Object -Unique) {
        foreach ($relative in @('artifacts/single-header-perf-build/libflash_chroma_bridge.dll',
                                'build-single-header/libflash_chroma_bridge.dll',
                                'build-single-header/libflash_chroma_bridge.so',
                                'artifacts/single-header-build/libflash_chroma_bridge.dll')) {
            $path = Join-Path $root $relative
            if (Test-Path -LiteralPath $path -PathType Leaf) { $libraryCandidates += [IO.Path]::GetFullPath($path) }
        }
    }
}
if (-not $libraryCandidates.Count) {
    throw '未找到单头文件原生库。请先构建 single_header，或设置 FLASH_CHROMA_LIBRARY 为当前 DLL 的完整路径。'
}
$libraryPath = @($libraryCandidates | Select-Object -Unique)[0]
$libraryHash = (Get-FileHash -LiteralPath $libraryPath -Algorithm SHA256).Hash.ToLowerInvariant()

function Test-CurrentStudioService($service, $health) {
    if ($service.root -ne $projectRoot -or $health.root -ne $projectRoot -or $health.status -ne 'ready') { return $false }
    if ($health.application -ne 'flash-chroma-studio' -or $health.api_version -ne 1 -or $health.studio_api_version -ne 1) { return $false }
    if (-not $health.engine.available -or $health.engine.library_sha256 -ne $libraryHash) { return $false }
    foreach ($pair in @(@('server.py', 'server_source_sha256'), @('studio.py', 'studio_source_sha256'),
                         @('studio_catalog.json', 'studio_catalog_sha256'))) {
        if ($sourceHashes.ContainsKey($pair[0]) -and $health.($pair[1]) -ne $sourceHashes[$pair[0]]) { return $false }
    }
    return $true
}

function Test-StudioLoopbackUrl([string]$url) {
    try {
        $value = [Uri]$url
        return $value.Scheme -eq 'http' -and $value.Host -in @('127.0.0.1', 'localhost') -and $value.AbsolutePath -eq '/' -and -not $value.UserInfo
    } catch { return $false }
}

if (Test-Path -LiteralPath $serviceRecord) {
    try {
        $existingService = Get-Content -LiteralPath $serviceRecord -Raw | ConvertFrom-Json
        if (-not (Test-StudioLoopbackUrl $existingService.url)) { throw '服务记录不是本机HTTP地址' }
        $health = Invoke-RestMethod -Uri ($existingService.url + 'api/health') -TimeoutSec 2
        if (Test-CurrentStudioService $existingService $health) {
            if (-not $NoBrowser) { Start-Process $existingService.url }
            Write-Output "Flash Chroma Studio 已在运行：$($existingService.url)"
            return
        }
    } catch { }
}

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
        $path = Join-Path $root "artifacts/$environment/Scripts/python.exe"
        if (Test-Path -LiteralPath $path -PathType Leaf) { $pythonCandidates += $path }
    }
}
try { $pythonCandidates += (Get-Command python -ErrorAction Stop).Source } catch { }
$probeCode = @'
import json, sys
from pathlib import Path
import numpy, PIL
sys.path.insert(0, str(Path(sys.argv[1]) / "scripts"))
import flash_chroma_support
library = flash_chroma_support.Library(Path(sys.argv[2]))
print(json.dumps({"python": sys.version.split()[0], "numpy": numpy.__version__, "pillow": PIL.__version__, "library_sha256": library.sha256}))
'@
$pythonExecutable = $null
$probeFailures = @()
foreach ($candidate in $pythonCandidates | Select-Object -Unique) {
    try {
        $probeOutput = & $candidate '-X' 'utf8' '-c' $probeCode $projectRoot $libraryPath 2>&1
        if ($LASTEXITCODE -ne 0) { throw (($probeOutput | Select-Object -Last 3) -join ' ') }
        $probe = ($probeOutput | Select-Object -Last 1) | ConvertFrom-Json
        if ($probe.library_sha256 -ne $libraryHash) { throw '运行库摘要与选择的文件不同' }
        $pythonExecutable = $candidate
        break
    } catch { $probeFailures += "${candidate}：$($_.Exception.Message)" }
}
if (-not $pythonExecutable) {
    throw ("没有找到能够导入 NumPy/Pillow 并加载当前原生库的 Python。`n" + ($probeFailures -join "`n"))
}

$launchStamp = Get-Date -Format 'yyyyMMdd-HHmmss-fff'
$arguments = @('-X', 'utf8', ('"' + $serverScript + '"'), '--port', [string]$Port,
               '--studio-library', ('"' + $libraryPath + '"'))
if (-not $NoBrowser) { $arguments += '--open' }
$process = Start-Process -FilePath $pythonExecutable -ArgumentList $arguments -WorkingDirectory $projectRoot -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $taskDirectory "$launchStamp-server.log") -RedirectStandardError (Join-Path $taskDirectory "$launchStamp-server-error.log")
for ($attempt = 0; $attempt -lt 120; $attempt++) {
    try {
        $readyService = Get-Content -LiteralPath $serviceRecord -Raw | ConvertFrom-Json
        if (-not (Test-StudioLoopbackUrl $readyService.url)) { throw '服务记录不是本机HTTP地址' }
        $readyHealth = Invoke-RestMethod -Uri ($readyService.url + 'api/health') -TimeoutSec 1
        if (Test-CurrentStudioService $readyService $readyHealth) {
            Write-Output "Flash Chroma Studio 已启动（PID $($readyService.pid)，Python $($probe.python)）：$($readyService.url)"
            return
        }
    } catch { }
    $process.Refresh()
    if ($process.HasExited) { throw "服务启动失败，请查看 artifacts/gui-jobs/$launchStamp-server-error.log" }
    Start-Sleep -Milliseconds 100
}
throw '服务初始化尚未完成或版本不一致，请查看 artifacts/gui-jobs 下本次启动日志。'
