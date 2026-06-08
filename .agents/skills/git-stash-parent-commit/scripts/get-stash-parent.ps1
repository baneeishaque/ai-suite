#!pwsh
<#
.SYNOPSIS
    Gets the commit hash and subject line that was HEAD when a Git stash was created.
.DESCRIPTION
    Given a stash reference (default stash@{0}), this script outputs the commit hash
    and subject line of the stash's first parent (<stash>^1), representing the commit
    that was checked out when `git stash push` was run.
    The script is designed for use in agent-driven terminals: it never invokes a pager
    and returns machine-parsable output (hash on line 1, subject on line 2).
.PARAMETER StashRef
    The stash reference to inspect (e.g., stash@{0}, stash@{1}). Defaults to stash@{0}.
.EXAMPLE
    & "$PSScriptRoot\../../git-stash-parent-commit/scripts/get-stash-parent.ps1"
    Returns two lines: hash then subject of the latest stash's parent commit.
.EXAMPLE
    & "$PSScriptRoot\../../git-stash-parent-commit/scripts/get-stash-parent.ps1" -StashRef stash@{1}
    Returns hash/subject for the parent of stash@{1}.
.NOTES
    Author: Claude Code (Anthropic)
    Version: 1.0.0
    Required modules: None
    Depends on: Git 2.x+
    Tag: Git, Stash, Commit
#>

param (
    [string]$StashRef = 'stash@{0}'
)

# Enable strict mode and treat unset variables as errors
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

try {
    # Verify the stash reference and get its first parent commit hash
    $hash = git rev-parse --verify "$StashRef^1" 2>$null
    if (-not $hash) {
        Write-Error "Invalid stash reference '$StashRef' or unable to determine parent commit."
        exit 1
    }

    # Get the full hash and subject line
    $commitInfo = git show -s --format='%H:%s' $hash
    if (-not $commitInfo) {
        Write-Error "Failed to retrieve commit info for hash '$hash'."
        exit 1
    }

    # Split into hash and subject
    $parts = $commitInfo -split ':', 2
    if ($parts.Length -lt 2) {
        Write-Error "Unexpected commit info format: '$commitInfo'"
        exit 1
    }
    $commitHash = $parts[0]
    $commitSubject = $parts[1]

    # Output hash on first line, subject on second line
    Write-Output $commitHash
    Write-Output $commitSubject
    exit 0
}
catch {
    Write-Error $_.Exception.Message
    exit 1
}
