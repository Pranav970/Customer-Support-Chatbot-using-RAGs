import { Bot } from 'lucide-react'

export default function TypingIndicator() {
  return (
    <div className="message-row assistant">
      <div className="avatar assistant">
        <Bot size={15} />
      </div>
      <div className="bubble assistant">
        <div className="typing">
          <span /><span /><span />
        </div>
      </div>
    </div>
  )
}
