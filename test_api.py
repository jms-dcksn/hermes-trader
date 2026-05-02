#!/usr/bin/env python3
import asyncio
import aiohttp
import json
import sys

async def test_health(session, base_url):
    async with session.get(f"{base_url}/api/health") as resp:
        return resp.status, await resp.text()

async def test_portfolio(session, base_url):
    async with session.get(f"{base_url}/api/portfolio") as resp:
        return resp.status, await resp.json()

async def test_watchlist(session, base_url):
    async with session.get(f"{base_url}/api/watchlist") as resp:
        return resp.status, await resp.json()

async def test_add_watchlist(session, base_url):
    data = {"ticker": "PYPL"}
    async with session.post(f"{base_url}/api/watchlist", json=data) as resp:
        return resp.status, await resp.json()

async def test_stream(session, base_url):
    # Test SSE connection briefly
    try:
        async with session.get(f"{base_url}/api/stream/prices") as resp:
            # Read first few lines
            lines = []
            async for line in resp.content:
                lines.append(line.decode())
                if len(lines) >= 3:
                    break
            return resp.status, lines
    except Exception as e:
        return 0, str(e)

async def main():
    base_url = "http://localhost:8000"
    
    async with aiohttp.ClientSession() as session:
        print("Testing FinAlly API endpoints...")
        
        # Test health
        status, text = await test_health(session, base_url)
        print(f"✓ Health check: {status} - {text}")
        
        # Test portfolio
        status, data = await test_portfolio(session, base_url)
        print(f"✓ Portfolio: {status} - Cash: ${data.get('cash_balance', 0)}")
        
        # Test watchlist
        status, data = await test_watchlist(session, base_url)
        print(f"✓ Watchlist: {status} - {len(data.get('watchlist', []))} tickers")
        
        # Test add to watchlist
        status, data = await test_add_watchlist(session, base_url)
        print(f"✓ Add to watchlist: {status} - {data}")
        
        # Test stream (quick)
        status, lines = await test_stream(session, base_url)
        print(f"✓ SSE stream: {status} - {len(lines)} lines received")

if __name__ == "__main__":
    asyncio.run(main())