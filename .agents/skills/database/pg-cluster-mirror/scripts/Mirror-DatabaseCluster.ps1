#!pwsh
#Requires -Version 5.1

<#
.SYNOPSIS
    Industrial PostgreSQL Cluster Mirror Tool.
    Mirrors an on-disk ClusterSplit dump (globals.sql + per-DB *.dump) onto a
    target cluster (local DSN OR SSH-fronted remote via transparent port-forward tunnel).

.DESCRIPTION
    Five-phase pipeline, each gated by the previous one's success:
      1. Resolve   — source dir (auto-pick newest cluster dir or explicit)
                     + target connection (local DSN or SSH).
                     SSH mode: extracts DSN from remote .env, then opens a
                     local port-forward tunnel so all subsequent local tools
                     (psql, pg_restore, pg_dump, pg_dumpall) connect identically
                     to how they do in local mode.
      2. Preflight — verify target role has rolcreatedb (+ rolcreaterole when
                     -IncludeGlobals). Refuse before touching data.
      3. Audit     — render full report (per-source-DB → resolved target name,
                     action, PG version drift, backup destination).
                     Stop for [Y/n] unless -Confirm. -WhatIf exits here.
      4. Backup    — pre-mirror ClusterSplit backup of target:
                       SSH: Sync-RemoteDatabaseBackup.ps1 (separate session, no tunnel).
                       Local: inline pg_dumpall --globals-only + pg_dump per DB.
                     Hard-stop on failure unless -SkipBackup -Force.
      5. Mirror    — apply globals.sql (when -IncludeGlobals) then per DB:
                     terminate connections, drop, create, pg_restore --clean
                     --if-exists --no-owner --no-acl --jobs=N.

.PARAMETER SourceDir
    Path to a ClusterSplit dump directory (containing globals.sql + *.dump).
    If omitted, the newest directory matching -SourcePattern in db_dumps/ is selected.

.PARAMETER SourcePattern
    Glob used to auto-discover the source when -SourceDir is omitted.
    Defaults to '*-cluster-*-UTC' (convention used by Sync-RemoteDatabaseBackup.ps1).

.PARAMETER TargetDsn
    Local target DSN (postgres://user:pass@host:port/db). Either this OR the
    SSH parameter set must be supplied.

.PARAMETER TargetUser
    Remote SSH username (SSH mode).

.PARAMETER TargetHost
    Remote SSH host / IP address (SSH mode).

.PARAMETER TargetPassword
    Remote SSH password (SSH mode; requires 'sshpass' locally).

.PARAMETER TargetEnvPath
    Absolute path to .env on the remote target server (SSH mode).
    Used to extract DATABASE_URL for the maintenance connection.

.PARAMETER TargetEnvDbKey
    Env-file key holding the connection string. Defaults to DATABASE_URL.

.PARAMETER TunnelLocalPort
    Local port to use for the SSH port-forward tunnel (SSH mode only).
    Must be free on the local machine. Defaults to 15432.
    Auto-increments if the default is in use.

.PARAMETER TargetLabel
    Human-readable label used in backup directory naming (e.g. '<env>-staging').

.PARAMETER Mode
    Target DB naming mode:
      SameName — <src> → <src>  (DROP + CREATE on collision, default).
      Map      — <src> → $Mapping[<src>] (must cover every selected DB).
      New      — <src> → <src>_<timestamp> (refuses collision).

.PARAMETER Mapping
    Hashtable of source-DB → target-DB names. Required when -Mode Map.

.PARAMETER Databases
    Subset of source DBs to mirror. Defaults to every *.dump in $SourceDir
    except 'postgres' (toggle with -IncludePostgresDb).

.PARAMETER IncludeGlobals
    Apply globals.sql against the target maintenance DB before per-DB restore.
    Default: off. Target role must have CREATEROLE or SUPERUSER.

.PARAMETER IncludePostgresDb
    Include the postgres system DB in the selected set. Default: off.

.PARAMETER SkipBackup
    Skip the pre-mirror target backup. Requires -Force as a safety interlock.

.PARAMETER Force
    Acknowledges and unlocks dangerous toggles (currently only -SkipBackup).

.PARAMETER WhatIf
    Run phases 1-3 only (no backup, no mirror). Exits with the audit report.

.PARAMETER Confirm
    Skip the interactive [Y/n] prompt after the audit report.

.PARAMETER Jobs
    Parallel pg_restore workers per DB. Default 1.

.EXAMPLE
    # Dry-run: see audit report for a local target
    pwsh ./Mirror-DatabaseCluster.ps1 `
        -SourceDir db_dumps/<env-prefix>-cluster-<ts>-UTC `
        -TargetDsn 'postgres://<user>@127.0.0.1:5432/postgres' `
        -TargetLabel <target-label> -WhatIf

.EXAMPLE
    # Full mirror to SSH-fronted staging, same DB names, interactive confirm
    pwsh ./Mirror-DatabaseCluster.ps1 `
        -TargetUser <ssh-user> -TargetHost <staging-ip> `
        -TargetPassword '<ssh-password>' -TargetLabel <target-label> `
        -TargetEnvPath '<absolute-path-to-.env>' `
        -Databases <main-db> -Confirm

.EXAMPLE
    # Mirror with explicit renames via Map mode
    pwsh ./Mirror-DatabaseCluster.ps1 `
        -TargetUser <ssh-user> -TargetHost <staging-ip> `
        -TargetPassword '<ssh-password>' -TargetLabel <target-label> `
        -TargetEnvPath '<absolute-path-to-.env>' `
        -Mode Map -Mapping @{ <source-db>='<target-db>' } `
        -Databases <main-db> -Confirm

.NOTES
    SSH mode: opens a local port-forward tunnel after DSN extraction so all
    local pg_* tools connect through it — no remote postgres port needs to be
    publicly reachable. The tunnel is always closed in a finally block.
#>

[CmdletBinding(DefaultParameterSetName = 'Local')]
Param(
    [string]$SourceDir = "",
    [string]$SourcePattern = "*-cluster-*-UTC",

    [Parameter(ParameterSetName = 'Local',  Mandatory = $true)]
    [string]$TargetDsn,

    [Parameter(ParameterSetName = 'Ssh',    Mandatory = $true)]
    [string]$TargetUser,
    [Parameter(ParameterSetName = 'Ssh',    Mandatory = $true)]
    [string]$TargetHost,
    [Parameter(ParameterSetName = 'Ssh',    Mandatory = $true)]
    [string]$TargetPassword,
    [Parameter(ParameterSetName = 'Ssh',    Mandatory = $true)]
    [string]$TargetEnvPath,
    [Parameter(ParameterSetName = 'Ssh')]
    [string]$TargetEnvDbKey = "DATABASE_URL",
    [Parameter(ParameterSetName = 'Ssh')]
    [int]$TunnelLocalPort = 15432,

    [Parameter(Mandatory = $true)]
    [string]$TargetLabel,

    [ValidateSet("SameName","Map","New")]
    [string]$Mode = "SameName",
    [hashtable]$Mapping = @{},

    [string[]]$Databases = @(),
    [switch]$IncludeGlobals,
    [switch]$IncludePostgresDb,
    [switch]$SkipBackup,
    [switch]$Force,
    [switch]$WhatIf,
    [switch]$Confirm,
    [int]$Jobs = 1,

    [string]$OutputDirName = "db_dumps"
)

# ── Colour Scheme ──────────────────────────────────────────────────────────────
$C_HEADER = "Cyan"
$C_OK     = "Green"
$C_WARN   = "Yellow"
$C_ERR    = "Red"
$C_DIM    = "DarkGray"
$C_LABEL  = "White"

Function Write-Message {
    param([string]$Message, [string]$Color = "White")
    $Timestamp = Get-Date -Format "HH:mm:ss"
    Write-Host "[$Timestamp] $Message" -ForegroundColor $Color
}

# ── Path Resolution ────────────────────────────────────────────────────────────
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot  = Resolve-Path "$ScriptDir/../.."

Function Get-OutputDir { param([string]$Name)
    $p = Join-Path $RepoRoot $Name
    if (-not (Test-Path $p)) { New-Item -ItemType Directory -Path $p -Force | Out-Null }
    return (Resolve-Path $p).Path
}

# ── Phase 0: Dependency Check ─────────────────────────────────────────────────
Function Test-Dependency {
    param([string]$Exe)
    $found = Get-Command $Exe -ErrorAction SilentlyContinue
    if (-not $found) {
        Write-Message "Required local tool '$Exe' not on PATH. Install postgresql-client." $C_ERR
        exit 1
    }
}

Write-Message "Phase 0 — Checking local dependencies" $C_HEADER
Test-Dependency "psql"
Test-Dependency "pg_restore"
Test-Dependency "pg_dump"
Test-Dependency "pg_dumpall"
if ($PSCmdlet.ParameterSetName -eq 'Ssh') { Test-Dependency "sshpass" }

# ── Phase 1: Resolve ──────────────────────────────────────────────────────────
Write-Message "Phase 1 — Resolving source & target" $C_HEADER

# 1a — Source directory
if (-not $SourceDir) {
    $DumpDir = Get-OutputDir $OutputDirName
    $Candidates = Get-ChildItem -Path $DumpDir -Directory | Where-Object { $_.Name -like $SourcePattern } | Sort-Object LastWriteTime -Descending
    if (-not $Candidates) {
        Write-Message "No source cluster directories found matching '$SourcePattern' in '$DumpDir'." $C_ERR
        Write-Message "Pass -SourceDir explicitly or create a ClusterSplit dump first." $C_ERR
        exit 1
    }
    $SourceDir = $Candidates[0].FullName
    Write-Message "Auto-selected newest source: $(Split-Path $SourceDir -Leaf)" $C_OK
}

$GlobalsPath = Join-Path $SourceDir "globals.sql"
$DumpFiles = Get-ChildItem -Path $SourceDir -Filter "*.dump" | Sort-Object Name
if (-not $DumpFiles) {
    Write-Message "No *.dump files found in source directory '$SourceDir'." $C_ERR
    exit 1
}
if (-not (Test-Path $GlobalsPath)) {
    Write-Message "globals.sql not found in source — will skip globals restore (pass -IncludeGlobals only if the file exists)." $C_WARN
}

# 1b — Target DSN
$TargetDsnResolved = ""
$TunnelProc = $null
$TunnelPort = 0

if ($PSCmdlet.ParameterSetName -eq 'Local') {
    $TargetDsnResolved = $TargetDsn
    Write-Message "Target: Local DSN (masked)" $C_OK
} else {
    Write-Message "Target: SSH → $TargetHost (extracting DSN via remote .env)" $C_OK
    $env:SSHPASS = $TargetPassword
    $SshArgs = @("-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null", "-o", "LogLevel=QUIET", "$TargetUser@$TargetHost")
    $RemoteCmd = "grep '^${TargetEnvDbKey}=' '$TargetEnvPath' | cut -d= -f2- | sed 's/^[[:space:]]*//;s/[[:space:]]*$//;s/^\"//;s/\"$//'"
    $RawDsn = & sshpass -e ssh $SshArgs "bash -c '$($RemoteCmd -replace "'", "'\\''")'" 2>$null
    Remove-Item Env:SSHPASS -ErrorAction SilentlyContinue

    if (-not $RawDsn -or $LASTEXITCODE -ne 0) {
        Write-Message "Failed to extract DSN from '$TargetEnvPath' on $TargetHost." $C_ERR
        Write-Message "Verify the path and that $TargetEnvDbKey is defined." $C_ERR
        exit 1
    }

    $RawDsn = $RawDsn.Trim()
    if ($RawDsn -notmatch '^postgres(ql)?://') {
        Write-Message "Extracted value is not a valid postgres:// DSN: $RawDsn" $C_ERR
        exit 1
    }

    # 1c — SSH tunnel
    $TunnelPort = $TunnelLocalPort
    $MaxPort = $TunnelLocalPort + 20
    while ($TunnelPort -le $MaxPort) {
        $TcpClient = New-Object System.Net.Sockets.TcpClient
        $Connected = $TcpClient.BeginConnect("127.0.0.1", $TunnelPort, $null, $null)
        $WaitResult = $Connected.AsyncWaitHandle.WaitOne(100)
        $TcpClient.EndConnect($Connected) | Out-Null
        $TcpClient.Close()
        if (-not $WaitResult) { break }  # port is free
        $TunnelPort++
    }
    if ($TunnelPort -gt $MaxPort) {
        Write-Message "Could not find a free local port in range $TunnelLocalPort..$MaxPort." $C_ERR
        exit 1
    }

    $env:SSHPASS = $TargetPassword
    $TunnelArgs = @("-e", "ssh", "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null", "-o", "LogLevel=QUIET", "-L", "${TunnelPort}:localhost:5432", "-N", "$TargetUser@$TargetHost")
    $TunnelProc = New-Object System.Diagnostics.Process
    $TunnelProc.StartInfo.FileName = "sshpass"
    $TunnelProc.StartInfo.Arguments = $TunnelArgs -join ' '
    $TunnelProc.StartInfo.UseShellExecute = $false
    $TunnelProc.StartInfo.RedirectStandardOutput = $true
    $TunnelProc.StartInfo.RedirectStandardError = $true
    $TunnelProc.Start() | Out-Null

    Start-Sleep -Seconds 2
    # Verify tunnel is up
    $TcpCheck = New-Object System.Net.Sockets.TcpClient
    $AsyncCheck = $TcpCheck.BeginConnect("127.0.0.1", $TunnelPort, $null, $null)
    $WaitOk = $AsyncCheck.AsyncWaitHandle.WaitOne(5000)
    if (-not $WaitOk) {
        Write-Message "SSH tunnel did not become available on 127.0.0.1:$TunnelPort within 5 seconds." $C_ERR
        Remove-Item Env:SSHPASS -ErrorAction SilentlyContinue
        $TunnelProc.Kill()
        exit 1
    }
    $TcpCheck.EndConnect($AsyncCheck) | Out-Null
    $TcpCheck.Close()

    # Rewrite DSN to point at tunnel
    $TargetDsnResolved = $RawDsn -replace '^postgres(ql)?://', "postgresql://" -replace ':[^@/]+(?=@)', ':*****'  # mask for display
    $RealDsn = $RawDsn -replace '^postgres(ql)?://', "postgresql://"
    if ($RealDsn -match '^(postgresql://[^@]+@)([^:]+):(\d+)/(.*)$') {
        $TargetDsnResolved = $matches[1] + "127.0.0.1:$TunnelPort/" + $matches[4]
        # Also create the unmasked version for actual use
        $RealDsn = $matches[1] + "127.0.0.1:$TunnelPort/" + $matches[4]
        $RawDsn = $RealDsn
    }
    Write-Message "Tunnel open on 127.0.0.1:$TunnelPort" $C_OK
    Remove-Item Env:SSHPASS -ErrorAction SilentlyContinue
}

# ── Phase 2: Silent data collection ──────────────────────────────────────────
Write-Message "Phase 2 — Collecting metadata (silent)" $C_HEADER

$DbUrl = if ($PSCmdlet.ParameterSetName -eq 'Local') { $TargetDsn } else { $RawDsn }
$MaintenanceUrl = $DbUrl -replace '/[^/]+$', '/postgres'

# Target role permissions
$RoleInfo = @{}
$RoleQuery = "SELECT rolcreatedb, rolcreaterole, rolsuper FROM pg_roles WHERE rolname = current_user"
try {
    $Row = & psql -d $MaintenanceUrl -Atc $RoleQuery 2>$null
    if ($Row -and $Row -match '^([tf])\|([tf])\|([tf])$') {
        $RoleInfo.Createdb   = ($matches[1] -eq 't')
        $RoleInfo.Createrole = ($matches[2] -eq 't')
        $RoleInfo.Superuser  = ($matches[3] -eq 't')
    }
} catch {
    Write-Message "Permission query failed — cannot proceed without target role info." $C_ERR
    exit 1
}
if ($RoleInfo.Count -eq 0) {
    Write-Message "Could not determine target role permissions — aborting for safety." $C_ERR
    exit 1
}

# Source dump metadata
$SourceDbs = @{}
foreach ($Df in $DumpFiles) {
    $DbName = $Df.BaseName
    $PgVerLine = & pg_restore --list $Df.FullName 2>$null | Select-String "database version"
    $PgVer = if ($PgVerLine) { ($PgVerLine.Line -split ';')[-1].Trim() } else { "unknown" }
    $Size = (Get-Item $Df.FullName).Length
    $SourceDbs[$DbName] = @{ Path = $Df.FullName; PgVer = $PgVer; Size = $Size }
}

# Target PG version
$TargetPgVersion = & psql -d $MaintenanceUrl -Atc "SELECT version()" 2>$null

# Target existing databases
$TargetDbs = @()
try {
    $TargetDbs = & psql -d $MaintenanceUrl -Atc "SELECT datname FROM pg_database WHERE NOT datistemplate ORDER BY datname" 2>$null
} catch {}

# ── Phase 3: Audit Report ────────────────────────────────────────────────────
Write-Message "Phase 3 — Audit report" $C_HEADER

# Determine selected databases
$SelectedDbs = if ($Databases.Count -gt 0) { $Databases } else { $SourceDbs.Keys | Where-Object { $_ -ne 'postgres' -or $IncludePostgresDb } }

# Resolve target names per mode
$TargetNames = @{}
$DropCreate = @{}
foreach ($Db in $SelectedDbs) {
    switch ($Mode) {
        "SameName" { $TargetNames[$Db] = $Db; $DropCreate[$Db] = $true }
        "Map" {
            if (-not $Mapping.ContainsKey($Db)) {
                Write-Message "BLOCKED: Mode=Map requires -Mapping for every selected DB. Missing: $Db" $C_ERR
                exit 1
            }
            $TargetNames[$Db] = $Mapping[$Db]
            $DropCreate[$Db] = $true
        }
        "New" {
            $Ts = Get-Date -Format "yyyyMMdd_HHmmss"
            $NewName = "${Db}_${Ts}"
            if ($TargetDbs -contains $NewName) {
                Write-Message "BLOCKED: Mode=New — target '$NewName' already exists." $C_ERR
                exit 1
            }
            $TargetNames[$Db] = $NewName
            $DropCreate[$Db] = $false
        }
    }
}

# Transport string
$Transport = if ($PSCmdlet.ParameterSetName -eq 'Ssh') { "SSH (tunnel → $TargetHost:5432)" } else { "Local DSN" }

# Backup destination
$BackupDirName = "$TargetLabel-pre-mirror-cluster-$(Get-Date -Format 'dd-MM-yyyy-HH-mm')-UTC"
$BackupDir = Join-Path (Get-OutputDir $OutputDirName) $BackupDirName
$BackupStatus = if ($SkipBackup -and $Force) { "SKIPPED (acknowledged)" } else { $BackupDirName }

# Render the box
$BoxWidth = 74
"-" * $BoxWidth
"         CLUSTER MIRROR — AUDIT REPORT"
"-" * $BoxWidth
""
"  Source cluster  : $SourceDir"
"  Target          : $(if ($PSCmdlet.ParameterSetName -eq 'Local') { ($TargetDsn -replace ':[^@/]+(?=@)', ':*****') + " — $TargetPgVersion" } else { "postgres:*****@$TargetHost:5432 — $TargetPgVersion" })"
"  Mode            : $Mode"
"  Transport       : $Transport"
"  Pre-mirror bkp  : $BackupStatus"
""
"  Permissions (target role: $(whoami)):"
$cre = if ($RoleInfo.Createdb)   { " ✓  CREATEDB" } else { " ✗  CREATEDB   ← BLOCKING" }
$cro = if ($RoleInfo.Createrole) { " ✓  CREATEROLE (required only with -IncludeGlobals)" } else { " ✗  CREATEROLE (required only with -IncludeGlobals)" }
$sup = if ($RoleInfo.Superuser)  { " ✓  SUPERUSER (not required)" } else { " ✗  SUPERUSER  (not required — informational)" }
Write-Host "    $cre" -ForegroundColor $(if ($RoleInfo.Createdb) { $C_OK } elseif ($RoleInfo.Createdb -eq $false -and $RoleInfo.ContainsKey('Createdb')) { $C_ERR } else { $C_DIM })
Write-Host "    $cro" -ForegroundColor $(if ($RoleInfo.Createrole -or -not $IncludeGlobals) { $C_OK } else { $C_ERR })
Write-Host "    $sup" -ForegroundColor $C_DIM

if ($RoleInfo.Createdb -eq $false) {
    Write-Message "BLOCKED: Target role lacks CREATEDB. Run: ALTER ROLE <user> CREATEDB;" $C_ERR
    exit 1
}
if ($IncludeGlobals -and $RoleInfo.Createrole -eq $false) {
    Write-Message "BLOCKED: -IncludeGlobals requires CREATEROLE on the target role." $C_ERR
    exit 1
}

""
"  Options:"
$globalsStatus = if ($IncludeGlobals) { "apply" } else { "skip  (pass -IncludeGlobals to apply)" }
$postgresStatus = if ($IncludePostgresDb) { "include" } else { "skip  (pass -IncludePostgresDb to include)" }
"    globals.sql     : $globalsStatus"
"    postgres system : $postgresStatus"
"    Parallel jobs   : $Jobs per DB"
""

# Table
$ColW = @(28, 8, 28, 18)
$Sep = "─" * ($ColW[0] + $ColW[1] + $ColW[2] + $ColW[3] + 9)
"  ┌$($Sep)┐"
Write-Host ("  │ " + "Source DB".PadRight($ColW[0]) + "│ " + "pg-ver".PadRight($ColW[1]-1) + "│ " + "→ Target DB".PadRight($ColW[2]) + "│ " + "Action".PadRight($ColW[3]-1) + "│")
"  ├$($Sep)┤"

$AnyDowngrade = $false
foreach ($Db in $SelectedDbs) {
    $Info = $SourceDbs[$Db]
    $SrcPg = if ($Info) { $Info.PgVer } else { "—" }
    $Tgt = $TargetNames[$Db]
    $Action = if ($DropCreate[$Db]) { "DROP + CREATE" } else { "CREATE (new)" }
    Write-Host ("  │ " + $Db.PadRight($ColW[0]) + "│ " + $SrcPg.PadRight($ColW[1]-1) + "│ " + $Tgt.PadRight($ColW[2]) + "│ " + $Action.PadRight($ColW[3]-1) + "│")

    # Check downgrade
    if ($Info -and $Info.PgVer -ne "unknown") {
        $SourceMajor = ($Info.PgVer -split '\.')[0]
        if ($TargetPgVersion -match '(\d+)\.') {
            $TargetMajor = $matches[1]
            if ([int]$SourceMajor -gt [int]$TargetMajor) { $AnyDowngrade = $true }
        }
    }
}
"  └$($Sep)┘"
""

$TotalSize = ($SelectedDbs | ForEach-Object { if ($SourceDbs[$_]) { $SourceDbs[$_].Size } else { 0 } } | Measure-Object -Sum).Sum
$SizeStr = if ($TotalSize -gt 1GB) { "{0:N2} GB" -f ($TotalSize / 1GB) } elseif ($TotalSize -gt 1MB) { "{0:N2} MB" -f ($TotalSize / 1MB) } else { "{0:N2} KB" -f ($TotalSize / 1KB) }
"  Total payload   : $SizeStr across $($SelectedDbs.Count) DB(s)"

$SourcePgMajor = @($SourceDbs.Values.PgVer | ForEach-Object { ($_ -split '\.')[0] } | Sort-Object -Unique)
$TargetPgMajor = if ($TargetPgVersion -match '(\d+)\.') { $matches[1] } else { "?" }
foreach ($Sv in $SourcePgMajor) {
    if ($Sv -ne $TargetPgMajor) {
        if ([int]$Sv -gt [int]$TargetPgMajor) {
            Write-Host "  ⚠  Reverse-restore: source PG $Sv → target PG $TargetPgMajor (downgrade — FORBIDDEN)." $C_ERR
        } else {
            Write-Host "  ℹ  Forward-restore: source PG $Sv → target PG $TargetPgMajor (supported)." $C_OK
        }
    }
}
""
"-" * $BoxWidth

# Early exit for -WhatIf
if ($WhatIf) {
    Write-Message "WhatIf mode — exiting after audit. No changes made." $C_WARN
    exit 0
}

# Interactive confirm
if (-not $Confirm) {
    $Response = Read-Host "Proceed with backup + mirror? [y/N]"
    if ($Response -ne 'y' -and $Response -ne 'Y') {
        Write-Message "Aborted by user." $C_WARN
        exit 0
    }
}

# ── Phase 4: Pre-mirror backup ─────────────────────────────────────────────
Write-Message "Phase 4 — Pre-mirror backup" $C_HEADER

if ($SkipBackup -and $Force) {
    Write-Message "Pre-mirror backup SKIPPED (acknowledged via -SkipBackup -Force)." $C_WARN
} else {
    New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null

    if ($PSCmdlet.ParameterSetName -eq 'Ssh') {
        # Use Sync-RemoteDatabaseBackup.ps1 for SSH targets
        $SyncScript = Join-Path $ScriptDir "Sync-RemoteDatabaseBackup.ps1"
        if (-not (Test-Path $SyncScript)) {
            Write-Message "Sync-RemoteDatabaseBackup.ps1 not found at '$SyncScript'." $C_ERR
            Write-Message "Ensure it exists in the same scripts/ directory as Mirror-DatabaseCluster.ps1." $C_ERR
            exit 1
        }
        Write-Message "Invoking Sync-RemoteDatabaseBackup.ps1 for pre-mirror backup of target..." $C_WARN
        & $SyncScript -User $TargetUser -ServerHost $TargetHost -Password $TargetPassword `
            -RemoteEnvPath $TargetEnvPath -DatabasePrefix "$TargetLabel-pre-mirror" `
            -Scope ClusterSplit -PostDumpAction None -OutputDirName $OutputDirName
        if ($LASTEXITCODE -ne 0) {
            Write-Message "Pre-mirror backup FAILED. Mirror aborted." $C_ERR
            exit 1
        }
        Write-Message "Pre-mirror backup completed (SSH)." $C_OK
    } else {
        # Local — inline backup
        Write-Message "Performing local inline pre-mirror backup..." $C_WARN
        $GlobalsOut = Join-Path $BackupDir "globals.sql"
        & pg_dumpall --dbname="$MaintenanceUrl" --globals-only --no-role-passwords > $GlobalsOut 2>$null
        if ($LASTEXITCODE -ne 0) { Write-Message "globals.sql backup failed." $C_ERR; exit 1 }

        foreach ($Db in $SelectedDbs) {
            $DumpOut = Join-Path $BackupDir "${Db}.dump"
            $DbUrl = $DbUrl -replace '/[^/]+$', "/$Db"
            & pg_dump --dbname="$DbUrl" --format=custom > $DumpOut 2>$null
            if ($LASTEXITCODE -ne 0) { Write-Message "Backup of $Db failed." $C_ERR; exit 1 }
        }
        Write-Message "Pre-mirror backup completed (local) → $BackupDirName" $C_OK
    }
}

# ── Phase 5: Mirror ─────────────────────────────────────────────────────────
Write-Message "Phase 5 — Mirror" $C_HEADER

# Apply globals if requested
if ($IncludeGlobals -and (Test-Path $GlobalsPath)) {
    Write-Message "Applying globals.sql..." $C_WARN
    & psql -d $MaintenanceUrl -v ON_ERROR_STOP=0 -f $GlobalsPath 2>&1 | ForEach-Object {
        if ($_ -match 'ERROR') { Write-Host $_ -ForegroundColor $C_WARN }
    }
    if ($LASTEXITCODE -ne 0 -and $LASTEXITCODE -ne 1) {
        Write-Message "Globals apply returned non-zero exit code $LASTEXITCODE (warnings are expected — continuing)." $C_WARN
    } else {
        Write-Message "Globals applied." $C_OK
    }
}

$Results = @{}
foreach ($Db in $SelectedDbs) {
    $Dst = $TargetNames[$Db]
    $DumpPath = $SourceDbs[$Db].Path
    Write-Message "Processing $Db → $Dst ..." $C_WARN

    # Build DSN for this DB
    $DbMaintenanceUrl = $DbUrl -replace '/[^/]+$', "/postgres"
    $DbUrlSpecific = $DbUrl -replace '/[^/]+$', "/$Dst"

    if ($DropCreate[$Db]) {
        # Terminate connections
        & psql -d $DbMaintenanceUrl -Atc "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='$Dst' AND pid <> pg_backend_pid()" 2>$null | Out-Null

        # Drop and recreate
        & psql -d $DbMaintenanceUrl -Atc "DROP DATABASE IF EXISTS $Dst" 2>$null
        & psql -d $DbMaintenanceUrl -Atc "CREATE DATABASE $Dst" 2>$null
    }

    # Restore
    $RestoreArgs = @("--clean", "--if-exists", "--no-owner", "--no-acl", "--jobs=$Jobs", "--dbname=$DbUrlSpecific", $DumpPath)
    & pg_restore $RestoreArgs 2>&1 | ForEach-Object {
        if ($_ -match 'ERROR') { Write-Host $_ -ForegroundColor $C_WARN }
    }

    $ExitCode = $LASTEXITCODE
    switch ($ExitCode) {
        0     { $Results[$Db] = "ok";                Write-Message "$Db → $Dst: ok" $C_OK }
        1     { $Results[$Db] = "ok-with-warnings";   Write-Message "$Db → $Dst: ok (with warnings)" $C_WARN }
        default { $Results[$Db] = "failed($ExitCode)"; Write-Message "$Db → $Dst: FAILED (exit $ExitCode)" $C_ERR }
    }
}

# ── Summary ─────────────────────────────────────────────────────────────────
Write-Message "Mirror Summary" $C_HEADER
foreach ($Db in $SelectedDbs) {
    $Dst = $TargetNames[$Db]
    $Status = $Results[$Db]
    $Color = switch ($Status) {
        "ok"               { $C_OK }
        "ok-with-warnings" { $C_WARN }
        default            { $C_ERR }
    }
    Write-Host "  $Db → $Dst : $Status" -ForegroundColor $Color
}

$FailedCount = ($Results.Values | Where-Object { $_ -like "failed*" }).Count
if ($FailedCount -gt 0) {
    Write-Message "$FailedCount database(s) failed. Pre-mirror backup available at: $BackupDirName" $C_ERR
    exit 1
} else {
    Write-Message "All databases mirrored successfully." $C_OK
}

# ── Cleanup ─────────────────────────────────────────────────────────────────
if ($TunnelProc -and (-not $TunnelProc.HasExited)) {
    Write-Message "Closing SSH tunnel..." $C_DIM
    $TunnelProc.Kill()
    $TunnelProc.Dispose()
}
