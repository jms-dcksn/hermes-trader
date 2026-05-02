# FinAlly AI Trading Workstation - Windows Start Script

Write-Host "Starting FinAlly AI Trading Workstation..." -ForegroundColor Green

# Check if Docker is running
try {
    docker info | Out-Null
} catch {
    Write-Host "Docker is not running. Please start Docker Desktop and try again." -ForegroundColor Red
    exit 1
}

# Check for .env file
if (-not (Test-Path .env)) {
    Write-Host "No .env file found. Creating .env.example..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "Please edit .env file and add your OpenRouter API key." -ForegroundColor Yellow
    exit 1
}

# Parse command line arguments
$Build = $false
$OpenBrowser = $true

foreach ($arg in $args) {
    switch ($arg) {
        "--build" { $Build = $true }
        "--no-browser" { $OpenBrowser = $false }
        default {
            Write-Host "Unknown option: $arg" -ForegroundColor Red
            Write-Host "Usage: .\start_windows.ps1 [--build] [--no-browser]" -ForegroundColor Yellow
            exit 1
        }
    }
}

# Check if image exists
$ImageExists = docker images -q finally:latest

if ($Build -or (-not $ImageExists)) {
    Write-Host "Building Docker image..." -ForegroundColor Yellow
    docker build -t finally:latest .
}

# Check if container is already running
$ContainerId = docker ps -q -f "name=finally-app"

if ($ContainerId) {
    Write-Host "Container is already running. Stopping it first..." -ForegroundColor Yellow
    docker stop finally-app | Out-Null
    docker rm finally-app | Out-Null
}

# Run the container
Write-Host "Starting container..." -ForegroundColor Green
docker run -d `
    --name finally-app `
    -p 8000:8000 `
    -v finally-data:/app/db `
    --env-file .env `
    finally:latest | Out-Null

# Wait for container to start
Write-Host "Waiting for application to start..." -ForegroundColor Yellow
for ($i = 1; $i -le 30; $i++) {
    try {
        $null = Invoke-RestMethod -Uri "http://localhost:8000/api/health" -TimeoutSec 1
        Write-Host ""
        Write-Host "Application is running!" -ForegroundColor Green
        Write-Host ""
        Write-Host "=========================================="
        Write-Host "FinAlly AI Trading Workstation"
        Write-Host "=========================================="
        Write-Host "Local:    http://localhost:8000"
        Write-Host "API Docs: http://localhost:8000/docs"
        Write-Host ""
        Write-Host "Default portfolio: `$10,000 virtual cash"
        Write-Host "Default watchlist: 10 popular stocks"
        Write-Host "=========================================="
        
        # Open browser if requested
        if ($OpenBrowser) {
            Start-Process "http://localhost:8000"
        }
        
        exit 0
    } catch {
        Write-Host "." -NoNewline
        Start-Sleep -Seconds 1
    }
}

Write-Host ""
Write-Host "Failed to start application. Check logs with: docker logs finally-app" -ForegroundColor Red
exit 1