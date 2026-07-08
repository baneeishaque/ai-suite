<#
.SYNOPSIS
    Walk aligned commit pairs between two branches and emit per-pair equivalence verdicts.

.DESCRIPTION
    Iterates oldest-first over both branches in lockstep. For each positional pair, runs the
    single-pair `equivalence-check.ps1` primitive and prints the verdict.

    SPLIT-AWARENESS: when a pair returns DIVERGENT, the walker tests whether the local commit
    was *split* into two atomic commits (e.g., a Generated/Custom .gitignore split per
    `git-gitignore-handling-rules.md` §2). The split test compares `tree(local[i+1])` against
    `tree(remote[j])`:
      - tree-identical                          -> SPLIT EQUIVALENT          (advance local by 2)
      - tree differs but every line-pair normalises (kebab) -> SPLIT REFINED EQUIVALENT (advance local by 2)
      - otherwise                               -> true DIVERGENT, walker stops

    Symmetrically, if `tree(remote[j+1])` matches `tree(local[i])`, the remote side carries the
    split and the walker advances remote by 2 instead.

    The walker stops on any unrecoverable DIVERGENT verdict.

.PARAMETER LocalBranch
    The local branch ref (e.g. `master-3`).

.PARAMETER RemoteBranch
    The remote branch ref (e.g. `origin/master-3`).

.PARAMETER StartIndex
    1-based positional index to begin walking from. Default 1.

.PARAMETER MaxPairs
    Maximum number of pairs to walk. Default 100000 (effectively unlimited).

.PARAMETER RepoPath
    Optional repo root. Defaults to current working directory.

.EXAMPLE
    pwsh-preview -File pair-walker.ps1 -LocalBranch master-3 -RemoteBranch origin/master-3

.EXAMPLE
    pwsh-preview -File pair-walker.ps1 -LocalBranch master-3 -RemoteBranch origin/master-3 -StartIndex 5

.NOTES
    Profile-init mandate: invoke via `pwsh-preview -File ...`; `-NoProfile` is FORBIDDEN per
    `ai-agent-rules/script-management-rules.md`.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)] [string] $LocalBranch,
    [Parameter(Mandatory = $true)] [string] $RemoteBranch,
    [Parameter(Mandatory = $false)] [int]    $StartIndex = 1,
    [Parameter(Mandatory = $false)] [int]    $MaxPairs   = 100000,
    [Parameter(Mandatory = $false)] [string] $RepoPath   = (Get-Location).Path
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$ScriptDir       = Split-Path -Parent $MyInvocation.MyCommand.Path
$EquivCheckPath  = Join-Path $ScriptDir 'equivalence-check.ps1'
if (-not (Test-Path $EquivCheckPath)) {
    Write-Host "ERROR: cannot locate equivalence-check.ps1 at $EquivCheckPath" -ForegroundColor Red
    exit 2
}

Push-Location $RepoPath
try {
    # ---------- helpers ----------
    function _Normalise([string]$s) { return ($s.ToLowerInvariant() -replace '_', '-') }

    function Test-TreeEquivalent {
        param([string]$ShaA, [string]$ShaB)
        # Returns: 'IDENTICAL' | 'REFINED' | 'DIVERGENT'
        $tA = git rev-parse "${ShaA}^{tree}"
        $tB = git rev-parse "${ShaB}^{tree}"
        if ($tA -eq $tB) { return 'IDENTICAL' }

        $diff = git diff --no-color --unified=0 $ShaA $ShaB
        $minus = @(); $plus = @()
        foreach ($ln in $diff) {
            if ($ln -match '^(---|\+\+\+|diff |index |@@ )') { continue }
            if ($ln.StartsWith('-')) { $minus += $ln.Substring(1) }
            elseif ($ln.StartsWith('+')) { $plus += $ln.Substring(1) }
        }
        if ($minus.Count -gt 0 -and $minus.Count -eq $plus.Count) {
            $allMatch = $true
            for ($k = 0; $k -lt $minus.Count; $k++) {
                if ((_Normalise $minus[$k]) -ne (_Normalise $plus[$k])) { $allMatch = $false; break }
            }
            if ($allMatch) { return 'REFINED' }
        }
        return 'DIVERGENT'
    }

    function Get-VerdictLine {
        param([string]$ShaA, [string]$ShaB)
        $output = & pwsh-preview -File $EquivCheckPath -Sha1 $ShaA -Sha2 $ShaB 2>&1
        $matched = $output |
            Select-String -Pattern '^(CONTENT-EQUIVALENT|PATCH-EQUIVALENT|REFINED EQUIVALENT|DIVERGENT)' |
            Select-Object -First 1
        $verdict = $null
        if ($matched) { $verdict = $matched.Line }
        # Force single-object return via PSCustomObject.
        [pscustomobject]@{ Verdict = $verdict; Output = $output }
    }

    # ---------- enumerate ----------
    $local  = @(git log --format='%H' --reverse $LocalBranch)
    $remote = @(git log --format='%H' --reverse $RemoteBranch)
    Write-Host "local  ($LocalBranch)  count = $($local.Count)"
    Write-Host "remote ($RemoteBranch) count = $($remote.Count)"

    $i = $StartIndex - 1   # local index
    $j = $StartIndex - 1   # remote index
    $pairNum = $StartIndex
    $walked = 0

    while ($walked -lt $MaxPairs) {
        if ($i -ge $local.Count -or $j -ge $remote.Count) {
            Write-Host "`n=== END OF ALIGNMENT ===" -ForegroundColor Yellow
            Write-Host "  local  remaining: $($local.Count - $i)"
            Write-Host "  remote remaining: $($remote.Count - $j)"
            break
        }
        $L = $local[$i]; $R = $remote[$j]
        $sL = git log -1 --format='%s' $L
        $sR = git log -1 --format='%s' $R

        Write-Host "`n=========================================================" -ForegroundColor Magenta
        Write-Host "Pair #$pairNum   (local idx $($i+1), remote idx $($j+1))"  -ForegroundColor Magenta
        Write-Host "  local  $($L.Substring(0,8))  $sL"
        Write-Host "  remote $($R.Substring(0,8))  $sR"
        Write-Host "=========================================================" -ForegroundColor Magenta

        $verdictResult = Get-VerdictLine -ShaA $L -ShaB $R
        if (-not $verdictResult.Verdict) {
            Write-Host "FAILED to parse verdict" -ForegroundColor Red
            Write-Host ($verdictResult.Output -join "`n")
            break
        }
        Write-Host "VERDICT: $($verdictResult.Verdict)"

        if ($verdictResult.Verdict -notlike 'DIVERGENT*') {
            $i++; $j++; $pairNum++; $walked++
            continue
        }

        # ---------- split-equivalence probe ----------
        Write-Host "`n--- Probing for SPLIT-EQUIVALENCE ---" -ForegroundColor Cyan

        $splitFound = $false

        # Hypothesis A: local was split (local[i] + local[i+1] == remote[j])
        if ($i + 1 -lt $local.Count) {
            $L2 = [string]$local[$i + 1]
            $sL2 = git log -1 --format='%s' $L2
            $L2_8 = if ($L2.Length -ge 8) { $L2.Substring(0, 8) } else { $L2 }
            $R_8  = if ($R.Length  -ge 8) { $R.Substring(0, 8)  } else { $R  }
            Write-Host ("  A) test tree(local[i+1]=" + $L2_8 + " '" + $sL2 + "') vs tree(remote[j]=" + $R_8 + ")")
            $cmp = Test-TreeEquivalent -ShaA $L2 -ShaB $R
            Write-Host "     -> $cmp"
            if ($cmp -eq 'IDENTICAL') {
                Write-Host "VERDICT: SPLIT EQUIVALENT (local was split into 2; trees match after both halves)" -ForegroundColor Green
                $i += 2; $j += 1; $pairNum++; $walked++; $splitFound = $true
            } elseif ($cmp -eq 'REFINED') {
                Write-Host "VERDICT: SPLIT REFINED EQUIVALENT (local split + kebab refinement; safe)" -ForegroundColor Green
                $i += 2; $j += 1; $pairNum++; $walked++; $splitFound = $true
            }
        }

        if (-not $splitFound -and $j + 1 -lt $remote.Count) {
            # Hypothesis B: remote was split (remote[j] + remote[j+1] == local[i])
            $R2 = [string]$remote[$j + 1]
            $sR2 = git log -1 --format='%s' $R2
            $R2_8 = if ($R2.Length -ge 8) { $R2.Substring(0, 8) } else { $R2 }
            $L_8  = if ($L.Length  -ge 8) { $L.Substring(0, 8)  } else { $L  }
            Write-Host ("  B) test tree(remote[j+1]=" + $R2_8 + " '" + $sR2 + "') vs tree(local[i]=" + $L_8 + ")")
            $cmp = Test-TreeEquivalent -ShaA $L -ShaB $R2
            Write-Host "     -> $cmp"
            if ($cmp -eq 'IDENTICAL') {
                Write-Host "VERDICT: SPLIT EQUIVALENT (remote was split into 2; trees match after both halves)" -ForegroundColor Green
                $i += 1; $j += 2; $pairNum++; $walked++; $splitFound = $true
            } elseif ($cmp -eq 'REFINED') {
                Write-Host "VERDICT: SPLIT REFINED EQUIVALENT (remote split + kebab refinement; safe)" -ForegroundColor Green
                $i += 1; $j += 2; $pairNum++; $walked++; $splitFound = $true
            }
        }

        if (-not $splitFound) {
            Write-Host "`nSTOPPING at pair #$pairNum — true DIVERGENT, no split-equivalence detected." -ForegroundColor Red
            Write-Host "Full equivalence-check output:" -ForegroundColor Red
            Write-Host ($verdictResult.Output -join "`n")
            break
        }
    }

    Write-Host "`n=== WALK COMPLETE ===" -ForegroundColor Cyan
    Write-Host "  pairs walked        : $walked"
    Write-Host "  next local  index   : $($i + 1) of $($local.Count)"
    Write-Host "  next remote index   : $($j + 1) of $($remote.Count)"
}
finally {
    Pop-Location
}
