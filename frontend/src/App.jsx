import { useEffect, useRef } from 'react'
import { Bot, Trash2 } from 'lucide-react'
import { useChat } from './hooks/useChat'
import { useDocuments } from './hooks/useDocuments'
import Sidebar from './components/Sidebar'
import ChatMessage from './components/ChatMessage'
import ChatInput from './components/ChatInput'
import TypingIndicator from './components/TypingIndicator'
import './styles/globals.css'

export default function App() {
  const { messages, loading, send, clearMessages } = useChat()
  const { documents, loadingDocs, uploading, uploadProgress, upload, remove, refresh } = useDocuments()
  const bottomRef = useRef(null)

  // Auto-scroll to latest message
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  return (
    <div className="app-layout">
      <Sidebar
        documents={documents}
        loadingDocs={loadingDocs}
        uploading={uploading}
        uploadProgress={uploadProgress}
        onUpload={upload}
        onDelete={remove}
        onRefresh={refresh}
      />

      <main className="chat-panel">
        <header className="chat-header">
          <h2>
            <Bot size={16} color="var(--accent)" style={{ display: 'inline', marginRight: 7 }} />
            Customer Support Assistant
          </h2>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <div className="status">
              <span className="status-dot" />
              Online
            </div>
            {messages.length > 0 && (
              <button className="clear-btn" onClick={clearMessages}>
                <Trash2 size={13} /> Clear
              </button>
            )}
          </div>
        </header>

        <div className="messages-area">
          {messages.length === 0 && (
            <div className="empty-state">
              <Bot size={44} color="var(--accent)" strokeWidth={1.3} />
              <h3>How can I help you today?</h3>
              <p>
                Upload support documents in the sidebar, then ask any customer support question. I'll answer based on your knowledge base.
              </p>
            </div>
          )}

          {messages.map((msg) => (
            <ChatMessage key={msg.id} message={msg} />
          ))}

          {loading && <TypingIndicator />}
          <div ref={bottomRef} />
        </div>

        <ChatInput onSend={send} disabled={loading} />
      </main>
    </div>
  )
}

