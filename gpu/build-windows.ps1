param(
    [string]$OutputDirectory = "build-gpu",
    [int]$Architecture = 120
)
$ErrorActionPreference = "Stop"
$projectRoot = Split-Path $PSScriptRoot -Parent
$destination = [System.IO.Path]::GetFullPath((Join-Path $projectRoot $OutputDirectory))
New-Item -ItemType Directory -Path $destination -Force | Out-Null
$vswhere = "${env:ProgramFiles(x86)}/Microsoft Visual Studio/Installer/vswhere.exe"
if (-not (Test-Path -LiteralPath $vswhere)) { throw "Visual Studio locator was not found" }
$visualStudio = & $vswhere -latest -products '*' -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath
if (-not $visualStudio) { throw "MSVC x64 build tools were not found" }
$vcvars = Join-Path $visualStudio "VC/Auxiliary/Build/vcvars64.bat"
$cudaRoot = $env:CUDA_PATH
if (-not $cudaRoot) { $cudaRoot = "C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v13.2" }
$nvcc = Join-Path $cudaRoot "bin/nvcc.exe"
if (-not (Test-Path -LiteralPath $nvcc)) { throw "nvcc was not found: $nvcc" }
$source = Join-Path $PSScriptRoot "main.cu"
$includes = Join-Path $projectRoot "cpp/third_party"
$publicIncludes = Join-Path $projectRoot "cpp/include"
$executable = Join-Path $destination "jshc_gpu.exe"
# Native cubin only: the installed driver need not JIT newer Toolkit PTX.
$command = 'call "' + $vcvars + '" && "' + $nvcc + '" -O3 -std=c++17 --generate-code=arch=compute_' + $Architecture + ',code=sm_' + $Architecture + ' --cudart=static -Xcompiler "/O2,/MT,/EHsc,/utf-8" -I"' + $includes + '" -I"' + $publicIncludes + '" "' + $source + '" -o "' + $executable + '"'
$command | Set-Content -LiteralPath (Join-Path $destination "command.txt") -Encoding utf8
& $env:ComSpec /d /s /c $command 2>&1 | Tee-Object -FilePath (Join-Path $destination "build.log")
if ($LASTEXITCODE -ne 0) { throw "CUDA build failed with exit code $LASTEXITCODE" }
& $nvcc --version | Set-Content -LiteralPath (Join-Path $destination "nvcc-version.txt") -Encoding utf8
$sourceHashes = [ordered]@{}
foreach ($inputPath in @($source, (Join-Path $publicIncludes "jshc/image_contract.hpp"), (Join-Path $includes "stb_image.h"), (Join-Path $includes "stb_image_write.h"), $PSCommandPath)) {
    $sourceHashes[$inputPath] = (Get-FileHash -LiteralPath $inputPath -Algorithm SHA256).Hash.ToLowerInvariant()
}
[ordered]@{
    architecture = "sm_$Architecture"
    ptx_jit_required = $false
    executable = $executable
    executable_sha256 = (Get-FileHash -LiteralPath $executable -Algorithm SHA256).Hash.ToLowerInvariant()
    nvcc = $nvcc
    visual_studio = $visualStudio
    command = $command
    command_file_sha256 = (Get-FileHash -LiteralPath (Join-Path $destination "command.txt") -Algorithm SHA256).Hash.ToLowerInvariant()
    sources_sha256 = $sourceHashes
} | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $destination "build-manifest.json") -Encoding utf8
Write-Output $executable
