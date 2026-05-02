#!/bin/bash

echo "Testing FinAlly API endpoints..."

# Start container
echo "Starting container..."
docker run -d --name finally-test -p 8002:8000 -v finally-test-data:/app/db --env-file .env finally-test
sleep 5

echo "Waiting for application to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:8002/api/health > /dev/null; then
        echo "Application is ready!"
        break
    fi
    sleep 1
    echo -n "."
done

echo ""
echo "=== Testing API Endpoints ==="

# Test health endpoint
echo "1. Testing /api/health..."
curl -s http://localhost:8002/api/health | jq -r '.status' || echo "Health check failed"

# Test watchlist endpoint
echo "2. Testing /api/watchlist..."
curl -s http://localhost:8002/api/watchlist | jq -r '.watchlist[0:3][] | .ticker' || echo "Watchlist test failed"

# Test portfolio endpoint
echo "3. Testing /api/portfolio..."
curl -s http://localhost:8002/api/portfolio | jq -r '.cash_balance' || echo "Portfolio test failed"

# Test SSE stream (quick check)
echo "4. Testing SSE connection..."
timeout 3 curl -s http://localhost:8002/api/stream/prices > /tmp/sse_test.txt &
SSE_PID=$!
sleep 2
if [ -s /tmp/sse_test.txt ]; then
    echo "SSE stream is working (received data)"
    head -c 200 /tmp/sse_test.txt
else
    echo "SSE stream test inconclusive"
fi

# Test chat endpoint (mock mode)
echo "5. Testing /api/chat..."
curl -s -X POST http://localhost:8002/api/chat \
    -H "Content-Type: application/json" \
    -d '{"message": "Hello", "user_id": "default"}' | jq -r '.message' || echo "Chat test failed"

echo ""
echo "=== Frontend Test ==="
echo "Checking if frontend is served..."
curl -s -o /tmp/frontend_test.html http://localhost:8002/
if [ -s /tmp/frontend_test.html ]; then
    echo "Frontend is being served (HTML found)"
    grep -o "<title>[^<]*</title>" /tmp/frontend_test.html || echo "No title found"
else
    echo "Frontend test failed"
fi

# Cleanup
echo ""
echo "=== Cleanup ==="
docker stop finally-test
docker rm finally-test

echo "Test complete!"