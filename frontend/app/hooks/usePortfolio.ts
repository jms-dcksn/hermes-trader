import { useState, useCallback } from 'react'

interface Position {
  ticker: string
  quantity: number
  avg_cost: number
  current_price: number
  position_value: number
  unrealized_pnl: number
  unrealized_pnl_percent: number
}

interface PortfolioData {
  cash_balance: number
  positions: Position[]
  total_value: number
  unrealized_pnl: number
}

export function usePortfolio() {
  const [portfolio, setPortfolio] = useState<PortfolioData>({
    cash_balance: 10000.0,
    positions: [],
    total_value: 10000.0,
    unrealized_pnl: 0
  })
  const [isLoading, setIsLoading] = useState(false)
  
  const fetchPortfolio = useCallback(async () => {
    setIsLoading(true)
    try {
      const response = await fetch('/api/portfolio')
      if (!response.ok) throw new Error('Failed to fetch portfolio')
      const data = await response.json()
      setPortfolio(data)
    } catch (error) {
      console.error('Error fetching portfolio:', error)
      // Keep existing portfolio data on error
    } finally {
      setIsLoading(false)
    }
  }, [])
  
  const refreshPortfolio = useCallback(() => {
    fetchPortfolio()
  }, [fetchPortfolio])
  
  const executeTrade = useCallback(async (ticker: string, side: 'buy' | 'sell', quantity: number) => {
    setIsLoading(true)
    try {
      const response = await fetch('/api/portfolio/trade', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ticker, side, quantity })
      })
      
      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Trade failed')
      }
      
      const data = await response.json()
      
      // Refresh portfolio after successful trade
      await fetchPortfolio()
      
      return { success: true, data }
    } catch (error: any) {
      return { success: false, error: error.message }
    } finally {
      setIsLoading(false)
    }
  }, [fetchPortfolio])
  
  // Fetch portfolio on mount
  useState(() => {
    fetchPortfolio()
  })
  
  return {
    portfolio,
    isLoading,
    refreshPortfolio,
    executeTrade
  }
}