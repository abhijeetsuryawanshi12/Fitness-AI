import { useState } from 'react'
import api from '@/lib/api'

type Msg = { role: 'user' | 'ai', text: string }

export default function Chat() {
  const [messages, setMessages] = useState<Msg[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)

  async function send(e: React.FormEvent) {
    e.preventDefault()
    if (!input.trim()) return
    const toSend = input
    setMessages(m => [...m, { role: 'user', text: toSend }])
    setInput('')
    setLoading(true)
    try {
      const { data } = await api.post('/chat/', { message: toSend })
      setMessages(m => [...m, { role: 'ai', text: data.response }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-2xl">
      <div className="bg-white rounded shadow p-4 h-96 overflow-auto mb-3 space-y-2">
        {messages.map((m, i) => (
          <div key={i} className={m.role === 'user' ? 'text-right' : 'text-left'}>
            <span className={`inline-block px-3 py-2 rounded ${m.role==='user' ? 'bg-blue-600 text-white' : 'bg-gray-100'}`}>{m.text}</span>
          </div>
        ))}
        {loading && <div className="text-gray-500 text-sm">Thinking...</div>}
      </div>
      <form onSubmit={send} className="flex gap-2">
        <input className="flex-1 border rounded px-3 py-2" value={input} onChange={e=>setInput(e.target.value)} placeholder="Type a message..." />
        <button className="px-4 py-2 bg-blue-600 text-white rounded">Send</button>
      </form>
    </div>
  )
} 