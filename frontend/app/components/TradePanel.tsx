'use client'

import React, { useState } from 'react'
import { FiArrowUp, FiArrowDown, FiDollarSign } from 'react-icons/fi'

interface TradePanelProps {
  selectedTicker: string
}

export default function TradePanel({ selectedTicker }: TradePanelProps) {
  const [ticker, setTicker] = useState(selectedTicker)
  const [quantity, setQuantity] = useState('')
  const [side, setSide] = useState<'buy' | 'sell'>('buy')
  const [isSubmitting, setIsSubmitting] = useState(false)
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!ticker || !quantity || parseFloat(quantity) <= 0) {
      alert('Please enter a valid ticker and quantity')
      return
    }
    
    setIsSubmitting(true)
    
    try {
      const response = await fetch('/api/portfolio/trade', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ticker: ticker.toUpperCase(),
          side,
          quantity: parseFloat(quantity)
        })
      })
      
      const data = await response.json()
      
      if (response.ok) {
        alert(`Trade executed successfully! ${data.message}`)
        setQuantity('')
      } else {
        alert(`Trade failed: ${data.detail || 'Unknown error'}`)
      }
    } catch (error) {
      alert('Error executing trade. Please try again.')
      console.error(error)
    } finally {
      setIsSubmitting(false)
    }
  }
  
  return (
    <div className="bg-terminal-card border border-terminal-border rounded-lg p-4">
      <h2 className="text-lg font-semibold mb-4">Trade</h2>
      
      <form onSubmit={handleSubmit}>
        <div className="space-y-4">
          {/* Ticker input */}
          <div>
            <label className="block text-sm text-gray-400 mb-1">Ticker</label>
            <div className="relative">
              <FiDollarSign className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500" />
              <input
                type="text"
                value={ticker}
                onChange={(e) => setTicker(e.target.value.toUpperCase())}
                className="w-full bg-terminal-bg border border-terminal-border rounded-lg pl-10 pr-4 py-2 focus:outline-none focus:border-blue-primary"
                placeholder="AAPL"
              />
            </div>
          </div>
          
          {/* Quantity input */}
          <div>
            <label className="block text-sm text-gray-400 mb-1">Quantity</label>
            <input
              type="number"
              value={quantity}
              onChange={(e) => setQuantity(e.target.value)}
              min="0.01"
              step="0.01"
              className="w-full bg-terminal-bg border border-terminal-border rounded-lg px-4 py-2 focus:outline-none focus:border-blue-primary font-mono"
              placeholder="0.00"
            />
          </div>
          
          {/* Side selection */}
          <div>
            <label className="block text-sm text-gray-400 mb-2">Side</label>
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                className={`flex items-center justify-center gap-2 py-3 rounded-lg transition-colors ${
                  side === 'buy'
                    ? 'bg-green-up/20 border border-green-up text-green-up'
                    : 'bg-terminal-bg border border-terminal-border text-gray-400 hover:text-white'
                }`}
                onClick={() => setSide('buy')}
              >
                <FiArrowUp className="w-5 h-5" />
                Buy
              </button>
              <button
                type="button"
                className={`flex items-center justify-center gap-2 py-3 rounded-lg transition-colors ${
                  side === 'sell'
                    ? 'bg-red-down/20 border border-red-down text-red-down'
                    : 'bg-terminal-bg border border-terminal-border text-gray-400 hover:text-white'
                }`}
                onClick={() => setSide('sell')}
              >
                <FiArrowDown className="w-5 h-5" />
                Sell
              </button>
            </div>
          </div>
          
          {/* Order summary */}
          {quantity && parseFloat(quantity) > 0 && (
            <div className="bg-terminal-bg/50 rounded-lg p-3">
              <p className="text-sm text-gray-400">Order Summary</p>
              <div className="mt-2 space-y-1">
                <div className="flex justify-between">
                  <span className="text-gray-400">Action</span>
                  <span className={`font-semibold ${
                    side === 'buy' ? 'text-green-up' : 'text-red-down'
                  }`}>
                    {side === 'buy' ? 'BUY' : 'SELL'} {ticker}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Quantity</span>
                  <span className="font-mono">{parseFloat(quantity).toFixed(2)} shares</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Estimated Cost</span>
                  <span className="font-mono">${(parseFloat(quantity) * 150).toFixed(2)}</span>
                </div>
              </div>
            </div>
          )}
          
          {/* Submit button */}
          <button
            type="submit"
            disabled={isSubmitting}
            className={`w-full py-3 rounded-lg font-semibold transition-colors flex items-center justify-center gap-2 ${
              side === 'buy'
                ? 'bg-green-up hover:bg-green-up/80'
                : 'bg-red-down hover:bg-red-down/80'
            } ${isSubmitting ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            {isSubmitting ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Executing...
              </>
            ) : (
              <>
                {side === 'buy' ? <FiArrowUp className="w-5 h-5" /> : <FiArrowDown className="w-5 h-5" />}
                {side === 'buy' ? 'Buy' : 'Sell'} {ticker}
              </>
            )}
          </button>
          
          <p className="text-xs text-gray-500 text-center">
            Market orders only • Instant fill at current price • No fees
          </p>
        </div>
      </form>
    </div>
  )
}