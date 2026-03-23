# backend/vector_store.py
import faiss, numpy as np

STORES = {}

def build_index(doc_id: str, chunks: list[dict], embeddings: list[list[float]]):
    vecs = np.array(embeddings, dtype='float32')
    index = faiss.IndexFlatL2(vecs.shape[1])
    index.add(vecs)
    STORES[doc_id] = {'index': index, 'chunks': chunks}

def search(doc_id: str, query_vec: list[float], k: int = 10) -> list[dict]:
    store = STORES.get(doc_id)
    if not store:
        raise ValueError(f'Document {doc_id} not found')
    q = np.array([query_vec], dtype='float32')
    distances, indices = store['index'].search(q, k)
    results = []
    seen_texts = set()
    for dist, idx in zip(distances[0], indices[0]):
        if idx == -1: continue
        chunk = store['chunks'][idx]
        if chunk['text'][:100] in seen_texts:
            continue
        seen_texts.add(chunk['text'][:100])
        results.append({**chunk, 'score': float(dist)})
    return [r for r in results if r['score'] < 3.0][:5]