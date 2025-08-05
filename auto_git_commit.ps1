# Auto Git Commit Script - Runs every 3 hours
# Location: C:\Users\ianki\OneDrive\2. Projects\ClaudeCode_New\PrimePath_

param(
    [string]$ProjectPath = "C:\Users\ianki\OneDrive\2. Projects\ClaudeCode_New\PrimePath_"
)

# Set location to project directory
Set-Location -Path $ProjectPath

# Get current timestamp
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

try {
    # Check if there are any changes
    $gitStatus = git status --porcelain
    
    if ($gitStatus) {
        Write-Host "[$timestamp] Changes detected, creating auto-commit..."
        
        # Add all changes
        git add .
        
        # Create commit with timestamp
        $commitMessage = "Auto-commit: $timestamp`n`n🤖 Automated backup commit`n`nGenerated every 3 hours for version control safety."
        git commit -m $commitMessage
        
        # Push to remote
        try {
            git push origin main
            Write-Host "[$timestamp] Successfully pushed changes to remote repository"
        }
        catch {
            Write-Host "[$timestamp] Warning: Could not push to remote - $($_.Exception.Message)"
            Write-Host "[$timestamp] Local commit created successfully"
        }
        
        # Log the action
        $logEntry = "[$timestamp] Auto-commit created and pushed"
        Add-Content -Path "$ProjectPath\auto_git.log" -Value $logEntry
        
    } else {
        Write-Host "[$timestamp] No changes detected, skipping commit"
        $logEntry = "[$timestamp] No changes detected"
        Add-Content -Path "$ProjectPath\auto_git.log" -Value $logEntry
    }
}
catch {
    $errorMsg = "[$timestamp] Error during auto-commit: $($_.Exception.Message)"
    Write-Host $errorMsg
    Add-Content -Path "$ProjectPath\auto_git.log" -Value $errorMsg
}

# Keep log file manageable (last 100 entries)
$logFile = "$ProjectPath\auto_git.log"
if (Test-Path $logFile) {
    $logContent = Get-Content $logFile
    if ($logContent.Count -gt 100) {
        $logContent | Select-Object -Last 100 | Set-Content $logFile
    }
}