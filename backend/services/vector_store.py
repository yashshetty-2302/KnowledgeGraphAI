import faiss
import numpy as np
import pickle
import os
from typing import List, Dict, Tuple
from config import Config

class VectorStore:
    def __init__(self):
        self.index = None
        self.chunks_metadata = []
        self.embedding_dim = 384  # all-MiniLM-L6-v2 dimension
        self.index_path = Config.FAISS_INDEX_PATH
        self.metadata_path = os.path.join(Config.DATA_DIR, "chunks_metadata.pkl")
        
        self._load_or_create_index()
    
    def _load_or_create_index(self):
        """Load existing index or create new one."""
        os.makedirs(Config.DATA_DIR, exist_ok=True)
        
        if os.path.exists(self.index_path) and os.path.exists(self.metadata_path):
            self.index = faiss.read_index(self.index_path)
            with open(self.metadata_path, 'rb') as f:
                self.chunks_metadata = pickle.load(f)
        else:
            self.index = faiss.IndexFlatL2(self.embedding_dim)
            self.chunks_metadata = []
    
    def add_chunks(self, embeddings: np.ndarray, metadata: List[Dict]):
        """Add chunks to the index."""
        if self.index is None:
            self.index = faiss.IndexFlatL2(self.embedding_dim)
        
        self.index.add(embeddings.astype('float32'))
        self.chunks_metadata.extend(metadata)
        self._save()
    
    def search(self, query_embedding: np.ndarray, k: int = 5) -> Tuple[List[Dict], np.ndarray]:
        """Search for similar chunks."""
        if self.index is None or self.index.ntotal == 0:
            return [], np.array([])
        
        query_embedding = query_embedding.reshape(1, -1).astype('float32')
        distances, indices = self.index.search(query_embedding, min(k, self.index.ntotal))
        
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx >= 0 and idx < len(self.chunks_metadata):
                result = self.chunks_metadata[idx].copy()
                result['distance'] = float(distance)
                results.append(result)
        
        return results, distances
    
    def _save(self):
        """Save index and metadata to disk."""
        faiss.write_index(self.index, self.index_path)
        with open(self.metadata_path, 'wb') as f:
            pickle.dump(self.chunks_metadata, f)
    
    def clear(self):
        """Clear the index."""
        self.index = faiss.IndexFlatL2(self.embedding_dim)
        self.chunks_metadata = []
        self._save()
