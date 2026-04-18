import axios from 'axios'

const BASE = '/api/v1'

const client = axios.create({
  baseURL: BASE,
  timeout: 60000,
})

// ── Chat ─────────────────────────────────────────────────────────────────────

export async function sendChat({ query, sessionId = null, expandQuery = true }) {
  const { data } = await client.post('/chat', {
    query,
    session_id: sessionId,
    expand_query: expandQuery,
  })
  return data
}

// ── Documents ─────────────────────────────────────────────────────────────────

export async function uploadDocument(file, onProgress) {
  const form = new FormData()
  form.append('file', file)
  const { data } = await client.post('/documents/upload', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (e) => {
      if (onProgress && e.total) onProgress(Math.round((e.loaded / e.total) * 100))
    },
  })
  return data
}

export async function listDocuments() {
  const { data } = await client.get('/documents')
  return data
}

export async function deleteDocument(docId) {
  const { data } = await client.delete(`/documents/${docId}`)
  return data
}

// ── Health ────────────────────────────────────────────────────────────────────

export async function fetchHealth() {
  const { data } = await axios.get('/health')
  return data
}
