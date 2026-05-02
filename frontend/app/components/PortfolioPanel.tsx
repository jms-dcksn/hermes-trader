'use client'

import React, { useState, useEffect } from 'react'
import { FiPieChart, FiTrendingUp, FiTrendingDown } from 'react-icons/fi'

interface Position {
  ticker: string
  quantity: number
  avg_cost: number
  current_price: number
  position_value: number
  unrealized_pnl: number
  unrealized_pnl_percent: number
}

interface PortfolioPanelProps {
  portfolio: any
}

export default function PortfolioPanel({ portfolio }: PortfolioPanelProps) {
  const [selectedView, setSelectedView] = useState<'positions' | 'heatmap'>('positions')
  
  const positions: Position[] = portfolio?.positions || []
  const totalValue = portfolio?.total_value || 0
  const cashBalance = portfolio?.cash_balance || 0
  
  // Calculate portfolio allocation
  const allocation = positions.map(pos => ({
    ticker: pos.ticker,
    value: pos.position_value,
    percent: (pos.position_value / totalValue) * 100,
    pnlPercent: pos.unrealized_pnl_percent
  }))
  
  // Add cash to allocation
  if (cashBalance > 0) {
    allocation.unshift({
      ticker: 'CASH',
      value: cashBalance,
      percent: (cashBalance / totalValue) * 100,
      pnlPercent: 0
    })
  }
  
  const totalPnl = positions.reduce((sum, pos) => sum + pos.unrealized_pnl, 0)
  const totalPnlPercent = totalValue > 0 ? (totalPnl / (totalValue - totalPnl)) * 100 : 0
  
  return (
    <div className="bg-terminal-card border border-terminal-border rounded-lg p-4">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold">Portfolio</h2>
        <div className="flex bg-terminal-border rounded-lg p-1">
          <button
            className={`px-3 py-1 rounded text-sm transition-colors flex items-center gap-2 ${
              selectedView === 'positions' 
                ? 'bg-terminal-bg text-white' 
                : 'text-gray-400 hover:text-white'
            }`}
            onClick={() => setSelectedView('positions')}
          >
            Positions
          </button>
          <button
            className={`px-3 py-1 rounded text-sm transition-colors flex items-center gap-2 ${
              selectedView === 'heatmap' 
                ? 'bg-terminal-bg text-white' 
                : 'text-gray-400 hover:text-white'
            }`}
            onClick={() => setSelectedView('heatmap')}
          >
            <FiPieChart className="w-4 h-4" />
            Heatmap
          </button>
        </div>
      </div>
      
      {/* Portfolio summary */}
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="bg-terminal-bg/50 rounded-lg p-3">
          <p className="text-sm text-gray-400">Total Value</p>
          <p className="text-xl font-bold">${totalValue.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</p>
        </div>
        <div className="bg-terminal-bg/50 rounded-lg p-3">
          <p className="text-sm text-gray-400">Total P&L</p>
          <div className={`flex items-center gap-2 ${
            totalPnl >= 0 ? 'text-green-up' : 'text-red-down'
          }`}>
            {totalPnl >= 0 ? <FiTrendingUp className="w-4 h-4" /> : <FiTrendingDown className="w-4 h-4" />}
            <p className="text-xl font-bold">
              ${Math.abs(totalPnl).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              <span className="text-sm ml-2">
                ({totalPnlPercent >= 0 ? '+' : ''}{totalPnlPercent.toFixed(2)}%)
              </span>
            </p>
          </div>
        </div>
      </div>
      
      {selectedView === 'positions' ? (
        <div className="overflow-y-auto max-h-64">
          {positions.length > 0 ? (
            <table className="w-full">
              <thead>
                <tr className="text-left text-sm text-gray-400 border-b border-terminal-border">
                  <th className="pb-2">Ticker</th>
                  <th className="pb-2">Qty</th>
                  <th className="pb-2">Avg Cost</th>
                  <th className="pb-2">Value</th>
                  <th className="pb-2 text-right">P&L</th>
                </tr>
              </thead>
              <tbody>
                {positions.map((pos) => (
                  <tr key={pos.ticker} className="border-b border-terminal-border/50 hover:bg-terminal-border/30">
                    <td className="py-2 font-semibold">{pos.ticker}</td>
                    <td className="py-2 font-mono">{pos.quantity.toFixed(2)}</td>
                    <td className="py-2 font-mono">${pos.avg_cost.toFixed(2)}</td>
                    <td className="py-2 font-mono">${pos.position_value.toFixed(2)}</td>
                    <td className="py-2 text-right">
                      <div className={`font-mono ${
                        pos.unrealized_pnl >= 0 ? 'text-green-up' : 'text-red-down'
                      }`}>
                        {pos.unrealized_pnl >= 0 ? '+' : ''}${Math.abs(pos.unrealized_pnl).toFixed(2)}
                        <br />
                        <span className="text-xs">
                          ({pos.unrealized_pnl_percent >= 0 ? '+' : ''}{pos.unrealized_pnl_percent.toFixed(2)}%)
                        </span>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="text-center py-6 text-gray-500">
              <FiPieChart className="w-12 h-12 mx-auto mb-2 opacity-50" />
              <p>No positions yet</p>
              <p className="text-sm">Start trading to build your portfolio</p>
            </div>
          )}
        </div>
      ) : (
        <div className="space-y-2">
          {allocation.map((item) => (
            <div key={item.ticker} className="space-y-1">
              <div className="flex justify-between text-sm">
                <div className="flex items-center gap-2">
                  <span className="font-semibold">{item.ticker}</span>
                  <span className="text-gray-400">
                    ${item.value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                  </span>
                </div>
                <span className="font-mono">{item.percent.toFixed(1)}%</span>
              </div>
              <div className="h-2 bg-terminal-border rounded-full overflow-hidden">
                <div 
                  className={`h-full rounded-full ${
                    item.ticker === 'CASH' ? 'bg-gray-600' :
                    item.pnlPercent >= 0 ? 'bg-green-up' : 'bg-red-down'
                  }`}
                  style={{ width: `${Math.min(item.percent, 100)}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}