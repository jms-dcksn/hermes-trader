#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Stopping FinAlly AI Trading Workstation...${NC}"

# Check if container is running
CONTAINER_ID=$(docker ps -q -f name=finally-app)

if [ -n "$CONTAINER_ID" ]; then
    echo -e "${YELLOW}Stopping container...${NC}"
    docker stop finally-app
    
    echo -e "${YELLOW}Removing container...${NC}"
    docker rm finally-app
    
    echo -e "${GREEN}Container stopped and removed.${NC}"
    echo "Note: Database volume (finally-data) is preserved."
else
    echo -e "${YELLOW}Container is not running.${NC}"
fi

# Check for other running containers with the same image
OTHER_CONTAINERS=$(docker ps -q -f ancestor=finally:latest)
if [ -n "$OTHER_CONTAINERS" ]; then
    echo -e "${YELLOW}Other containers using the finally image are still running.${NC}"
    echo "Container IDs: $OTHER_CONTAINERS"
    echo "Stop them with: docker stop <container_id>"
fi

echo -e "${GREEN}Done.${NC}"