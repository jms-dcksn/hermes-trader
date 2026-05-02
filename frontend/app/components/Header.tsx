import React from 'react'
import { FiBell, FiSettings, FiUser } from 'react-icons/fi'

interface HeaderProps {
  portfolio: any
  connectionStatus: 'connected' | 'reconnecting' | 'disconnected'
}

export default function Header({ portfolio, connectionStatus }: HeaderProps) {
  const totalValue = portfolio?.total_value || 0
  const cashBalance = portfolio?.cash_balance || 0
  
  return (
    <header className="bg-terminal-card border border-terminal-border rounded-lg p-4">
      <div className="flex items-center justify-between">
        {/* Logo and title */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-blue-primary to-purple-secondary rounded-lg flex items-center justify-center">
            <span className="font-bold text-lg">F</span>
          </div>
          <div>
            <h1 className="text-xl font-bold">FinAlly</h1>
            <p className="text-xs text-gray-400">AI Trading Workstation</p>
          </div>
        </div>
        
        {/* Portfolio summary */}
        <div className="flex items-center gap-6">
          <div className="text-right">
            <p className="text-sm text-gray-400">Total Portfolio Value</p>
            <p className="text-2xl font-bold">${totalValue.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</p>
          </div>
          
          <div className="text-right">
            <p className="text-sm text-gray-400">Cash Balance</p>
            <p className="text-xl font-semibold">${cashBalance.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</p>
          </div>
          
          <div className="text-right">
            <p className="text-sm text-gray-400">Connection</p>
            <div className="flex items-center gap-2">
              <div className={`connection-indicator connection-${connectionStatus}`} />
              <span className="text-sm capitalize">{connectionStatus}</span>
            </div>
          </div>
        </div>
        
        {/* User controls */}
        <div className="flex items-center gap-3">
          <button className="p-2 hover:bg-terminal-border rounded-lg transition-colors">
            <FiBell className="w-5 h-5" />
          </button>
          <button className="p-2 hover:bg-terminal-border rounded-lg transition-colors">
            <FiSettings className="w-5 h-5" />
          </button>
          <button className="p-2 hover:bg-terminal-border rounded-lg transition-colors">
            <FiUser className="w-5 h-5" />
          </button>
        </div>
      </div>
    </header>
  )
}