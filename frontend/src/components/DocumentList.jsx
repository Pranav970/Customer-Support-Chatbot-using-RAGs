import { Trash2, FileText, Image, File } from 'lucide-react'

const TYPE_ICONS = {
  pdf:      <FileText size={13} color="var(--accent)" />,
  docx:     <FileText size={13} color="#7eb8ff" />,
  doc:      <FileText size={13} color="#7eb8ff" />,
  txt:      <File      size={13} color="var(--text-muted)" />,
  md:       <File      size={13} color="var(--text-muted)" />,
  markdown: <File      size={13} color="var(--text-muted)" />,
  png:      <Image     size={13} color="#ffb347" />,
  jpg:      <Image     size={13} color="#ffb347" />,
  jpeg:     <Image     size={13} color="#ffb347" />,
  webp:     <Image     size={13} color="#ffb347" />,
}

function formatDate(iso) {
  if (!iso) return ''
  try { return new Date(iso).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' }) }
  catch { return '' }
}

export default function DocumentList({ documents, onDelete, loading }) {
  if (loading) return <p className="no-docs">Loading documents…</p>
  if (!documents.length) return <p className="no-docs">No documents indexed yet.<br />Upload one above to get started.</p>

  return (
    <div>
      {documents.map((doc) => (
        <div key={doc.doc_id} className="doc-item">
          <div className="doc-item-info">
            <div className="doc-item-name" title={doc.filename}>
              {TYPE_ICONS[doc.file_type] || <File size={13} />}
              {' '}
              {doc.filename}
            </div>
            <div className="doc-item-meta">
              {doc.chunk_count} chunk{doc.chunk_count !== 1 ? 's' : ''} · {formatDate(doc.uploaded_at)}
            </div>
          </div>
          <button
            className="doc-delete-btn"
            onClick={() => onDelete(doc.doc_id)}
            title="Delete document"
            aria-label={`Delete ${doc.filename}`}
          >
            <Trash2 size={14} />
          </button>
        </div>
      ))}
    </div>
  )
}
