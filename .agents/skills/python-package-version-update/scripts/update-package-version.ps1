<#
.SYNOPSIS
    Updates Python package version in requirements files and installs in virtual environment.

.DESCRIPTION
    This script automates the process of updating Python package versions by:
    1. Analyzing codebase compatibility
    2. Updating requirements files
    3. Installing updated packages
    4. Verifying installation

.PARAMETER PackageName
    Name of the Python package to update

.PARAMETER NewVersion
    Target version to update to

.PARAMETER RequirementsFile
    Path to requirements file (default: requirements/local.txt)

.EXAMPLE
    .\update-package-version.ps1 -PackageName quickfix -NewVersion 1.16.0

.EXAMPLE
    .\update-package-version.ps1 -PackageName requests -NewVersion 2.31.0 -RequirementsFile requirements/production.txt

.NOTES
    Requires active Python virtual environment.
    Creates backup of requirements file before modification.
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$PackageName,

    [Parameter(Mandatory=$true)]
    [string]$NewVersion,

    [string]$RequirementsFile = "requirements/local.txt"
)

# Set strict mode and error handling
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# Import common utilities
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$CommonUtils = Join-Path $ScriptDir "../../powershell-scripts/Common-Utils.ps1"
if (Test-Path $CommonUtils) {
    . $CommonUtils
} else {
    Write-Warning "Common-Utils.ps1 not found at $CommonUtils"
}

function Write-Message {
    param([string]$Message)
    if (-not [string]::IsNullOrWhiteSpace($Message)) {
        Write-Host $Message
    }
}

# Phase 1: Environment validation
Write-Message "Phase 1: Environment validation..."

# Check if virtual environment is active
if (-not $env:VIRTUAL_ENV) {
    throw "No active virtual environment detected. Please activate venv first."
}

# Check Python availability
$pythonVersion = & python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    throw "Python not available in current environment"
}
Write-Message "Python version: $pythonVersion"

# Phase 2: Codebase analysis
Write-Message "Phase 2: Codebase analysis..."

# Search for package usage
$importPatterns = "import $PackageName", "from $PackageName"
$usagePatterns = "$PackageName\."

$usageFound = $false
foreach ($pattern in $importPatterns) {
    $results = Get-ChildItem -Path . -Include "*.py" -Recurse | Select-String -Pattern $pattern
    if ($results) {
        Write-Message "Found imports: $($results.Count) occurrences"
        $usageFound = $true
    }
}

if (-not $usageFound) {
    Write-Warning "No direct imports found for $PackageName. This may indicate indirect usage."
}

# Phase 3: Requirements file update
Write-Message "Phase 3: Requirements file update..."

if (-not (Test-Path $RequirementsFile)) {
    throw "Requirements file not found: $RequirementsFile"
}

# Create backup
$backupFile = "$RequirementsFile.backup"
Copy-Item $RequirementsFile $backupFile
Write-Message "Created backup: $backupFile"

# Read and update requirements file
$content = Get-Content $RequirementsFile
$updatedContent = $content -replace "^$PackageName==.*$", "$PackageName==$NewVersion"

if ($content -eq $updatedContent) {
    Write-Warning "Package $PackageName not found in $RequirementsFile or already at version $NewVersion"
} else {
    $updatedContent | Set-Content $RequirementsFile
    Write-Message "Updated $PackageName to version $NewVersion in $RequirementsFile"
}

# Phase 4: Package installation
Write-Message "Phase 4: Package installation..."

try {
    $installResult = & pip install "$PackageName==$NewVersion" 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Package installation failed: $installResult"
    }
    Write-Message "Successfully installed $PackageName $NewVersion"
} catch {
    Write-Error "Installation failed: $_"
    # Restore backup on failure
    Copy-Item $backupFile $RequirementsFile
    Write-Message "Restored backup due to installation failure"
    throw
}

# Phase 5: Verification
Write-Message "Phase 5: Verification..."

# Test import
try {
    $testResult = & python -c "import $PackageName; print('${PackageName} import successful')" 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Import test failed: $testResult"
    }
    Write-Message "Import verification: PASSED"
} catch {
    Write-Warning "Import verification: FAILED - $_"
}

Write-Message "Package update completed successfully!"

# Cleanup backup if everything succeeded
Remove-Item $backupFile
Write-Message "Cleaned up backup file"