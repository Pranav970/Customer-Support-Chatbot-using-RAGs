import { useState, useCallback, useRef } from 'react'
import { sendChat } from '../api/client'

export function useChat() {
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const sessionId = useRef(`session_${Date.now()}`)

  const send = useCallback(async (query) => {
    if (!query.trim()) return

    const userMsg = { role: 'user', content: query, id: Date.now() }
    setMessages((prev) => [...prev, userMsg])
    setLoading(true)
    setError(null)

    try {
      const res = await sendChat({
        query,
        sessionId: sessionId.current,
        expandQuery: true,
      })

      const assistantMsg = {
        role: 'assistant',
        content: res.answer,
        sources: res.sources || [],
        flagged: res.flagged || false,
        id: Date.now() + 1,
      }
      setMessages((prev) => [...prev, assistantMsg])
    } catch (err) {
      const msg = err?.response?.data?.detail || 'Something went wrong. Please try again.'
      setError(msg)
      setMessages((prev) => [
        ...prev,
        { role: 'error', content: msg, id: Date.now() + 1 },
      ])
    } finally {
      setLoading(false)
    }
  }, [])

  const clearMessages = useCallback(() => {
    setMessages([])
    setError(null)
    sessionId.current = `session_${Date.now()}`
  }, [])

  return { messages, loading, error, send, clearMessages }
}
