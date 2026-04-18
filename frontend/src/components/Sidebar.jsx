import { HeadphonesIcon, RefreshCw } from 'lucide-react'
import FileUpload from './FileUpload'
import DocumentList from './DocumentList'

export default function Sidebar({ documents, loadingDocs, uploading, uploadProgress, onUpload, onDelete, onRefresh }) {
  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <h1>
          <HeadphonesIcon size={18} color="var(--accent)" />
          Support RAG
        </h1>
        <p className="subtitle">AI-powered customer support</p>
      </div>

      <div className="sidebar-section">
        <div className="sidebar-section-title">Upload Documents</div>
        <FileUpload
          onUpload={onUpload}
          uploading={uploading}
          progress={uploadProgress}
        />
      </div>

      <div className="sidebar-section" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div className="sidebar-section-title" style={{ marginBottom: 0 }}>
          Knowledge Base
          <span style={{ marginLeft: 8, background: 'var(--surface2)', border: '1px solid var(--border)', borderRadius: 100, padding: '1px 8px', fontSize: '0.7rem', color: 'var(--text-muted)' }}>
            {documents.length} doc{documents.length !== 1 ? 's' : ''}
          </span>
        </div>
        <button
          onClick={onRefresh}
          style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)', display: 'flex' }}
          title="Refresh document list"
          aria-label="Refresh"
        >
          <RefreshCw size={13} />
        </button>
      </div>

      <div className="doc-list">
        <DocumentList documents={documents} onDelete={onDelete} loading={loadingDocs} />
      </div>
    </aside>
  )
}
