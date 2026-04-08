# 🤖 Customer Support RAG Chatbot

A production-ready Retrieval-Augmented Generation (RAG) customer support system powered by **Claude Sonnet**, **ChromaDB**, and **Sentence Transformers** — with a React + Vite frontend and a FastAPI backend.

---

## 📐 Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        INDEXING LAYER                           │
│                                                                 │
│  Upload (PDF/DOCX/TXT/MD/Image)                                 │
│      │                                                          │
│      ▼                                                          │
│  Parser  ──►  Chunker  ──►  Embedder (SentenceTransformers)    │
│                                   │                             │
│                                   ▼                             │
│                          ChromaDB (Persistent)                  │
└─────────────────────────────────────────────────────────────────┘
          │
          │  vector store
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                       RETRIEVAL LAYER                           │
│                                                                 │
│  User Query ──► Input Guardrails ──► Query Expansion           │
│                                          │                      │
│                                          ▼                      │
│                              Vector Similarity Search           │
│                                          │                      │
│                                   Retrieved Chunks              │
└─────────────────────────────────────────────────────────────────┘
          │
          │  top-k chunks + metadata
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                      GENERATION LAYER                           │
│                                                                 │
│  RAG Prompt Builder ──► Claude Sonnet 4.6 ──► Output Guardrails│
│                                                      │          │
│                                              Answer + Sources   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🗂 Project Structure

```
customer-support-rag-chatbot/
├── backend/
│   ├── app/
│   │   ├── api/routes/
│   │   │   ├── chat.py          # POST /api/v1/chat
│   │   │   └── documents.py     # POST/GET/DELETE /api/v1/documents
│   │   ├── core/
│   │   │   ├── indexing/
│   │   │   │   ├── parser.py    # PDF, DOCX, TXT, MD, image parsing
│   │   │   │   ├── chunker.py   # Intelligent sentence/paragraph chunking
│   │   │   │   ├── embedder.py  # SentenceTransformers singleton
│   │   │   │   └── indexer.py   # Orchestrates parse→chunk→embed→store
│   │   │   ├── retrieval/
│   │   │   │   ├── retriever.py # Vector search + query expansion
│   │   │   │   └── guardrails.py# Input/output safety checks
│   │   │   ├── generation/
│   │   │   │   ├── generator.py # Claude Sonnet 4.6 generation
│   │   │   │   └── prompt_templates.py # System prompt + RAG builder
│   │   │   └── vectorstore/
│   │   │       └── chromadb_store.py  # ChromaDB wrapper
│   │   ├── models/
│   │   │   └── schemas.py       # Pydantic request/response models
│   │   ├── config.py            # Settings via pydantic-settings
│   │   ├── dependencies.py      # FastAPI DI singletons
│   │   └── main.py              # FastAPI app + lifespan
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── api/client.js        # Axios API wrapper
│   │   ├── hooks/
│   │   │   ├── useChat.js       # Chat state + send logic
│   │   │   └── useDocuments.js  # Document CRUD state
│   │   ├── components/
│   │   │   ├── Sidebar.jsx      # Left panel: upload + doc list
│   │   │   ├── FileUpload.jsx   # Drag-and-drop uploader
│   │   │   ├── DocumentList.jsx # Indexed document list
│   │   │   ├── ChatMessage.jsx  # Bubble + sources display
│   │   │   ├── ChatInput.jsx    # Auto-resizing textarea
│   │   │   └── TypingIndicator.jsx
│   │   ├── styles/globals.css   # Dark theme design system
│   │   ├── App.jsx              # Root layout
│   │   └── main.jsx             # React entry point
│   ├── index.html
│   ├── vite.config.js
│   ├── package.json
│   └── .env.example
│
├── .gitignore
└── README.md
```

---

## ⚡ Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- An [Anthropic API key](https://console.anthropic.com/)

---

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/customer-support-rag-chatbot.git
cd customer-support-rag-chatbot
```

---

### 2. Set up the backend

```bash
cd backend

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env and set your ANTHROPIC_API_KEY
```

> **Note:** The first run downloads the `all-MiniLM-L6-v2` embedding model (~90 MB) from Hugging Face. This is cached automatically.

Start the backend:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`.
Interactive docs: `http://localhost:8000/docs`

---

### 3. Set up the frontend

```bash
cd ../frontend

npm install
npm run dev
```

The UI will be available at `http://localhost:5173`.

---

## 📤 Uploading Documents

### Via the Web UI

1. Open `http://localhost:5173`
2. In the left sidebar, drag and drop (or click) the upload zone
3. Supported formats: **PDF, DOCX, DOC, TXT, MD, PNG, JPG, WEBP**
4. The document is parsed, chunked, embedded, and stored in ChromaDB
5. The knowledge base counter in the sidebar updates immediately

### Via the REST API

```bash
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -F "file=@/path/to/your/manual.pdf"
```

Response:
```json
{
  "filename": "manual.pdf",
  "doc_id": "uuid-here",
  "chunks_indexed": 42,
  "status": "success",
  "message": "Indexed 42 chunks successfully."
}
```

List all documents:

```bash
curl http://localhost:8000/api/v1/documents
```

Delete a document:

```bash
curl -X DELETE http://localhost:8000/api/v1/documents/{doc_id}
```

---

## 💬 Chat API

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How do I reset my password?",
    "expand_query": true
  }'
```

Response:
```json
{
  "answer": "To reset your password, go to the login page and click **Forgot Password**...",
  "sources": [
    {
      "doc_id": "...",
      "filename": "user-guide.pdf",
      "chunk_index": 5,
      "score": 0.87,
      "preview": "If you have forgotten your password, navigate to..."
    }
  ],
  "query_used": "How do I reset my password? password reset login credentials access",
  "flagged": false
}
```

---

## 🔍 How Retrieval Works

1. **Query Expansion** — The user query is enriched with support-domain synonyms (e.g., "cancel" → adds "cancellation terminate subscription"). This widens the semantic search surface for better recall.

2. **Embedding** — The expanded query is embedded using `all-MiniLM-L6-v2` (384-dim cosine space).

3. **Vector Search** — ChromaDB runs approximate nearest-neighbour search and returns the top-K chunks by cosine similarity.

4. **Score Filtering** — Chunks below the `RETRIEVAL_SCORE_THRESHOLD` (default 0.3) are dropped to reduce noise.

5. **Source Metadata** — Each chunk carries `doc_id`, `filename`, `page`, `chunk_index`, and `uploaded_at` for full traceability.

---

## 🧠 Prompt Engineering

The system uses a two-part prompt architecture:

### System Prompt (`prompt_templates.py`)
Sets the assistant's persona and enforces hard rules:
- Answer **only from provided context** — no hallucination
- If context is insufficient → ask a clarifying question
- Stay on topic (customer support only)
- Be concise, empathetic, and use bullet points for multi-step answers
- Never impersonate a human agent

### RAG Prompt (user turn)
Injects retrieved context chunks with source labels and relevance scores:

```
## Context Documents
[Document 1 | Source: manual.pdf | Relevance: 0.87]
<chunk text>

---

[Document 2 | Source: faq.txt | Relevance: 0.74]
<chunk text>

---

## Customer Question
How do I reset my password?

## Your Answer
```

When no relevant context is found, a separate `NO_CONTEXT_PROMPT` instructs the model to acknowledge the gap and ask a clarifying question — preventing hallucination.

---

## 🛡 Guardrails

| Layer | Check | Action |
|-------|-------|--------|
| Input | Query too short/long | Reject with message |
| Input | Prompt injection patterns | Reject with message |
| Input | Off-topic keywords | Log warning, allow through |
| Output | Hallucination markers (`as an AI language model`, etc.) | Block response |
| Output | Safe → send to client | Pass through |

---

## 🚀 Deploying to GitHub

```bash
# Inside the project root
git init
git add .
git commit -m "feat: initial production RAG chatbot"

# Create a repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/customer-support-rag-chatbot.git
git branch -M main
git push -u origin main
```

> ⚠️ Never commit your `.env` file. It's in `.gitignore`. Only commit `.env.example`.

---

## 🔧 Configuration Reference

All settings live in `backend/.env`. Key options:

| Variable | Default | Description |
|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | — | **Required**. Your Anthropic key |
| `CLAUDE_MODEL` | `claude-sonnet-4-6` | Generation model |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | SentenceTransformers model |
| `RETRIEVAL_TOP_K` | `5` | Chunks to retrieve per query |
| `RETRIEVAL_SCORE_THRESHOLD` | `0.3` | Min cosine similarity to include |
| `CHUNK_SIZE` | `512` | Max characters per chunk |
| `CHUNK_OVERLAP` | `64` | Overlap between consecutive chunks |
| `MAX_TOKENS` | `1024` | Max tokens in Claude's response |
| `TEMPERATURE` | `0.2` | Lower = more deterministic answers |
| `CHROMA_PERSIST_DIR` | `./data/chromadb` | Where ChromaDB stores data |

---

## 📦 Tech Stack

| Layer | Technology |
|-------|-----------|
| LLM | Claude Sonnet 4.6 (Anthropic) |
| Embeddings | `all-MiniLM-L6-v2` via Sentence Transformers |
| Vector DB | ChromaDB (persistent, local) |
| Backend | FastAPI + Uvicorn |
| Frontend | React 18 + Vite |
| Parsing | PyPDF2, python-docx |
| Styling | Custom CSS design system (dark theme) |

---

## 📄 License

MIT — use freely, attribute kindly.
