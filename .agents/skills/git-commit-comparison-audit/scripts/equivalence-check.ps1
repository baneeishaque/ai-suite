<#
.SYNOPSIS
    Industrial content-equivalence check between two Git commits.

.DESCRIPTION
    Performs four depth-comparison primitives on two commits and prints a tabular verdict:
      1. Patch-ID comparison  (`git patch-id --stable`) — content fingerprint, independent of SHA/parent/author/date.
      2. Tree-SHA comparison  (`git rev-parse <SHA>^{tree}`) — exact-tree identity.
      3. Tree-diff analysis   (`git diff --stat`)         — file-level delta when trees differ.
      4. Subject + body diff  (`git log -1 --format`)     — message-level delta (typical signature of a reword-rebase mirror).

    This is the canonical primitive for distinguishing a content-equivalent rewrite (safe force-push)
    from a true semantic divergence (cherry-pick / rebase reconciliation required).

.PARAMETER Sha1
    The first commit SHA (full or unique short form).

.PARAMETER Sha2
    The second commit SHA (full or unique short form).

.PARAMETER RepoPath
    Optional path to the Git repository. Defaults to the current working directory.

.EXAMPLE
    pwsh-preview -File equivalence-check.ps1 -Sha1 9e15d8f2 -Sha2 72be8116

.EXAMPLE
    pwsh-preview -File equivalence-check.ps1 9e15d8f2 72be8116 -RepoPath /repos/ai-agent-rules

.NOTES
    Common-Utils dot-source: skipped — `Common-Utils.ps1` is not present in this workspace's
    `ai-agent-rules/powershell-scripts/` submodule. When the submodule is initialized, this script
    SHOULD be refactored to dot-source it for `Write-Message` consistency.

    Profile-init mandate: invoke via `pwsh-preview -File ...` (or `pwsh -File ...`); `-NoProfile` is FORBIDDEN
    per `ai-agent-rules/script-management-rules.md`.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0)] [string] $Sha1,
    [Parameter(Mandatory = $true, Position = 1)] [string] $Sha2,
    [Parameter(Mandatory = $false)] [string] $RepoPath = (Get-Location).Path
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Push-Location $RepoPath
try {
    # 1. Patch-ID comparison
    Write-Host "=== 1. PATCH-ID (content fingerprint) ===" -ForegroundColor Cyan
    $pid1 = (git show $Sha1 | git patch-id --stable) -split '\s+' | Select-Object -First 1
    $pid2 = (git show $Sha2 | git patch-id --stable) -split '\s+' | Select-Object -First 1
    Write-Host ("Sha1 patch-id = " + $pid1)
    Write-Host ("Sha2 patch-id = " + $pid2)
    $patchEq = ($pid1 -eq $pid2)
    if ($patchEq) { Write-Host "PATCH-ID EQUIVALENT" -ForegroundColor Green }
    else          { Write-Host "PATCH-ID DIFFERENT"  -ForegroundColor Yellow }

    # 2. Tree-SHA comparison
    Write-Host "`n=== 2. TREE SHA ===" -ForegroundColor Cyan
    $t1 = git rev-parse "${Sha1}^{tree}"
    $t2 = git rev-parse "${Sha2}^{tree}"
    Write-Host ("Sha1 tree = " + $t1)
    Write-Host ("Sha2 tree = " + $t2)
    $treeEq = ($t1 -eq $t2)
    if ($treeEq) { Write-Host "TREE IDENTICAL" -ForegroundColor Green }
    else         { Write-Host "TREE DIFFERS"   -ForegroundColor Yellow }

    # 3. Tree diff (only meaningful if trees differ)
    Write-Host "`n=== 3. TREE DIFF (file-level) ===" -ForegroundColor Cyan
    if ($treeEq) {
        Write-Host "(skipped — trees identical)" -ForegroundColor DarkGray
    } else {
        git diff --stat $Sha1 $Sha2
    }

    # 4. Subjects + bodies
    Write-Host "`n=== 4. SUBJECTS & BODIES ===" -ForegroundColor Cyan
    Write-Host "--- $Sha1 ---"
    git log -1 --format="%s%n%n%b" $Sha1
    Write-Host "`n--- $Sha2 ---"
    git log -1 --format="%s%n%n%b" $Sha2

    # 5. Refinement detection (only meaningful when trees differ)
    $refined = $false
    if (-not $treeEq) {
        Write-Host "`n=== 5. REFINEMENT NORMALISATION CHECK ===" -ForegroundColor Cyan
        # Collect unified diff and inspect '-'/'+' line pairs after stripping diff metadata.
        $diff = git diff --no-color --unified=0 $Sha1 $Sha2
        $minus = @()
        $plus  = @()
        foreach ($line in $diff) {
            if ($line -match '^(---|\+\+\+|diff |index |@@ )') { continue }
            if ($line.StartsWith('-')) { $minus += $line.Substring(1) }
            elseif ($line.StartsWith('+')) { $plus += $line.Substring(1) }
        }

        function _Normalise([string]$s) {
            # Kebab-case normalisation: lowercase + snake_case -> kebab-case.
            return ($s.ToLowerInvariant() -replace '_', '-')
        }

        $eligible = ($minus.Count -gt 0) -and ($minus.Count -eq $plus.Count)
        $allMatch = $eligible
        if ($eligible) {
            for ($i = 0; $i -lt $minus.Count; $i++) {
                if ((_Normalise $minus[$i]) -ne (_Normalise $plus[$i])) { $allMatch = $false; break }
            }
        }

        if ($allMatch) {
            $refined = $true
            Write-Host "REFINED — every removed/added line pair is identical after kebab-case normalisation" -ForegroundColor Green
            Write-Host ("  pairs inspected = " + $minus.Count)
        } else {
            Write-Host "NOT a pure normalisation — at least one line pair carries a semantic delta" -ForegroundColor Yellow
        }
    }

    # Verdict
    Write-Host "`n=== VERDICT ===" -ForegroundColor Cyan
    if ($patchEq -and $treeEq) {
        Write-Host "CONTENT-EQUIVALENT (rewrite mirror — safe force-push after full audit)" -ForegroundColor Green
    } elseif ($patchEq -and -not $treeEq) {
        Write-Host "PATCH-EQUIVALENT BUT TREES DIFFER (different parents — likely cherry-pick across histories)" -ForegroundColor Yellow
    } elseif ($refined) {
        Write-Host "REFINED EQUIVALENT (trees differ; delta is a deterministic kebab-case normalisation — intentional refinement, safe to keep local form)" -ForegroundColor Green
    } else {
        Write-Host "DIVERGENT (true semantic delta — reconciliation required)" -ForegroundColor Red
    }
}
finally {
    Pop-Location
}
