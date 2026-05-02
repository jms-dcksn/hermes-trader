#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting FinAlly AI Trading Workstation...${NC}"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Docker is not running. Please start Docker Desktop and try again.${NC}"
    exit 1
fi

# Check for .env file
if [ ! -f .env ]; then
    echo -e "${YELLOW}No .env file found. Creating .env.example...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}Please edit .env file and add your OpenRouter API key.${NC}"
    exit 1
fi

# Parse command line arguments
BUILD=false
OPEN_BROWSER=true

while [[ $# -gt 0 ]]; do
    case $1 in
        --build)
            BUILD=true
            shift
            ;;
        --no-browser)
            OPEN_BROWSER=false
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--build] [--no-browser]"
            exit 1
            ;;
    esac
done

# Check if image exists
IMAGE_EXISTS=$(docker images -q finally:latest)

if [ "$BUILD" = true ] || [ -z "$IMAGE_EXISTS" ]; then
    echo -e "${YELLOW}Building Docker image...${NC}"
    docker build -t finally:latest .
fi

# Check if container is already running
CONTAINER_ID=$(docker ps -q -f name=finally-app)

if [ -n "$CONTAINER_ID" ]; then
    echo -e "${YELLOW}Container is already running. Stopping it first...${NC}"
    docker stop finally-app > /dev/null 2>&1
    docker rm finally-app > /dev/null 2>&1
fi

# Run the container
echo -e "${GREEN}Starting container...${NC}"
docker run -d \
    --name finally-app \
    -p 8000:8000 \
    -v finally-data:/app/db \
    --env-file .env \
    finally:latest

# Wait for container to start
echo -e "${YELLOW}Waiting for application to start...${NC}"
for i in {1..30}; do
    if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
        echo -e "${GREEN}Application is running!${NC}"
        
        # Print connection info
        echo ""
        echo "=========================================="
        echo "FinAlly AI Trading Workstation"
        echo "=========================================="
        echo "Local:    http://localhost:8000"
        echo "API Docs: http://localhost:8000/docs"
        echo ""
        echo "Default portfolio: $10,000 virtual cash"
        echo "Default watchlist: 10 popular stocks"
        echo "=========================================="
        
        # Open browser if requested
        if [ "$OPEN_BROWSER" = true ]; then
            if command -v open > /dev/null 2>&1; then
                open http://localhost:8000
            elif command -v xdg-open > /dev/null 2>&1; then
                xdg-open http://localhost:8000
            else
                echo "Could not automatically open browser. Please navigate to http://localhost:8000"
            fi
        fi
        
        exit 0
    fi
    sleep 1
    echo -n "."
done

echo ""
echo -e "${RED}Failed to start application. Check logs with: docker logs finally-app${NC}"
exit 1