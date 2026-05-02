import { useState, useEffect, useCallback } from 'react'

interface PriceData {
  ticker: string
  price: number
  previous_price: number
  change: number
  change_percent: number
  direction: 'up' | 'down' | 'same'
  timestamp: string
}

export function useSSEConnection() {
  const [prices, setPrices] = useState<PriceData[]>([])
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'reconnecting' | 'disconnected'>('disconnected')
  
  const subscribeToPrices = useCallback(() => {
    const eventSource = new EventSource('/api/stream/prices')
    
    setConnectionStatus('reconnecting')
    
    eventSource.onopen = () => {
      setConnectionStatus('connected')
      console.log('SSE connection opened')
    }
    
    eventSource.onmessage = (event) => {
      try {
        const priceData = JSON.parse(event.data)
        
        setPrices(prev => {
          const existingIndex = prev.findIndex(p => p.ticker === priceData.ticker)
          
          if (existingIndex >= 0) {
            const newPrices = [...prev]
            newPrices[existingIndex] = priceData
            return newPrices
          } else {
            return [...prev, priceData]
          }
        })
      } catch (error) {
        console.error('Error parsing SSE data:', error)
      }
    }
    
    eventSource.onerror = (error) => {
      console.error('SSE error:', error)
      setConnectionStatus('reconnecting')
      
      // Try to reconnect after delay
      setTimeout(() => {
        eventSource.close()
        subscribeToPrices()
      }, 3000)
    }
    
    // Cleanup on unmount
    return () => {
      eventSource.close()
      setConnectionStatus('disconnected')
    }
  }, [])
  
  // Subscribe on mount
  useEffect(() => {
    const cleanup = subscribeToPrices()
    return cleanup
  }, [subscribeToPrices])
  
  return { prices, connectionStatus, subscribeToPrices }
}