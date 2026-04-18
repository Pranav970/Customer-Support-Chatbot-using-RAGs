import ReactMarkdown from 'react-markdown'
import { Bot, User, AlertTriangle } from 'lucide-react'

function SourceChips({ sources }) {
  if (!sources || !sources.length) return null
  return (
    <div className="sources">
      <div className="sources-label">Sources</div>
      {sources.map((s, i) => (
        <span key={i} className="source-chip" title={s.preview}>
          {s.filename}
          <span className="source-score">{(s.score * 100).toFixed(0)}%</span>
        </span>
      ))}
    </div>
  )
}

export default function ChatMessage({ message }) {
  const { role, content, sources, flagged } = message

  const avatarEl = (
    <div className={`avatar ${role}`}>
      {role === 'user' ? <User size={15} /> : role === 'error' ? <AlertTriangle size={15} /> : <Bot size={15} />}
    </div>
  )

  return (
    <div className={`message-row ${role}`}>
      {avatarEl}
      <div className={`bubble ${role}`}>
        {role === 'user' ? (
          <p>{content}</p>
        ) : (
          <ReactMarkdown>{content}</ReactMarkdown>
        )}
        {role === 'assistant' && !flagged && <SourceChips sources={sources} />}
      </div>
    </div>
  )
}
