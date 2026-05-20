<#
.SYNOPSIS
    Split a Microsoft / GitHub Copilot activity-history CSV into one CSV per Conversation.

.DESCRIPTION
    Reads a Copilot activity-history export (columns: Conversation, Time, Author, Message),
    groups rows by the Conversation column, sorts each group by Time ascending with the
    Human author placed before the AI author on identical timestamps (the human always
    starts a turn), and writes one CSV per conversation into the output directory. Output
    file names are slugified (lowercase, hyphen-separated, alphanumerics only, max 120
    chars) from the Conversation title.

    The input CSV is expected to be UTF-8 (BOM tolerated) with the literal header
    "Conversation,Time,Author,Message". Multi-line quoted Message cells are preserved
    losslessly because Import-Csv fully parses RFC-4180 quoting.

.PARAMETER InputPath
    Absolute or relative path to the source copilot-activity-history.csv file.

.PARAMETER OutputDirectory
    Directory to write per-conversation CSVs into. Created if missing. Existing files with
    the same slug are overwritten.

.PARAMETER HumanAuthor
    Author label to place first on tie-broken timestamps. Defaults to "Human".

.PARAMETER AiAuthor
    Author label that loses the timestamp tiebreak. Defaults to "AI".

.EXAMPLE
    pwsh-preview -File ./Split-CopilotActivityHistory.ps1 `
        -InputPath ~/Downloads/copilot-activity-history.csv `
        -OutputDirectory ~/Downloads/copilot-conversations

.EXAMPLE
    pwsh -File ./Split-CopilotActivityHistory.ps1 -InputPath ./history.csv -OutputDirectory ./out

.NOTES
    Common-Utils.ps1 dot-sourcing is exempted here because the script's only side effect is
    file emission to a user-provided directory; it produces no console messaging beyond a
    final summary line, so the Write-Message safeguard is unnecessary. If shared logging is
    later required, dot-source via the portable anchored path documented in SKILL.md section 3.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$InputPath,

    [Parameter(Mandatory = $true)]
    [string]$OutputDirectory,

    [string]$HumanAuthor = 'Human',

    [string]$AiAuthor = 'AI'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if (-not (Test-Path -LiteralPath $InputPath)) {
    Write-Error "Input CSV not found: $InputPath"
    exit 1
}

if (-not (Test-Path -LiteralPath $OutputDirectory)) {
    New-Item -ItemType Directory -Path $OutputDirectory -Force | Out-Null
}

function ConvertTo-Slug {
    param([string]$Text)
    if ([string]::IsNullOrWhiteSpace($Text)) { return 'untitled' }
    $lower = $Text.Trim().ToLowerInvariant()
    $cleaned = [regex]::Replace($lower, '[^a-z0-9]+', '-').Trim('-')
    if ([string]::IsNullOrEmpty($cleaned)) { return 'untitled' }
    if ($cleaned.Length -gt 120) { $cleaned = $cleaned.Substring(0, 120).TrimEnd('-') }
    return $cleaned
}

$rows = Import-Csv -LiteralPath $InputPath
$groups = $rows | Group-Object -Property Conversation

$written = 0
foreach ($g in $groups) {
    $sorted = $g.Group | Sort-Object -Property `
        @{ Expression = 'Time'; Ascending = $true }, `
        @{ Expression = { if ($_.Author -eq $HumanAuthor) { 0 } elseif ($_.Author -eq $AiAuthor) { 1 } else { 2 } }; Ascending = $true }

    $slug = ConvertTo-Slug -Text $g.Name
    $outPath = Join-Path -Path $OutputDirectory -ChildPath ($slug + '.csv')
    $sorted | Export-Csv -LiteralPath $outPath -NoTypeInformation -Encoding utf8
    $written++
}

Write-Host ("Wrote {0} conversation CSVs to {1}" -f $written, (Resolve-Path -LiteralPath $OutputDirectory))
