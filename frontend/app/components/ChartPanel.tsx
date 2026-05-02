'use client'

import React, { useState, useEffect } from 'react'
import { FiBarChart2, FiActivity } from 'react-icons/fi'

interface PriceData {
  ticker: string
  price: number
  change: number
  change_percent: number
  direction: 'up' | 'down' | 'same'
  timestamp: string
}

interface ChartPanelProps {
  ticker: string
  prices: PriceData[]
}

export default function ChartPanel({ ticker, prices }: ChartPanelProps) {
  const [chartType, setChartType] = useState<'line' | 'candle'>('line')
  const [timeframe, setTimeframe] = useState<'1D' | '1W' | '1M' | '3M'>('1D')
  
  // Generate mock chart data based on price history
  const chartData = prices.map((price, index) => ({
    time: index,
    price: price.price,
    volume: Math.random() * 1000000
  }))
  
  const currentPrice = prices.length > 0 ? prices[prices.length - 1].price : 0
  const priceChange = prices.length > 0 ? prices[prices.length - 1].change : 0
  const priceChangePercent = prices.length > 0 ? prices[prices.length - 1].change_percent : 0
  
  return (
    <div className="bg-terminal-card border border-terminal-border rounded-lg p-4">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <h2 className="text-lg font-semibold">{ticker}</h2>
          <div className={`text-xl font-bold ${
            priceChange >= 0 ? 'text-green-up' : 'text-red-down'
          }`}>
            ${currentPrice.toFixed(2)}
            <span className="ml-2 text-sm">
              {priceChange >= 0 ? '+' : ''}{priceChange.toFixed(2)} 
              ({priceChangePercent >= 0 ? '+' : ''}{priceChangePercent.toFixed(2)}%)
            </span>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          <div className="flex bg-terminal-border rounded-lg p-1">
            {['1D', '1W', '1M', '3M'].map((tf) => (
              <button
                key={tf}
                className={`px-3 py-1 rounded text-sm transition-colors ${
                  timeframe === tf 
                    ? 'bg-terminal-bg text-white' 
                    : 'text-gray-400 hover:text-white'
                }`}
                onClick={() => setTimeframe(tf as any)}
              >
                {tf}
              </button>
            ))}
          </div>
          
          <div className="flex bg-terminal-border rounded-lg p-1">
            <button
              className={`px-3 py-1 rounded text-sm transition-colors flex items-center gap-2 ${
                chartType === 'line' 
                  ? 'bg-terminal-bg text-white' 
                  : 'text-gray-400 hover:text-white'
              }`}
              onClick={() => setChartType('line')}
            >
              <FiActivity className="w-4 h-4" />
              Line
            </button>
            <button
              className={`px-3 py-1 rounded text-sm transition-colors flex items-center gap-2 ${
                chartType === 'candle' 
                  ? 'bg-terminal-bg text-white' 
                  : 'text-gray-400 hover:text-white'
              }`}
              onClick={() => setChartType('candle')}
            >
              <FiBarChart2 className="w-4 h-4" />
              Candle
            </button>
          </div>
        </div>
      </div>
      
      {/* Chart placeholder */}
      <div className="h-64 bg-terminal-bg/50 rounded-lg border border-terminal-border p-4">
        {chartData.length > 0 ? (
          <div className="h-full flex flex-col">
            {/* Chart visualization */}
            <div className="flex-1 relative">
              {/* Simple line chart using divs */}
              <div className="absolute inset-0">
                {chartData.map((point, i) => {
                  const x = (i / (chartData.length - 1)) * 100
                  const maxPrice = Math.max(...chartData.map(d => d.price))
                  const minPrice = Math.min(...chartData.map(d => d.price))
                  const range = maxPrice - minPrice || 1
                  const y = 100 - ((point.price - minPrice) / range) * 90
                  
                  return (
                    <div
                      key={i}
                      className="absolute w-1 h-1 bg-blue-primary rounded-full"
                      style={{ left: `${x}%`, top: `${y}%` }}
                    />
                  )
                })}
                
                {/* Line connecting points */}
                <div className="absolute inset-0">
                  <svg width="100%" height="100%" className="overflow-visible">
                    <polyline
                      points={chartData.map((point, i) => {
                        const x = (i / (chartData.length - 1)) * 100
                        const maxPrice = Math.max(...chartData.map(d => d.price))
                        const minPrice = Math.min(...chartData.map(d => d.price))
                        const range = maxPrice - minPrice || 1
                        const y = 100 - ((point.price - minPrice) / range) * 90
                        return `${x},${y}`
                      }).join(' ')}
                      fill="none"
                      stroke="#209dd7"
                      strokeWidth="2"
                    />
                  </svg>
                </div>
              </div>
            </div>
            
            {/* X-axis labels */}
            <div className="flex justify-between text-xs text-gray-500 mt-2">
              <span>Open</span>
              <span>High: ${Math.max(...chartData.map(d => d.price)).toFixed(2)}</span>
              <span>Low: ${Math.min(...chartData.map(d => d.price)).toFixed(2)}</span>
              <span>Close</span>
            </div>
          </div>
        ) : (
          <div className="h-full flex items-center justify-center text-gray-500">
            <div className="text-center">
              <FiActivity className="w-12 h-12 mx-auto mb-2 opacity-50" />
              <p>Loading chart data for {ticker}...</p>
              <p className="text-sm">Waiting for price updates</p>
            </div>
          </div>
        )}
      </div>
      
      {/* Volume indicator */}
      {chartData.length > 0 && (
        <div className="mt-4">
          <div className="flex items-center justify-between text-sm text-gray-400">
            <span>Volume</span>
            <span className="font-mono">
              {chartData.reduce((sum, d) => sum + d.volume, 0).toLocaleString(undefined, { 
                notation: 'compact',
                compactDisplay: 'short'
              })}
            </span>
          </div>
          <div className="h-2 bg-terminal-border rounded-full overflow-hidden mt-1">
            <div 
              className="h-full bg-purple-secondary rounded-full"
              style={{ width: '70%' }}
            />
          </div>
        </div>
      )}
    </div>
  )
}