import { useState, useCallback, useEffect } from 'react'
import { listDocuments, uploadDocument, deleteDocument } from '../api/client'

export function useDocuments() {
  const [documents, setDocuments] = useState([])
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [loadingDocs, setLoadingDocs] = useState(false)
  const [error, setError] = useState(null)

  const fetchDocs = useCallback(async () => {
    setLoadingDocs(true)
    try {
      const docs = await listDocuments()
      setDocuments(docs)
    } catch (err) {
      setError('Failed to load documents.')
    } finally {
      setLoadingDocs(false)
    }
  }, [])

  useEffect(() => { fetchDocs() }, [fetchDocs])

  const upload = useCallback(async (file) => {
    setUploading(true)
    setUploadProgress(0)
    setError(null)
    try {
      const result = await uploadDocument(file, setUploadProgress)
      await fetchDocs()
      return result
    } catch (err) {
      const msg = err?.response?.data?.detail || 'Upload failed.'
      setError(msg)
      throw new Error(msg)
    } finally {
      setUploading(false)
      setUploadProgress(0)
    }
  }, [fetchDocs])

  const remove = useCallback(async (docId) => {
    try {
      await deleteDocument(docId)
      setDocuments((prev) => prev.filter((d) => d.doc_id !== docId))
    } catch {
      setError('Failed to delete document.')
    }
  }, [])

  return {
    documents,
    uploading,
    uploadProgress,
    loadingDocs,
    error,
    upload,
    remove,
    refresh: fetchDocs,
  }
}
