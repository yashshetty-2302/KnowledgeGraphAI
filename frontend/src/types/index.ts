export interface Document {
  id: number;
  filename: string;
  original_filename: string;
  upload_date: string;
  total_pages: number;
  total_chunks: number;
}

export interface Citation {
  document: string;
  page: number;
  chunk_id: string;
}

export interface QueryResponse {
  answer: string;
  citations: Citation[];
  retrieved_chunks: number;
}

export interface QueryRequest {
  question: string;
}
