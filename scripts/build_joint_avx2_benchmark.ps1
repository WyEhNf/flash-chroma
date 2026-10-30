param(
    [Parameter(Mandatory = $true)]
    [string]$Compiler,

    [Parameter(Mandatory = $true)]
    [string]$Output
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$outputPath = [System.IO.Path]::GetFullPath($Output)
$outputDirectory = Split-Path -Parent $outputPath

if (-not (Test-Path -LiteralPath $Compiler -PathType Leaf)) {
    throw "找不到编译器：$Compiler"
}

if (-not (Test-Path -LiteralPath $outputDirectory -PathType Container)) {
    New-Item -ItemType Directory -Path $outputDirectory | Out-Null
}

$sources = @(
    'experiments/joint-avx2-runtime/bench_direct_avx2.cpp',
    'experiments/skylake-andn-normal-runtime/andn_outplace/channel_avx2.cpp',
    'experiments/joint-avx2-runtime/repo_no_prefetch.cpp',
    'experiments/joint-avx2-runtime/repo_t0.cpp',
    'experiments/joint-avx2-runtime/repo_cached.cpp',
    'experiments/joint-avx2-runtime/repo_t0_cached.cpp'
) | ForEach-Object { Join-Path $root $_ }

$arguments = @(
    '-O3', '-DNDEBUG', '-std=c++17', '-mavx2', '-mbmi', '-mtune=skylake', '-fopenmp',
    ('-I' + (Join-Path $root 'experiments/channel-runtime'))
) + $sources + @('-o', $outputPath)

$originalPath = $env:PATH
try {
    $env:PATH = (Split-Path -Parent ([System.IO.Path]::GetFullPath($Compiler))) + ';' + $env:PATH
    & $Compiler @arguments
    if ($LASTEXITCODE -ne 0) {
        throw "AVX2 微基准构建失败，编译器退出码：$LASTEXITCODE"
    }
} finally {
    $env:PATH = $originalPath
}

Write-Output "已生成：$outputPath"
