'use client'

import React, { useState, useRef, useEffect } from 'react'
import { FiSend, FiMessageSquare, FiUser } from 'react-icons/fi'
import { MdAutoAwesome } from 'react-icons/md'

interface ChatMessage {
id: string
role: 'user' | 'assistant'
content: string
timestamp: string
actions?: {
trades?: any[]
watchlist_changes?: any[]
}
}

export default function ChatPanel() {
const [messages, setMessages] = useState<ChatMessage[]>([
{
id: '1',
role: 'assistant',
content: 'Hello! I\'m FinAlly, your AI trading assistant. I can help you analyze your portfolio, suggest trades, and manage your watchlist. How can I help you today?',
timestamp: new Date().toISOString()
}
])
const [input, setInput] = useState('')
const [isLoading, setIsLoading] = useState(false)
const messagesEndRef = useRef<HTMLDivElement>(null)

const scrollToBottom = () => {
messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
}

useEffect(() => {
scrollToBottom()
}, [messages])

const handleSubmit = async (e: React.FormEvent) => {
e.preventDefault()

if (!input.trim() || isLoading) return

const userMessage = input.trim()
setInput('')

// Add user message
const userMsg: ChatMessage = {
id: Date.now().toString(),
role: 'user',
content: userMessage,
timestamp: new Date().toISOString()
}

setMessages(prev => [...prev, userMsg])
setIsLoading(true)

try {
// Call chat API
const response = await fetch('/api/chat', {
method: 'POST',
headers: { 'Content-Type': 'application/json' },
body: JSON.stringify({
message: userMessage,
user_id: 'default'
})
})

const data = await response.json()

// Add assistant response
const assistantMsg: ChatMessage = {
id: (Date.now() + 1).toString(),
role: 'assistant',
content: data.message,
timestamp: new Date().toISOString(),
actions: {
trades: data.trades,
watchlist_changes: data.watchlist_changes
}
}

setMessages(prev => [...prev, assistantMsg])

} catch (error) {
console.error('Chat error:', error)

// Add error message
const errorMsg: ChatMessage = {
id: (Date.now() + 1).toString(),
role: 'assistant',
content: 'Sorry, I encountered an error processing your request. Please try again.',
timestamp: new Date().toISOString()
}

setMessages(prev => [...prev, errorMsg])
} finally {
setIsLoading(false)
}
}

const renderMessageActions = (actions: any) => {
if (!actions) return null

const trades = actions.trades || []
const watchlistChanges = actions.watchlist_changes || []

return (
<div className="mt-2 space-y-2">
{trades.length > 0 && (
<div className="bg-terminal-bg/50 rounded-lg p-2">
<p className="text-xs text-gray-400 mb-1">Executed Trades:</p>
{trades.map((trade: any, i: number) => (
<div key={i} className="flex items-center gap-2 text-sm">
<div className={`w-2 h-2 rounded-full ${
trade.side === 'buy' ? 'bg-green-up' : 'bg-red-down'
}`} />
<span className="font-semibold">{trade.ticker}</span>
<span>{trade.side === 'buy' ? 'Bought' : 'Sold'}</span>
<span className="font-mono">{trade.quantity} shares</span>
{trade.status === 'pending_execution' && (
<span className="text-xs text-yellow-500">(Pending)</span>
)}
</div>
))}
</div>
)}

{watchlistChanges.length > 0 && (
<div className="bg-terminal-bg/50 rounded-lg p-2">
<p className="text-xs text-gray-400 mb-1">Watchlist Changes:</p>
{watchlistChanges.map((change: any, i: number) => (
<div key={i} className="flex items-center gap-2 text-sm">
<div className={`w-2 h-2 rounded-full ${
change.action === 'add' ? 'bg-green-up' : 'bg-red-down'
}`} />
<span>{change.action === 'add' ? 'Added' : 'Removed'}</span>
<span className="font-semibold">{change.ticker}</span>
{change.status && (
<span className={`text-xs ${
change.status === 'success' ? 'text-green-up' : 'text-red-down'
}`}>
({change.status})
</span>
)}
</div>
))}
</div>
)}
</div>
)
}

return (
<div className="bg-terminal-card border border-terminal-border rounded-lg p-4 h-full flex flex-col">
<div className="flex items-center justify-between mb-4">
<div className="flex items-center gap-2">
<div className="w-8 h-8 bg-gradient-to-br from-blue-primary to-purple-secondary rounded-lg flex items-center justify-center">
<MdAutoAwesome className="w-5 h-5" />
</div>
<div>
<h2 className="text-lg font-semibold">AI Assistant</h2>
<p className="text-xs text-gray-400">Powered by Cerebras</p>
</div>
</div>

<div className="flex items-center gap-2 text-xs text-gray-400">
<MdAutoAwesome className="w-4 h-4" />
<span>Auto-execute trades</span>
</div>
</div>

{/* Messages container */}
<div className="flex-1 overflow-y-auto mb-4 space-y-4 pr-2">
{messages.map((message) => (
<div
key={message.id}
className={`flex gap-3 ${
message.role === 'user' ? 'flex-row-reverse' : ''
}`}
>
<div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
message.role === 'user' 
? 'bg-blue-primary' 
: 'bg-gradient-to-br from-purple-secondary to-accent-yellow'
}`}>
{message.role === 'user' ? (
<FiUser className="w-4 h-4" />
) : (
<MdAutoAwesome className="w-4 h-4" />
)}
</div>

<div className={`max-w-[80%] rounded-lg p-3 ${
message.role === 'user'
? 'bg-blue-primary/20 border border-blue-primary/30'
: 'bg-terminal-bg/50 border border-terminal-border'
}`}>
<div className="flex items-center justify-between mb-1">
<span className="text-xs font-semibold">
{message.role === 'user' ? 'You' : 'FinAlly'}
</span>
<span className="text-xs text-gray-500">
{new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
</span>
</div>

<p className="text-sm whitespace-pre-wrap">{message.content}</p>

{renderMessageActions(message.actions)}
</div>
</div>
))}

{isLoading && (
<div className="flex gap-3">
<div className="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center bg-gradient-to-br from-purple-secondary to-accent-yellow">
<MdAutoAwesome className="w-4 h-4" />
</div>
<div className="bg-terminal-bg/50 border border-terminal-border rounded-lg p-3">
<div className="flex items-center gap-2">
<div className="w-2 h-2 bg-blue-primary rounded-full animate-pulse" />
<div className="w-2 h-2 bg-blue-primary rounded-full animate-pulse" style={{ animationDelay: '0.2s' }} />
<div className="w-2 h-2 bg-blue-primary rounded-full animate-pulse" style={{ animationDelay: '0.4s' }} />
<span className="text-sm text-gray-400">Thinking...</span>
</div>
</div>
</div>
)}

<div ref={messagesEndRef} />
</div>

{/* Input form */}
<form onSubmit={handleSubmit} className="border-t border-terminal-border pt-4">
<div className="relative">
<textarea
value={input}
onChange={(e) => setInput(e.target.value)}
onKeyDown={(e) => {
if (e.key === 'Enter' && !e.shiftKey) {
e.preventDefault()
handleSubmit(e)
}
}}
placeholder="Ask about your portfolio, suggest trades, or manage your watchlist..."
className="w-full bg-terminal-bg border border-terminal-border rounded-lg px-4 py-3 pr-12 focus:outline-none focus:border-blue-primary resize-none"
rows={2}
disabled={isLoading}
/>

<button
type="submit"
disabled={isLoading || !input.trim()}
className="absolute right-3 bottom-3 p-2 bg-blue-primary hover:bg-blue-primary/80 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
>
<FiSend className="w-4 h-4" />
</button>
</div>

<div className="flex items-center justify-between mt-2 text-xs text-gray-500">
<div className="flex items-center gap-4">
<span>Press Enter to send</span>
<span className="flex items-center gap-1">
<MdAutoAwesome className="w-3 h-3" />
Trades auto-execute
</span>
</div>
<button
type="button"
onClick={() => {
setInput("Analyze my portfolio and suggest some trades")
setTimeout(() => {
const submitBtn = document.querySelector('button[type="submit"]') as HTMLButtonElement
submitBtn?.click()
}, 100)
}}
className="text-blue-primary hover:text-blue-300 transition-colors"
>
Try example
</button>
</div>
</form>
</div>
)
}