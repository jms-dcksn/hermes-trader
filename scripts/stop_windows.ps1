# FinAlly AI Trading Workstation - Windows Stop Script

Write-Host "Stopping FinAlly AI Trading Workstation..." -ForegroundColor Yellow

# Check if container is running
$ContainerId = docker ps -q -f "name=finally-app"

if ($ContainerId) {
    Write-Host "Stopping container..." -ForegroundColor Yellow
    docker stop finally-app | Out-Null
    
    Write-Host "Removing container..." -ForegroundColor Yellow
    docker rm finally-app | Out-Null
    
    Write-Host "Container stopped and removed." -ForegroundColor Green
    Write-Host "Note: Database volume (finally-data) is preserved." -ForegroundColor Yellow
} else {
    Write-Host "Container is not running." -ForegroundColor Yellow
}

# Check for other running containers with the same image
$OtherContainers = docker ps -q -f "ancestor=finally:latest"
if ($OtherContainers) {
    Write-Host "Other containers using the finally image are still running." -ForegroundColor Yellow
    Write-Host "Container IDs: $OtherContainers"
    Write-Host "Stop them with: docker stop <container_id>"
}

Write-Host "Done." -ForegroundColor Green