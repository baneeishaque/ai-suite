<#
.SYNOPSIS
    Materialize INSTRUCTIONS.md from the skill template into a chunk folder.

.DESCRIPTION
    The split_log.exe C splitter emits chunks + INDEX.csv but does NOT write
    INSTRUCTIONS.md. The large-text-file-stream-split skill mandates that the
    chunk folder be self-describing (humans + machines). This script closes
    that gap: it reads templates\INSTRUCTIONS.md.template, substitutes every
    {{PLACEHOLDER}} from values derived from INDEX.csv + the source file, and
    writes INSTRUCTIONS.md into the chunk folder.

    Idempotent: by default refuses to overwrite an existing INSTRUCTIONS.md;
    pass -Force to overwrite.

    All values except -OutDir and -SourcePath are auto-derived from INDEX.csv.

.PARAMETER OutDir
    The chunk folder. Must already contain INDEX.csv (produced by split_log.exe).

.PARAMETER SourcePath
    Path to the original (pre-split) source file. Used for size / line-count /
    basename derivation.

.PARAMETER Force
    Overwrite an existing INSTRUCTIONS.md.

.EXAMPLE
    .\emit_instructions.ps1 -OutDir ..\..\..\log_194_chunks -SourcePath ..\..\..\#194.txt

.NOTES
    - Cross-compatible with Windows PowerShell 5.1+ and PowerShell Core 7+.
    - Anchored on this script's own location to find the template; safe to invoke
      from any cwd.
    - Does NOT dot-source Common-Utils.ps1 — this skill is intentionally
      dependency-free so it can be vendored into a chunk-folder consumer.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string]$OutDir,
    [Parameter(Mandatory)] [string]$SourcePath,
    [switch]$Force
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# Resolve template relative to THIS script, not the caller's cwd.
$scriptDir   = Split-Path -Parent $MyInvocation.MyCommand.Path
$templateRel = Join-Path $scriptDir '..\templates\INSTRUCTIONS.md.template'
$templatePath = (Resolve-Path -LiteralPath $templateRel).Path

if (-not (Test-Path -LiteralPath $OutDir -PathType Container)) {
    throw "OutDir not found: $OutDir"
}
if (-not (Test-Path -LiteralPath $SourcePath -PathType Leaf)) {
    throw "SourcePath not found: $SourcePath"
}

$indexPath = Join-Path $OutDir 'INDEX.csv'
if (-not (Test-Path -LiteralPath $indexPath)) {
    throw "INDEX.csv not found in $OutDir -- run split_log.exe first."
}

$dest = Join-Path $OutDir 'INSTRUCTIONS.md'
if ((Test-Path -LiteralPath $dest) -and -not $Force) {
    throw "INSTRUCTIONS.md already exists at $dest. Pass -Force to overwrite."
}

# Derive values from INDEX.csv + source file.
$index = Import-Csv -LiteralPath $indexPath
if (-not $index -or $index.Count -eq 0) { throw "INDEX.csv is empty: $indexPath" }

$chunkCount = $index.Count
$lastRow    = $index[-1]
$sourceLines = [int64]$lastRow.EndLine

# Recover base name from any chunk filename: <base>_part_NNN_of_TTT__lines_...
$firstName = $index[0].FileName
if ($firstName -notmatch '^(.+?)_part_\d+_of_\d+__lines_\d+-\d+\.txt$') {
    throw "Cannot derive base_name from chunk filename: $firstName"
}
$baseName = $Matches[1]

$srcItem = Get-Item -LiteralPath $SourcePath
$srcSizeBytes = $srcItem.Length
$srcSizeMB    = [math]::Round($srcSizeBytes / 1MB, 2)
$chunkSizeMB  = [math]::Round(($srcSizeBytes / $chunkCount) / 1MB, 2)
$srcFileName  = $srcItem.Name

# Format line count with thousands separators for human-readability.
$sourceLinesFmt = '{0:N0}' -f $sourceLines

# Load template and substitute placeholders.
$template = Get-Content -LiteralPath $templatePath -Raw -Encoding UTF8

$replacements = @{
    'SOURCE_FILENAME'    = $srcFileName
    'SOURCE_SIZE_MB'     = $srcSizeMB
    'SOURCE_LINE_COUNT'  = $sourceLinesFmt
    'CHUNK_COUNT'        = $chunkCount
    'CHUNK_SIZE_MB'      = $chunkSizeMB
    'BASE_NAME'          = $baseName
}

$rendered = $template
foreach ($key in $replacements.Keys) {
    $rendered = $rendered.Replace("{{$key}}", [string]$replacements[$key])
}

# Strip the template's "Drop this INSTRUCTIONS.md ..." authoring note (lines
# starting with `> Drop this`) so the emitted file is consumer-facing.
$rendered = $rendered -replace '(?ms)^> Drop this `INSTRUCTIONS\.md`.*?\r?\n\r?\n', ''

# Write UTF-8 (no BOM) with LF line endings to match the splitter's contract.
$rendered = $rendered -replace "`r`n", "`n"
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText($dest, $rendered, $utf8NoBom)

Write-Host "[emit_instructions] OK -> $dest"
Write-Host "[emit_instructions]   source       : $srcFileName ($srcSizeMB MB / $sourceLinesFmt lines)"
Write-Host "[emit_instructions]   chunks       : $chunkCount (~$chunkSizeMB MB each)"
Write-Host "[emit_instructions]   base_name    : $baseName"
