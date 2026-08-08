import { useState, useEffect } from 'react';
import { api } from './lib/api';
import type { Document, QueryResponse } from './types';
import './App.css';

function App() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [question, setQuestion] = useState('');
  const [querying, setQuerying] = useState(false);
  const [queryResponse, setQueryResponse] = useState<QueryResponse | null>(null);
  const [queryError, setQueryError] = useState<string | null>(null);

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      const docs = await api.getDocuments();
      setDocuments(docs);
    } catch (error) {
      console.error('Failed to load documents:', error);
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (!file.name.endsWith('.pdf')) {
      setUploadError('Only PDF files are supported');
      return;
    }

    setUploading(true);
    setUploadError(null);

    try {
      await api.uploadDocument(file);
      await loadDocuments();
    } catch (error) {
      setUploadError(error instanceof Error ? error.message : 'Failed to upload document');
    } finally {
      setUploading(false);
    }
  };

  const handleQuery = async () => {
    if (!question.trim()) return;

    setQuerying(true);
    setQueryError(null);
    setQueryResponse(null);

    try {
      const response = await api.queryDocuments(question);
      setQueryResponse(response);
    } catch (error) {
      setQueryError(error instanceof Error ? error.message : 'Failed to query documents');
    } finally {
      setQuerying(false);
    }
  };

  return (
    <div className="app">
      <header className="header">
        <h1>KnowledgeGraph AI</h1>
        <p>Upload documents and ask questions</p>
      </header>

      <main className="main">
        <section className="upload-section">
          <h2>Upload Documents</h2>
          <div className="upload-area">
            <input
              type="file"
              id="file-upload"
              accept=".pdf"
              onChange={handleFileUpload}
              disabled={uploading}
              className="file-input"
            />
            <label htmlFor="file-upload" className="upload-button">
              {uploading ? 'Uploading...' : 'Select PDF File'}
            </label>
            {uploadError && <p className="error">{uploadError}</p>}
          </div>

          <div className="documents-list">
            <h3>Uploaded Documents ({documents.length})</h3>
            {documents.length === 0 ? (
              <p className="empty-state">No documents uploaded yet</p>
            ) : (
              <ul className="document-items">
                {documents.map((doc) => (
                  <li key={doc.id} className="document-item">
                    <span className="document-name">{doc.original_filename}</span>
                    <span className="document-meta">
                      {doc.total_pages} pages, {doc.total_chunks} chunks
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </section>

        <section className="query-section">
          <h2>Ask a Question</h2>
          <div className="query-area">
            <textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Enter your question here..."
              className="question-input"
              rows={3}
            />
            <button
              onClick={handleQuery}
              disabled={querying || !question.trim() || documents.length === 0}
              className="query-button"
            >
              {querying ? 'Processing...' : 'Ask'}
            </button>
            {queryError && <p className="error">{queryError}</p>}
          </div>

          {queryResponse && (
            <div className="response-area">
              <h3>Answer</h3>
              
              {queryResponse.self_corrected && (
                <p className="self-correction-info">
                  Initial retrieval was insufficient — query reformulated and searched again.
                </p>
              )}
              
              {!queryResponse.evidence_sufficient && (
                <p className="insufficient-evidence-warning">
                  Could not find sufficient evidence in uploaded documents.
                </p>
              )}
              
              <div className="answer-text">{queryResponse.answer}</div>
              
              {queryResponse.citations.length > 0 && (
                <div className="citations-area">
                  <h4>Sources ({queryResponse.citations.length})</h4>
                  <ul className="citations-list">
                    {queryResponse.citations.map((citation, index) => (
                      <li key={index} className="citation-item">
                        <span className="citation-doc">{citation.document}</span>
                        <span className="citation-meta">
                          Page {citation.page} • {citation.chunk_id}
                        </span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              
              <p className="chunks-info">
                Retrieved {queryResponse.retrieved_chunks} chunks in {queryResponse.retrieval_attempts} retrieval attempt{queryResponse.retrieval_attempts !== 1 ? 's' : ''}
              </p>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

export default App;
