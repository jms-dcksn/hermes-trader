'use client'

import React, { useState, useEffect } from 'react'
import { FiStar, FiTrendingUp, FiTrendingDown } from 'react-icons/fi'

interface PriceData {
  ticker: string
  price: number
  change: number
  change_percent: number
  direction: 'up' | 'down' | 'same'
  timestamp: string
}

interface WatchlistPanelProps {
  prices: PriceData[]
  selectedTicker: string
  onSelectTicker: (ticker: string) => void
}

export default function WatchlistPanel({ prices, selectedTicker, onSelectTicker }: WatchlistPanelProps) {
  const [watchlist, setWatchlist] = useState<string[]>([
    'AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'NVDA', 'META', 'JPM', 'V', 'NFLX'
  ])
  
  const [priceHistory, setPriceHistory] = useState<Record<string, number[]>>({})
  
  // Initialize price history
  useEffect(() => {
    const initialHistory: Record<string, number[]> = {}
    watchlist.forEach(ticker => {
      initialHistory[ticker] = [100] // Starting placeholder
    })
    setPriceHistory(initialHistory)
  }, [watchlist])
  
  // Update price history when prices change
  useEffect(() => {
    const newHistory = { ...priceHistory }
    
    prices.forEach(price => {
      if (!newHistory[price.ticker]) {
        newHistory[price.ticker] = []
      }
      
      // Keep last 20 price points for sparkline
      newHistory[price.ticker] = [...newHistory[price.ticker], price.price].slice(-20)
    })
    
    setPriceHistory(newHistory)
  }, [prices])
  
  const getPriceData = (ticker: string): PriceData | undefined => {
    return prices.find(p => p.ticker === ticker)
  }
  
  const renderSparkline = (ticker: string) => {
    const history = priceHistory[ticker] || []
    if (history.length < 2) return null
    
    const max = Math.max(...history)
    const min = Math.min(...history)
    const range = max - min || 1
    
    // Simple SVG sparkline
    const points = history.map((price, i) => {
      const x = (i / (history.length - 1)) * 40
      const y = 20 - ((price - min) / range) * 18
      return `${x},${y}`
    }).join(' ')
    
    const latestDirection = getPriceData(ticker)?.direction || 'same'
    const strokeColor = latestDirection === 'up' ? '#00c853' : latestDirection === 'down' ? '#ff5252' : '#666'
    
    return (
      <svg width="50" height="24" className="opacity-80">
        <polyline
          points={points}
          fill="none"
          stroke={strokeColor}
          strokeWidth="1.5"
        />
      </svg>
    )
  }
  
  return (
    <div className="bg-terminal-card border border-terminal-border rounded-lg p-4">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold">Watchlist</h2>
        <button className="text-sm text-blue-primary hover:text-blue-300 transition-colors">
          + Add Ticker
        </button>
      </div>
      
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="text-left text-sm text-gray-400 border-b border-terminal-border">
              <th className="pb-2 pl-2">Ticker</th>
              <th className="pb-2">Price</th>
              <th className="pb-2">Change</th>
              <th className="pb-2">Chart</th>
              <th className="pb-2 pr-2 text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            {watchlist.map(ticker => {
              const priceData = getPriceData(ticker)
              const isSelected = selectedTicker === ticker
              
              return (
                <tr 
                  key={ticker}
                  className={`border-b border-terminal-border/50 hover:bg-terminal-border/30 cursor-pointer transition-colors ${
                    isSelected ? 'bg-terminal-border/30' : ''
                  }`}
                  onClick={() => onSelectTicker(ticker)}
                >
                  <td className="py-3 pl-2">
                    <div className="flex items-center gap-2">
                      <FiStar className={`w-4 h-4 ${isSelected ? 'text-accent-yellow' : 'text-gray-500'}`} />
                      <span className="font-semibold">{ticker}</span>
                    </div>
                  </td>
                  
                  <td className="py-3">
                    <div className={`flex items-center gap-2 ${
                      priceData?.direction === 'up' ? 'text-green-up' : 
                      priceData?.direction === 'down' ? 'text-red-down' : 
                      'text-gray-300'
                    }`}>
                      {priceData?.direction === 'up' && <FiTrendingUp className="w-4 h-4" />}
                      {priceData?.direction === 'down' && <FiTrendingDown className="w-4 h-4" />}
                      <span className={`font-mono ${priceData ? 'price-flash-' + priceData.direction : ''}`}>
                        ${priceData?.price.toFixed(2) || '--.--'}
                      </span>
                    </div>
                  </td>
                  
                  <td className="py-3">
                    <div className={`font-mono ${
                      (priceData?.change_percent || 0) >= 0 ? 'text-green-up' : 'text-red-down'
                    }`}>
                      {priceData ? (
                        <>
                          {priceData.change >= 0 ? '+' : ''}{priceData.change.toFixed(2)} 
                          <span className="ml-1">
                            ({priceData.change_percent >= 0 ? '+' : ''}{priceData.change_percent.toFixed(2)}%)
                          </span>
                        </>
                      ) : (
                        '-- (--%)'
                      )}
                    </div>
                  </td>
                  
                  <td className="py-3">
                    {renderSparkline(ticker)}
                  </td>
                  
                  <td className="py-3 pr-2 text-right">
                    <button className="text-sm text-gray-400 hover:text-white transition-colors">
                      Trade
                    </button>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}