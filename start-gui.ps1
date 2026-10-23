param([int]$Port = 8765, [switch]$NoBrowser)
$ErrorActionPreference = 'Stop'
$projectRoot = $PSScriptRoot
$taskDirectory = Join-Path $projectRoot 'artifacts/gui-jobs'
New-Item -ItemType Directory -Force -Path $taskDirectory | Out-Null
$serviceRecord = Join-Path $taskDirectory 'server.json'
if (Test-Path -LiteralPath $serviceRecord) {
    try {
        $existingService = Get-Content -LiteralPath $serviceRecord -Raw | ConvertFrom-Json
        $health = Invoke-RestMethod -Uri ($existingService.url + 'api/health') -TimeoutSec 2
        if ($health.root -eq $projectRoot -and $health.status -eq 'ready') {
            if (-not $NoBrowser) { Start-Process $existingService.url }
            Write-Output "Flash Chroma 已在运行：$($existingService.url)"
            return
        }
    } catch { }
}
$preferredPython = Join-Path $projectRoot 'artifacts/camera-raw-env-v1/Scripts/python.exe'
$pythonExecutable = if (Test-Path -LiteralPath $preferredPython) { $preferredPython } else { (Get-Command python -ErrorAction Stop).Source }
$serverScript = Join-Path $projectRoot 'gui/server.py'
$launchStamp = Get-Date -Format 'yyyyMMdd-HHmmss-fff'
$arguments = @('-X', 'utf8', ('"' + $serverScript + '"'), '--port', [string]$Port)
if (-not $NoBrowser) { $arguments += '--open' }
$process = Start-Process -FilePath $pythonExecutable -ArgumentList $arguments -WorkingDirectory $projectRoot -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $taskDirectory "$launchStamp-server.log") -RedirectStandardError (Join-Path $taskDirectory "$launchStamp-server-error.log")
for ($attempt = 0; $attempt -lt 60; $attempt++) {
    $process.Refresh()
    if ($process.HasExited) { throw "服务启动失败，请查看 artifacts/gui-jobs/$launchStamp-server-error.log" }
    try {
        $readyService = Get-Content -LiteralPath $serviceRecord -Raw | ConvertFrom-Json
        if ($readyService.root -eq $projectRoot) {
            $readyHealth = Invoke-RestMethod -Uri ($readyService.url + 'api/health') -TimeoutSec 1
            if ($readyHealth.status -eq 'ready') {
                Write-Output "Flash Chroma 已启动（PID $($readyService.pid)）：$($readyService.url)"
                return
            }
        }
    } catch { }
    Start-Sleep -Milliseconds 100
}
throw '服务初始化尚未完成，请查看 artifacts/gui-jobs 下本次启动日志。'
