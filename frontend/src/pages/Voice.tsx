import { useState, useRef } from 'react'
import api from '@/lib/api'

export default function Voice() {
  const [file, setFile] = useState<File | null>(null)
  const [transcript, setTranscript] = useState('')
  const [reply, setReply] = useState('')
  const [loading, setLoading] = useState(false)
  const audioRef = useRef<HTMLAudioElement>(null)

  async function send() {
    if (!file) return
    setLoading(true)
    const form = new FormData()
    form.append('file', file)
    try {
      const { data } = await api.post('/voice/chat', form)
      setTranscript(data.user_text)
      setReply(data.ai_text)
      const src = `data:audio/mpeg;base64,${data.audio_b64}`
      if (audioRef.current) {
        audioRef.current.src = src
        audioRef.current.play()
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-4 max-w-xl">
      <h1 className="text-2xl font-bold">Voice Assistant</h1>
      <div className="bg-white p-4 rounded shadow space-y-3">
        <input type="file" accept="audio/*" onChange={e=>setFile(e.target.files?.[0] || null)} />
        <button onClick={send} disabled={!file || loading} className="px-4 py-2 bg-blue-600 text-white rounded">{loading ? 'Processing...' : 'Send'}</button>
        <audio ref={audioRef} controls className="w-full" />
      </div>
      {(transcript || reply) && (
        <div className="bg-white p-4 rounded shadow">
          <div className="text-sm text-gray-500">Transcript</div>
          <div className="mb-2">{transcript}</div>
          <div className="text-sm text-gray-500">Assistant</div>
          <div>{reply}</div>
        </div>
      )}
    </div>
  )
} 