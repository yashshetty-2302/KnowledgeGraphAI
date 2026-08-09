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

  const handleFileUpload = async (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
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
      setUploadError(
        error instanceof Error ? error.message : 'Failed to upload document'
      );
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
      setQueryError(
        error instanceof Error ? error.message : 'Failed to query documents'
      );
    } finally {
      setQuerying(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleQuery();
    }
  };

  return (
    <div className="app">
      <header className="header">
        <h1>KnowledgeGraph AI</h1>
        <p>Enterprise Intelligence</p>
      </header>

      <main className="main">
        {/* Left Column - Document Management */}
        <section>
          <h2>Document Management</h2>

          <div className="upload-area">
            <input
              type="file"
              id="file-upload"
              accept=".pdf"
              onChange={handleFileUpload}
              disabled={uploading}
              className="file-input"
            />

            <label htmlFor="file-upload" className="upload-card">
              <div className="upload-icon">📄</div>

              <div className="upload-title">
                Upload Enterprise Documents
              </div>

              <div className="upload-subtitle">
                PDF files supported
              </div>

              <button
                className="upload-button"
                disabled={uploading}
                onClick={(e) => {
                  e.preventDefault();
                  document.getElementById('file-upload')?.click();
                }}
              >
                {uploading ? (
                  <>
                    <span className="loading-spinner"></span>
                    Uploading...
                  </>
                ) : (
                  'Select PDF File'
                )}
              </button>
            </label>

            {uploadError && <p className="error">{uploadError}</p>}
          </div>

          <div className="documents-list">
            <h3>Uploaded Documents ({documents.length})</h3>

            {documents.length === 0 ? (
              <p className="empty-state">
                No documents uploaded yet
              </p>
            ) : (
              <ul className="document-items">
                {documents.map((doc) => (
                  <li key={doc.id} className="document-item">
                    <span className="document-name">
                      {doc.original_filename}
                    </span>

                    <span className="document-meta">
                      {doc.total_pages} pages • {doc.total_chunks} chunks
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </section>

        {/* Right Column - Query & Results */}
        <section>
          <h2>Ask Questions</h2>

          <div className="query-area">
            <textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask a question about your enterprise documents..."
              className="question-input"
              rows={4}
              disabled={querying}
            />

            <button
              onClick={handleQuery}
              disabled={
                querying ||
                !question.trim() ||
                documents.length === 0
              }
              className="query-button"
            >
              {querying ? (
                <>
                  <span className="loading-spinner"></span>
                  Processing...
                </>
              ) : (
                'Ask Question'
              )}
            </button>

            {queryError && <p className="error">{queryError}</p>}
          </div>

          {queryResponse && (
            <div className="response-area">
              {/* Status Badges */}
              <div className="status-badges">
                <span
                  className={`status-badge ${
                    queryResponse.self_corrected
                      ? 'self-corrected'
                      : 'direct'
                  }`}
                >
                  {queryResponse.self_corrected
                    ? 'Self-corrected'
                    : 'Direct retrieval'}
                </span>

                {queryResponse.graph_used && (
                  <span className="status-badge graph-used">
                    Knowledge Graph used
                  </span>
                )}

                <span className="status-badge attempts">
                  {queryResponse.retrieval_attempts} retrieval attempt
                  {queryResponse.retrieval_attempts !== 1 ? 's' : ''}
                </span>

                {!queryResponse.evidence_sufficient && (
                  <span className="status-badge insufficient">
                    Insufficient evidence
                  </span>
                )}
              </div>

              {/* Insufficient Evidence Warning */}
              {!queryResponse.evidence_sufficient && (
                <div className="insufficient-evidence">
                  <h4>Insufficient Evidence</h4>

                  <p>
                    The uploaded documents do not contain enough
                    information to answer this question.

                    {queryResponse.self_corrected &&
                      ' The system attempted to reformulate the query but still could not find sufficient evidence.'}
                  </p>
                </div>
              )}

              {/* Answer */}
              <div className="answer-card">
                <h4>AI Answer</h4>

                <div className="answer-text">
                  {queryResponse.answer}
                </div>
              </div>

              {/* Knowledge Graph Section */}
              {queryResponse.graph_used && (
                <div className="graph-section">
                  <h4>Knowledge Graph Context</h4>

                  {queryResponse.graph_entities.length === 0 &&
                   queryResponse.graph_relationships.length === 0 ? (
                    <p className="no-graph-data">
                      No relationship data was identified for this query.
                    </p>
                  ) : (
                    <>
                      {/* Entities */}
                      {queryResponse.graph_entities.length > 0 && (
                        <div className="graph-entities">
                          <div>Entities</div>

                          <div className="entity-pills">
                            {queryResponse.graph_entities.map(
                              (entity, index) => (
                                <span
                                  key={index}
                                  className="entity-pill"
                                >
                                  {entity}
                                </span>
                              )
                            )}
                          </div>
                        </div>
                      )}

                      {/* Relationships */}
                      {queryResponse.graph_relationships.length > 0 && (
                        <div className="graph-relationships">
                          <div className="graph-label">
                            Relationships
                          </div>

                          <div className="relationship-list">
                            {queryResponse.graph_relationships.map(
                              (rel, index) => {
                                // Parse relationship: "source relation target"
                                const parts = rel.split(' ');
                                if (parts.length < 3) return null;
                                
                                // Find the relation type (middle part)
                                const relationType = parts[1];
                                const source = parts[0];
                                const target = parts.slice(2).join(' ');

                                return (
                                  <div
                                    key={index}
                                    className="relationship-item"
                                  >
                                    <div className="graph-node source-node">
                                      {source}
                                    </div>

                                    <div className="graph-edge">
                                      <span className="relation-label">
                                        {relationType}
                                      </span>
                                      <span className="graph-arrow">
                                        →
                                      </span>
                                    </div>

                                    <div className="graph-node target-node">
                                      {target}
                                    </div>
                                  </div>
                                );
                              }
                            )}
                          </div>
                        </div>
                      )}
                    </>
                  )}
                </div>
              )}

              {/* Citations */}
              {queryResponse.citations.length > 0 && (
                <div className="citations-section">
                  <h4>
                    Sources ({queryResponse.citations.length})
                  </h4>

                  <ul className="citations-list">
                    {queryResponse.citations.map(
                      (citation, index) => (
                        <li
                          key={index}
                          className="citation-item"
                        >
                          <span className="citation-doc">
                            {citation.document}
                          </span>

                          <span className="citation-meta">
                            Page {citation.page} • {citation.chunk_id}
                          </span>
                        </li>
                      )
                    )}
                  </ul>
                </div>
              )}

              {/* Retrieval Info */}
              <p
                style={{
                  fontSize: '0.85rem',
                  color: '#6b7280',
                  marginTop: '1rem',
                  opacity: 0.8,
                }}
              >
                Retrieved {queryResponse.retrieved_chunks} chunks in{' '}
                {queryResponse.retrieval_attempts} retrieval attempt
                {queryResponse.retrieval_attempts !== 1
                  ? 's'
                  : ''}
              </p>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

export default App;