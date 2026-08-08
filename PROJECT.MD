# KnowledgeGraph AI

## 1. Problem

Build an enterprise RAG system that allows users to upload multiple documents and ask natural-language questions.

The system must provide accurate answers grounded in uploaded documents with source citations.

The solution should go beyond basic RAG by implementing:

- Hybrid retrieval
- Lightweight GraphRAG
- Self-correcting retrieval

---

## 2. Core User Flow

```text
Upload Documents
      ↓
Extract Text
      ↓
Chunk Documents + Metadata
      ↓
Generate Embeddings
      ↓
Vector Index
      ↓
Extract Entities + Relationships
      ↓
Knowledge Graph
      ↓
User Question
      ↓
Hybrid Retrieval
      ↓
Graph-aware Context
      ↓
Evaluate Retrieved Context
      ↓
 ┌───────────────┐
 │ Context enough?│
 └───────┬───────┘
     YES │ NO
         │  └──→ Rewrite Query → Retrieve Again
         ↓
    Grounded Answer
         ↓
    Citations + Sources

Maximum one retrieval retry.

3. MVP Features
Document Upload
Upload multiple PDF files
TXT support if easy
Validate file type and size
Display uploaded documents
Document Processing
Extract text using PyMuPDF
Split text into chunks
Preserve document name, page number and chunk ID
Generate embeddings
Retrieval
Semantic vector search using FAISS
Basic keyword search
Combine both into hybrid retrieval
Retrieve top relevant chunks
GraphRAG
Extract important entities from documents
Extract relationships between entities
Build a lightweight NetworkX graph
Use question-relevant graph relationships during retrieval
Display relevant graph relationships in the UI
Self-Correcting RAG

After initial retrieval:

Evaluate whether retrieved context is sufficient
If insufficient, reformulate the query
Perform one additional retrieval
If still insufficient, clearly say evidence is unavailable
Question Answering
Use Groq API
Answer only using retrieved evidence
Do not hallucinate
Clearly state when evidence is insufficient
Include source citations
UI
Clean React interface
Document upload
Document list
Chat/question interface
Answer display
Source/citation panel
Retrieval status
Knowledge graph visualization
4. Key Differentiators
Hybrid Retrieval

Combine:

Vector Search + Keyword Search

to improve retrieval for both semantic questions and exact terms such as policy names, contract numbers and entity names.

GraphRAG

Represent important entities and relationships:

Employee
   ↓ governed_by
Leave Policy
   ↓ affects
Benefits Policy
   ↓ exception_approved_by
HR Director

Use graph relationships to improve multi-document and multi-hop questions.

Self-Correction

The system must not blindly trust its first retrieval.

Question
 ↓
Retrieve
 ↓
Evaluate Context
 ↓
Insufficient?
 ↓ YES
Rewrite Query
 ↓
Retrieve Again
 ↓
Answer

Maximum one retry.

Grounded Answers

Answers must be based only on retrieved evidence and include citations.

If evidence is insufficient:

"I couldn't find sufficient evidence in the uploaded documents to answer this question."

5. Demo Knowledge Base

Use 6–8 interconnected synthetic enterprise documents:

employee_handbook.pdf
leave_policy.pdf
benefits_policy.pdf
hr_approval_policy.pdf
remote_work_policy.pdf
expense_policy.pdf
vendor_contract_a.pdf
vendor_contract_b.pdf

Documents should intentionally share entities and relationships so that multi-document and multi-hop questions can be demonstrated.

Example question:

An employee wants 20 consecutive days of unpaid leave. What approvals are required and when could their benefits be affected?

This should require information from multiple documents.

6. Example Insufficient-Evidence Question

Ask something not contained in the documents:

What happens to the employee's retirement contribution during extended unpaid leave?

The system should not invent an answer.

It should report that sufficient evidence was not found.

7. Technology Stack
Frontend
React
Vite
TypeScript
Tailwind CSS
Recharts if useful
Backend
Python
FastAPI
SQLAlchemy
SQLite
Document Processing
PyMuPDF
Embeddings
Sentence Transformers
all-MiniLM-L6-v2
Vector Search
FAISS
Graph
NetworkX
LLM
Groq API
Configuration
.env
Never expose API keys in frontend
Never commit secrets
8. Architecture
React + Vite
     ↓
FastAPI
     ↓
Document Processing
     ↓
 ┌───────────────┐
 │               │
Vector Index   Knowledge Graph
 │               │
 └───────┬───────┘
         ↓
 Hybrid + Graph Retrieval
         ↓
 Self-Correction
         ↓
      Groq LLM
         ↓
 Answer + Citations

Keep the architecture simple and modular. This is a 2–3 hour hackathon MVP, not a production distributed system.

9. API

Implement only the APIs required for the MVP:

GET  /api/health
POST /api/documents/upload
GET  /api/documents
POST /api/query
GET  /api/graph
10. Suggested Structure
backend/
├── main.py
├── config.py
├── database.py
├── models.py
├── schemas.py
├── routers/
│   ├── documents.py
│   ├── search.py
│   ├── chat.py
│   └── graph.py
├── services/
│   ├── document_processor.py
│   ├── embedding_service.py
│   ├── retrieval_service.py
│   ├── graph_service.py
│   ├── self_correction.py
│   ├── llm_service.py
│   └── citation_service.py
└── data/

frontend/
└── src/
    ├── pages/
    ├── components/
    ├── lib/
    └── types/

sample_documents/
11. Priority

Implement in this order:

Project setup
PDF upload and text extraction
Chunking + embeddings
FAISS retrieval
Groq question answering
Citations
Hybrid retrieval
Self-correction
Lightweight GraphRAG
Graph visualization
UI polish
Docker/deployment if time remains

Never sacrifice a working RAG pipeline for a bonus feature.

12. Important Development Rules
Do not implement the entire project at once.
Implement one milestone at a time.
Keep the application runnable after every milestone.
Do not modify unrelated files.
Do not introduce unnecessary technologies.
Prefer simple solutions suitable for a 2–3 hour hackathon.
Test each major feature before moving to the next.
Do not hard-code API keys.
Do not fabricate document information.
Preserve source metadata for citations.
13. Success Criteria

The MVP is successful when:

Multiple PDFs can be uploaded.
Documents are indexed.
Natural-language questions work.
Answers are grounded in uploaded documents.
Citations identify document and page.
Hybrid retrieval works.
Graph relationships can be demonstrated.
Weak retrieval triggers one retry.
Insufficient evidence is handled honestly.
The complete flow works through the UI.