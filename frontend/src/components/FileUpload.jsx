import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { UploadCloud, CheckCircle, AlertCircle } from 'lucide-react'

const ACCEPTED = {
  'application/pdf': ['.pdf'],
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
  'application/msword': ['.doc'],
  'text/plain': ['.txt'],
  'text/markdown': ['.md', '.markdown'],
  'image/png': ['.png'],
  'image/jpeg': ['.jpg', '.jpeg'],
  'image/webp': ['.webp'],
}

export default function FileUpload({ onUpload, uploading, progress }) {
  const [status, setStatus] = useState(null) // { type: 'success'|'error', msg }

  const onDrop = useCallback(async (accepted) => {
    if (!accepted.length) return
    setStatus(null)
    try {
      const result = await onUpload(accepted[0])
      setStatus({ type: 'success', msg: `✓ "${result.filename}" — ${result.chunks_indexed} chunks indexed` })
      setTimeout(() => setStatus(null), 5000)
    } catch (err) {
      setStatus({ type: 'error', msg: err.message || 'Upload failed.' })
    }
  }, [onUpload])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: ACCEPTED,
    multiple: false,
    disabled: uploading,
    maxSize: 50 * 1024 * 1024,
  })

  return (
    <div>
      <div
        {...getRootProps()}
        className={`dropzone${isDragActive ? ' active' : ''}`}
        style={{ opacity: uploading ? 0.6 : 1 }}
      >
        <input {...getInputProps()} />
        <UploadCloud size={22} color="var(--accent)" />
        <p>
          {isDragActive
            ? 'Drop it here!'
            : uploading
            ? 'Uploading…'
            : <><strong>Click or drag</strong> a file here</>}
        </p>
        <p className="formats text-muted">PDF · DOCX · TXT · MD · PNG · JPG · WEBP</p>
      </div>

      {uploading && (
        <div className="progress-bar-wrap">
          <div className="progress-bar" style={{ width: `${progress}%` }} />
        </div>
      )}

      {status && (
        <div className={`upload-status ${status.type}`}>
          {status.type === 'success'
            ? <CheckCircle size={13} style={{ display: 'inline', marginRight: 5 }} />
            : <AlertCircle size={13} style={{ display: 'inline', marginRight: 5 }} />}
          {status.msg}
        </div>
      )}
    </div>
  )
}
