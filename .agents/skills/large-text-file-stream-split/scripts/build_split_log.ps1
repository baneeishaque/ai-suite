<#
.SYNOPSIS
    Build split_log.exe from split_log.c using whatever C compiler is on $env:Path.

.DESCRIPTION
    Auto-detects gcc, clang, or MSVC cl on $env:Path (in that order) and compiles
    split_log.c with -O2 / /O2 plus warning flags. Idempotent: skips rebuild when
    split_log.exe is newer than split_log.c.

    This is the PUBLIC, organization-agnostic build script. If your environment ships
    a C compiler that is not on $env:Path (e.g., a corporate toolbase bundle), wrap
    this script in an organization-specific composer skill that prepends the compiler's
    bin\ directory to $env:Path BEFORE invoking this script — never edit this file to
    hard-code an organization-specific path.

.PARAMETER Src
    Absolute or relative path to split_log.c. Defaults to the sibling of this script.

.PARAMETER Out
    Absolute or relative path to the output split_log.exe. Defaults to the sibling of
    this script.

.PARAMETER Force
    Recompile unconditionally even if split_log.exe is newer than split_log.c.

.EXAMPLE
    .\build_split_log.ps1
    # idempotent build using the first compiler found on PATH

.EXAMPLE
    .\build_split_log.ps1 -Force
    # always recompile

.NOTES
    - Cross-compatible with Windows PowerShell 5.1+ and PowerShell Core 7+.
    - Runs in the current session (no child PS subprocess, no -ExecutionPolicy Bypass)
      per shell-execution-rules.md §2.5.
    - Does NOT dot-source Common-Utils.ps1 — this skill is intentionally
      dependency-free so it can be vendored into a chunk-folder consumer without
      requiring the powershell-scripts submodule. The Write-Host calls are simple
      diagnostics, not the Write-Message helper.
#>
[CmdletBinding()]
param(
    [string]$Src = (Join-Path (Split-Path -Parent $MyInvocation.MyCommand.Path) 'split_log.c'),
    [string]$Out = (Join-Path (Split-Path -Parent $MyInvocation.MyCommand.Path) 'split_log.exe'),
    [switch]$Force
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if (-not (Test-Path -LiteralPath $Src)) {
    throw "source not found: $Src"
}

# Up-to-date check.
if (-not $Force -and (Test-Path -LiteralPath $Out)) {
    $srcTime = (Get-Item -LiteralPath $Src).LastWriteTimeUtc
    $outTime = (Get-Item -LiteralPath $Out).LastWriteTimeUtc
    if ($outTime -ge $srcTime) {
        Write-Host "[build_split_log] up-to-date: $Out"
        return
    }
}

function Invoke-Build {
    param(
        [Parameter(Mandatory)] [string]$Exe,   # full path to compiler
        [Parameter(Mandatory)] [ValidateSet('cl','gcc-like')] [string]$Kind
    )
    Write-Host "[build_split_log] using: $Exe"
    if ($Kind -eq 'cl') {
        & $Exe /nologo /O2 /W4 /MT "/Fe:$Out" $Src
    } else {
        & $Exe -O2 -Wall -Wextra -o $Out $Src
    }
    if ($LASTEXITCODE -ne 0) { throw "compile failed (exit $LASTEXITCODE)" }
}

# PATH compilers, in priority order.
$probes = @(
    @{ Name = 'gcc.exe';   Kind = 'gcc-like' },
    @{ Name = 'clang.exe'; Kind = 'gcc-like' },
    @{ Name = 'cl.exe';    Kind = 'cl'       }
)

foreach ($p in $probes) {
    $cmd = Get-Command $p.Name -ErrorAction SilentlyContinue
    if ($cmd) {
        Invoke-Build -Exe $cmd.Source -Kind $p.Kind
        Write-Host "[build_split_log] OK -> $Out"
        return
    }
}

throw @"
No C compiler found on `$env:Path.
  Tried: gcc.exe, clang.exe, cl.exe
  Install one of:
    - MSVC Build Tools  (provides cl.exe; run inside a 'Developer PowerShell')
    - MinGW-w64         (provides gcc.exe; e.g., via MSYS2 or scoop)
    - LLVM / Clang      (provides clang.exe)
  If your organization ships a toolbase-bundled compiler that is not on PATH,
  prepend its bin\ directory to `$env:Path BEFORE running this script (typically
  via an organization-specific composer skill).
"@
