import urllib.request
import json
import sys

base = 'http://localhost:8000'

print('Testing FinAlly API...')

# Health
try:
    with urllib.request.urlopen(f'{base}/api/health') as f:
        print(f'✓ Health: {f.status}')
except Exception as e:
    print(f'✗ Health failed: {e}')
    sys.exit(1)

# Portfolio
try:
    with urllib.request.urlopen(f'{base}/api/portfolio') as f:
        portfolio = json.loads(f.read().decode())
        print(f'✓ Portfolio: Cash: {portfolio["cash_balance"]}, Positions: {len(portfolio["positions"])}')
except Exception as e:
    print(f'✗ Portfolio failed: {e}')

# Watchlist
try:
    with urllib.request.urlopen(f'{base}/api/watchlist') as f:
        watchlist = json.loads(f.read().decode())
        print(f'✓ Watchlist: {len(watchlist["watchlist"])} tickers')
        for item in watchlist['watchlist'][:3]:
            print(f'  - {item["ticker"]}: ${item.get("price", "N/A")}')
except Exception as e:
    print(f'✗ Watchlist failed: {e}')

print('\nAll tests completed.')