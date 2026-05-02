'use client'

import { useState, useEffect, useRef } from 'react'
import Header from './components/Header'
import WatchlistPanel from './components/WatchlistPanel'
import ChartPanel from './components/ChartPanel'
import PortfolioPanel from './components/PortfolioPanel'
import TradePanel from './components/TradePanel'
import ChatPanel from './components/ChatPanel'
import { useSSEConnection } from './hooks/useSSEConnection'
import { usePortfolio } from './hooks/usePortfolio'

export default function Home() {
  const [selectedTicker, setSelectedTicker] = useState<string>('AAPL')
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'reconnecting' | 'disconnected'>('disconnected')
  
  const { prices, subscribeToPrices } = useSSEConnection()
  const { portfolio, refreshPortfolio } = usePortfolio()
  
  // Initialize SSE connection
  useEffect(() => {
    subscribeToPrices()
  }, [subscribeToPrices])
  
  // Auto-refresh portfolio every 10 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      refreshPortfolio()
    }, 10000)
    
    return () => clearInterval(interval)
  }, [refreshPortfolio])
  
  // Update connection status based on SSE
  useEffect(() => {
    if (prices.length > 0) {
      setConnectionStatus('connected')
    } else {
      setConnectionStatus('reconnecting')
    }
  }, [prices])
  
  return (
    <div className="min-h-screen bg-terminal-bg text-gray-100 p-4">
      <Header 
        portfolio={portfolio} 
        connectionStatus={connectionStatus} 
      />
      
      <div className="grid grid-cols-12 gap-4 mt-4">
        {/* Left column: Watchlist and Chart */}
        <div className="col-span-8 space-y-4">
          <WatchlistPanel 
            prices={prices}
            selectedTicker={selectedTicker}
            onSelectTicker={setSelectedTicker}
          />
          
          <ChartPanel 
            ticker={selectedTicker}
            prices={prices.filter(p => p.ticker === selectedTicker)}
          />
          
          <div className="grid grid-cols-2 gap-4">
            <PortfolioPanel portfolio={portfolio} />
            <TradePanel selectedTicker={selectedTicker} />
          </div>
        </div>
        
        {/* Right column: Chat */}
        <div className="col-span-4">
          <ChatPanel />
        </div>
      </div>
      
      {/* Connection status toast */}
      {connectionStatus !== 'connected' && (
        <div className="fixed bottom-4 right-4 bg-terminal-card border border-terminal-border p-3 rounded-lg shadow-lg">
          <div className="flex items-center gap-2">
            <div className={`connection-indicator connection-${connectionStatus}`} />
            <span className="text-sm">
              {connectionStatus === 'reconnecting' ? 'Reconnecting to market data...' : 'Disconnected from market data'}
            </span>
          </div>
        </div>
      )}
    </div>
  )
}