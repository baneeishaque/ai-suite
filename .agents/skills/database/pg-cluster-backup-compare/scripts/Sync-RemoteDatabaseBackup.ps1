#!pwsh
#Requires -Version 5.1

<#
.SYNOPSIS
    Industrial Local-Remote Database Synchronization Tool (Single-Session).
    Compatible with PowerShell Core (Mac/Linux/Windows).

.DESCRIPTION
    Orchestrates a remote PostgreSQL backup via a single SSH streaming session.
    1. Connects to the remote server once.
    2. Validates dependencies and extracts DATABASE_URL remotely.
    3. Streams the binary dump directly to the local 'db_dumps' directory.
    4. Automatically commits the dump to the local repository.

.PARAMETER User
    Remote SSH username.

.PARAMETER Host
    Remote SSH host / IP address.

.PARAMETER Password
    Remote SSH password (requires 'sshpass' locally).

.PARAMETER RemoteEnvPath
    Absolute path to the .env file on the remote server.

.PARAMETER EnvDbKey
    The exact key in the remote .env file mapped to the connection string.
    Defaults to 'DATABASE_URL'.

.PARAMETER DatabasePrefix
    Core naming prefix for the output dump files.

.PARAMETER PendingSuffix
    Suffix applied to the temporary file during the streaming process.
    Defaults to 'pending'.

.PARAMETER OutputDirName
    Local directory name for database storage.
    Defaults to 'db_dumps'.

.PARAMETER TimeZones
    Array of TimeZone conversion strings formatted as "SystemZoneId:Label".

.PARAMETER Format
    Format of the dump file: 'Custom' (binary) or 'Plain' (text).
    Defaults to 'Custom'. Ignored when -Scope is 'Cluster' (forced to 'Plain').

.PARAMETER Scope
    Backup scope:
      Database    — Single database via pg_dump (default).
      Cluster     — Full cluster logical backup via pg_dumpall: every database,
                    roles, tablespaces, database-level settings (encoding,
                    collation, connection limits), privileges, and extensions.
                    Output is plain SQL (pg_dumpall has no custom format).
      ClusterSplit — Full cluster backup split into globals.sql (roles,
                    tablespaces, settings, privileges — plain SQL) plus one
                    custom-format compressed archive per database.
                    Best option for prod→staging mirror: small network
                    transfer, parallel restore via pg_restore -j N, and
                    surgical per-table/schema restores.  No extra remote
                    disk required beyond the largest single database dump.

.PARAMETER PostDumpAction
    Controls the Git pipeline executed after the dump is created.
    None   — Dump only, no Git operations.
    Commit — Dump, then git add + git commit.
    Push   — Dump, git add + git commit + git push (default).
#>

Param (
    [Parameter(Mandatory=$true)][string]$User,
    [Parameter(Mandatory=$true)][string]$ServerHost,
    [Parameter(Mandatory=$true)][string]$Password,
    [Parameter(Mandatory=$true)][string]$RemoteEnvPath,
    [string]$EnvDbKey = "DATABASE_URL",
    [Parameter(Mandatory=$true)][string]$DatabasePrefix,
    [string]$PendingSuffix = "pending",
    [string]$OutputDirName = "db_dumps",
    [Parameter(Mandatory=$true)][string[]]$TimeZones,
    [ValidateSet("Custom","Plain")]
    [string]$Format = "Custom",
    [ValidateSet("Database","Cluster","ClusterSplit")]
    [string]$Scope = "Database",
    [ValidateSet("None","Commit","Push")]
    [string]$PostDumpAction = "Push"
)

# pg_dumpall only emits plain SQL — force Plain when doing a full cluster backup.
if ($Scope -eq "Cluster" -and $Format -ne "Plain") {
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Note: Scope=Cluster forces Format=Plain (pg_dumpall has no custom format)." -ForegroundColor Yellow
    $Format = "Plain"
}

$DumpTool = switch ($Scope) {
    "Cluster"      { "pg_dumpall" }
    "ClusterSplit" { "pg_dumpall_split" }
    "Database"     { "pg_dump" }
}

$ErrorActionPreference = "Stop"

# Ensure consistent encoding for binary streams
$PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'
$PSDefaultParameterValues['*:Encoding'] = 'utf8'

# ── Constants ────────────────────────────────────────────────────────────────
Set-Variable -Name BASH_SCRIPT_NAME -Value "parse_dotenv_and_stream_pg_dump.bash" -Option Constant
Set-Variable -Name BASH_SCRIPT_FALLBACK_NAME -Value "parse_dotenv_and_stream_pg_dump.sh" -Option Constant
Set-Variable -Name SSH_OPTS -Value @(
    "-o", "StrictHostKeyChecking=no",
    "-o", "UserKnownHostsFile=/dev/null",
    "-o", "LogLevel=QUIET",
    "-o", "ConnectTimeout=15"
) -Option Constant
Set-Variable -Name BUFFER_SIZE -Value 65536 -Option Constant  # 64 KiB copy buffer

# NOTE: When using the bash helper with `-Scope ClusterSplit`, the helper
# interprets $Format as DUMP_FORMAT_FLAG — which is a placeholder for the
# positional argument contract. In ClusterSplit mode, the flag is ignored
# (the split path hardcodes `--format=custom` for per-DB and `--globals-only`
# for the globals). `$2` MUST be non-empty — see §3.3 of SKILL.md.
$DumpFormatFlag = $Format

# ── Helper Functions ────────────────────────────────────────────────────────

function Write-Message {
    param([string]$Message, [string]$Color = "White")
    $Timestamp = Get-Date -Format "HH:mm:ss"
    Write-Host "[$Timestamp] $Message" -ForegroundColor $Color
}

function Exit-WithError {
    param([string]$Message)
    Write-Message "Error: $Message" "Red"
    exit 1
}

# ── 0. Dependency Preflight ─────────────────────────────────────────────────
Write-Message "### Starting Industrial Database Synchronization (Single-Session) " "Cyan"
Write-Message "Scope: $Scope, Format: $Format, Dump tool: $DumpTool" "Gray"

$RequiredTools = @("sshpass", "git")
$MissingTools = @()

foreach ($Tool in $RequiredTools) {
    if (-not (Get-Command $Tool -ErrorAction SilentlyContinue)) {
        $MissingTools += $Tool
    }
}

if ($MissingTools.Count -gt 0) {
    Exit-WithError "Missing required local tools: $($MissingTools -join ', '). Install via brew (macOS) or apt (Linux)."
}

# ── 1. Script Discovery ────────────────────────────────────────────────────

function Find-BashScript {
    $ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
    $ScriptPath = Join-Path -Path $ScriptDir -ChildPath $BASH_SCRIPT_NAME
    if (Test-Path $ScriptPath) {
        Write-Message "Found bash helper at '$ScriptPath'" "Green"
        return $ScriptPath
    }
    $FallbackPath = Join-Path -Path $ScriptDir -ChildPath $BASH_SCRIPT_FALLBACK_NAME
    if (Test-Path $FallbackPath) {
        Write-Message "Found bash helper at '$FallbackPath'" "Green"
        return $FallbackPath
    }
    Exit-WithError "Bash helper script not found in '$ScriptDir'."
}

$BashHelperPath = Find-BashScript

# ── 2. SSH Connection & Remote Dump ────────────────────────────────────────
Write-Message "Establishing SSH session to '$User@$ServerHost'..." "Yellow"

$TimeStamp = Get-Date -Format "dd-MM-yyyy-HH-mm"
$PendingDirName = "$DatabasePrefix-$PendingSuffix"
$OutputBaseDir = Resolve-Path $PSScriptRoot/../../$OutputDirName -ErrorAction SilentlyContinue
if (-not $OutputBaseDir) {
    Exit-WithError "Output directory '$OutputDirName' not found relative to script."
}
$PendingDir = Join-Path -Path $OutputBaseDir.Path -ChildPath $PendingDirName

if (Test-Path $PendingDir) {
    Write-Message "Cleaning up existing pending directory: $PendingDirName" "Yellow"
    Remove-Item -Path "$PendingDir\*" -Recurse -Force -ErrorAction SilentlyContinue
} else {
    New-Item -ItemType Directory -Path $PendingDir -Force | Out-Null
}

Write-Message "Streaming payload into pending directory: $PendingDirName" "Yellow"

# Stream the dump directly into the pending directory via SSH + bash pipeline
$env:SSHPASS = $Password

$ProcessInfo = New-Object System.Diagnostics.ProcessStartInfo
$ProcessInfo.FileName = "sshpass"
$ProcessInfo.Arguments = "-e ssh $SSH_OPTS '$User@$ServerHost' bash -s -- '$RemoteEnvPath' '$DumpFormatFlag' '$EnvDbKey' '$DumpTool'"
$ProcessInfo.UseShellExecute = $false
$ProcessInfo.CreateNoWindow = $true
$ProcessInfo.RedirectStandardInput = $true
$ProcessInfo.RedirectStandardOutput = $true
$ProcessInfo.RedirectStandardError = $true

$Process = New-Object System.Diagnostics.Process
$Process.StartInfo = $ProcessInfo

# Read the bash helper script content and pipe it to SSH's stdin
$BashScriptContent = Get-Content -Path $BashHelperPath -Raw
$Process.Start() | Out-Null
$Process.StandardInput.Write($BashScriptContent)
$Process.StandardInput.Close()

$StdoutStream = $Process.StandardOutput.BaseStream
$StderrReader = $Process.StandardError

# Kick off a background job to collect stderr
$StderrJob = Start-Job -ScriptBlock {
    param($Reader)
    $ErrorLines = @()
    while (($Line = $Reader.ReadLine()) -ne $null) {
        $ErrorLines += $Line
    }
    return $ErrorLines
} -ArgumentList $StderrReader

# ── 3. Stream Processor ────────────────────────────────────────────────────

function Read-ClusterSplitStream {
    param(
        [System.IO.Stream]$InputStream,
        [string]$PendingDir,
        [string[]]$TimeZones,
        [string]$DumpTool
    )

    $CreatedFiles = @()
    $HeaderBuffer = New-Object System.Collections.ArrayList
    $ByteBuffer = New-Object byte[] $BUFFER_SIZE
    $PendingPrefix = $PendingDir  # Keep local scope param pass-through

    function Read-UntilLF {
        param([System.IO.Stream]$Stream)
        $HeaderBuffer.Clear()
        while ($true) {
            $ByteVal = $Stream.ReadByte()
            if ($ByteVal -eq -1) { return $null }   # EOF
            if ($ByteVal -eq 0x0A) { break }         # LF
            $null = $HeaderBuffer.Add([byte]$ByteVal)
        }
        if ($HeaderBuffer.Count -eq 0) { return "" }
        return [System.Text.Encoding]::ASCII.GetString($HeaderBuffer.ToArray())
    }

    while ($true) {
        $Header = Read-UntilLF -Stream $InputStream
        if ($Header -eq $null) {
            Write-Message "Unexpected EOF while reading stream header." "Red"
            exit 1
        }
        if ($Header -eq "DONE") {
            Write-Message "Stream complete. All files received." "Green"
            break
        }

        # Match FILE:<name>:<20-digit-size>:
        if ($Header -match '^FILE:(.+):(\d{20}):$') {
            $FileName = $matches[1]
            $FileSize = [long]$matches[2]
            $OutPath = Join-Path -Path $PendingPrefix -ChildPath $FileName
            Write-Message "Receiving: $FileName ($($FileSize) bytes)" "Gray"

            try {
                $OutStream = [System.IO.File]::OpenWrite($OutPath)
                $Remaining = $FileSize
                while ($Remaining -gt 0) {
                    $ReadSize = [Math]::Min($Remaining, $BUFFER_SIZE)
                    $Read = $InputStream.Read($ByteBuffer, 0, $ReadSize)
                    if ($Read -le 0) {
                        Write-Message "Unexpected EOF while reading $FileName" "Red"
                        exit 1
                    }
                    $OutStream.Write($ByteBuffer, 0, $Read)
                    $Remaining -= $Read
                }
                $OutStream.Close()
                Write-Message "Received: $FileName" "Green"
                $CreatedFiles += $OutPath
            } catch {
                Write-Message "Error writing $FileName : $($_.Exception.Message)" "Red"
                exit 1
            }
        } elseif ($Header -match '^ERR:(.+)$') {
            Write-Message "Remote error: $($matches[1])" "Red"
            exit 1
        } else {
            Write-Message "Unknown stream header: $Header" "Red"
            exit 1
        }
    }

    return $CreatedFiles
}

function Read-ClusterStream {
    param(
        [System.IO.Stream]$InputStream,
        [string]$PendingDir,
        [string]$DumpTool
    )

    $FileName = switch ($DumpTool) {
        "pg_dumpall" { "$PendingDir/../$PendingDirName.dump" }
        "pg_dump"    { "$PendingDir/../$PendingDirName.dump" }
    }

    $OutPath = Join-Path -Path (Split-Path $PendingDir -Parent) -ChildPath "$PendingDirName.dump"
    Write-Message "Receiving: $FileName" "Gray"

    try {
        $OutStream = [System.IO.File]::OpenWrite($OutPath)
        $ByteBuffer = New-Object byte[] $BUFFER_SIZE
        while (($Read = $InputStream.Read($ByteBuffer, 0, $BUFFER_SIZE)) -gt 0) {
            $OutStream.Write($ByteBuffer, 0, $Read)
        }
        $OutStream.Close()
        Write-Message "Received: $FileName" "Green"
        return @($OutPath)
    } catch {
        Write-Message "Error writing dump: $($_.Exception.Message)" "Red"
        exit 1
    }
}

# ── 4. Execute Stream Reader ───────────────────────────────────────────────

if ($DumpTool -eq "pg_dumpall_split") {
    $ReceivedFiles = Read-ClusterSplitStream -InputStream $StdoutStream -PendingDir $PendingDir -TimeZones $TimeZones -DumpTool $DumpTool
    $FinalDirName = $PendingDirName
} else {
    $ReceivedFiles = Read-ClusterStream -InputStream $StdoutStream -PendingDir $PendingDir -DumpTool $DumpTool
    $FinalDirName = $PendingDirName
}

# Wait for stderr job and report any remote warnings
$StderrLines = $StderrJob | Wait-Job | Receive-Job
$StderrText = $StderrLines -join "`n"
if (-not [string]::IsNullOrWhiteSpace($StderrText)) {
    Write-Message "Remote warnings/errors:" "Yellow"
    Write-Host $StderrText -ForegroundColor DarkYellow
}

$Process.WaitForExit()
$ExitCode = $Process.ExitCode

# Clean up SSHPASS from environment
Remove-Item Env:SSHPASS -ErrorAction SilentlyContinue

if ($ExitCode -ne 0) {
    Write-Message "SSH process exited with code $ExitCode" "Red"
    if ($StderrText -match "ERR:([a-z_]+)") {
        Exit-WithError "Remote failure: $($matches[1])"
    }
    Exit-WithError "SSH streaming failed (exit code $ExitCode)."
}

# ── 5. Determine Final Directory Name ──────────────────────────────────────

if ($DumpTool -eq "pg_dumpall_split") {
    # Extract timestamp from globals.sql header for the final directory name
    $GlobalsPath = Join-Path -Path $PendingDir -ChildPath "globals.sql"
    if (Test-Path $GlobalsPath) {
        $GlobalsContent = Get-Content -Path $GlobalsPath -TotalCount 5 -Raw
        if ($GlobalsContent -match '-- Started on (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})') {
            $StartedOn = Get-Date $matches[1]
            $FinalDirName = "$DatabasePrefix-cluster-$($StartedOn.ToString('dd-MM-yyyy-HH-mm'))-UTC"
            Write-Message "Extracted dump timestamp from globals: $($StartedOn.ToString('yyyy-MM-dd HH:mm:ss')) UTC" "Green"
        } else {
            Write-Message "Could not parse timestamp from globals.sql; falling back to local clock." "Yellow"
            $FinalDirName = "$PendingDirName-ts"
        }
    } else {
        Write-Message "globals.sql not found in stream; falling back to local clock." "Yellow"
        $FinalDirName = "$PendingDirName-ts"
    }
}

$FinalDir = Join-Path -Path $OutputBaseDir.Path -ChildPath $FinalDirName

# ── 6. Rename Pending Directory ────────────────────────────────────────────
if (Test-Path $FinalDir) {
    Write-Message "Final directory already exists: $FinalDirName" "Yellow"
    Write-Message "Removing existing directory for clean replacement." "Gray"
    Remove-Item -Path $FinalDir -Recurse -Force
}

if ($DumpTool -eq "pg_dumpall_split") {
    Rename-Item -Path $PendingDir -NewName $FinalDirName
    Write-Message "### Cluster dump saved to: $FinalDirName" "Green"
} else {
    Write-Message "### Dump saved to: $FinalDirName" "Green"
}

# ── 7. Git Pipeline ────────────────────────────────────────────────────────

if ($PostDumpAction -ne "None") {
    Write-Message "### Executing Git Pipeline (Action: $PostDumpAction)" "Cyan"

    # Build commit message with timezone conversions
    $UtcTime = (Get-Date).ToUniversalTime()
    $TimeStrings = @()

    # UTC always first
    $TimeStrings += "$($UtcTime.ToString('MMM dd yyyy HH:mm')) UTC"

    # Convert to each provided timezone
    foreach ($TzSpec in $TimeZones) {
        $Parts = $TzSpec -split ':', 2
        if ($Parts.Length -ne 2) {
            Write-Message "Invalid timezone spec: '$TzSpec'. Expected format 'SystemZoneId:Label'." "Yellow"
            continue
        }
        $SystemZoneId = $Parts[0].Trim()
        $Label = $Parts[1].Trim()

        try {
            $TzInfo = [System.TimeZoneInfo]::FindSystemTimeZoneById($SystemZoneId)
            $LocalTime = [System.TimeZoneInfo]::ConvertTimeFromUtc($UtcTime, $TzInfo)
            $TimeStrings += "$($LocalTime.ToString('MMM dd yyyy HH:mm')) $Label"
        } catch {
            Write-Message "Unknown timezone: '$SystemZoneId'. Skipping." "Yellow"
        }
    }

    $CommitMessage = "DB Dump ($(($DatabasePrefix -split '-')[0])): $($TimeStrings -join ', ')"

    Write-Message "Stage: git add $OutputDirName/$FinalDirName" "Gray"
    & git add "$OutputDirName/$FinalDirName" 2>&1 | ForEach-Object { Write-Host $_ -ForegroundColor Gray }
    if ($LASTEXITCODE -ne 0) {
        Exit-WithError "Failed to stage dump directory."
    }

    Write-Message "Stage: git commit -m '$CommitMessage'" "Gray"
    & git commit -m "$CommitMessage" 2>&1 | ForEach-Object { Write-Host $_ -ForegroundColor Gray }
    if ($LASTEXITCODE -ne 0) {
        Exit-WithError "Failed to commit dump."
    }

    if ($PostDumpAction -eq "Push") {
        Write-Message "Stage: git push" "Gray"
        & git push 2>&1 | ForEach-Object { Write-Host $_ -ForegroundColor Gray }
        if ($LASTEXITCODE -ne 0) {
            Exit-WithError "Failed to push dump."
        }
    }
}

Write-Message "### Synchronization Pipeline Validated (Dump Deployed)" "Green"
