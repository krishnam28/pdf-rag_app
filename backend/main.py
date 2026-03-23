# backend/main.py
import uuid, shutil, os, tempfile
import uuid, shutil, os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from extractor import extract_from_pdf, extract_from_docx
from chunker import chunk_pages
from embeddings import get_embeddings
from vector_store import build_index
from rag import query_document

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        'http://localhost:5173',
        'http://localhost:3000',
    ],
    allow_methods=['*'],
    allow_headers=['*']
)

class QueryRequest(BaseModel):
    document_id: str
    question: str
    task: str = 'qa'

@app.get('/health')
def health():
    return {'status': 'ok'}

@app.post('/upload')
async def upload(file: UploadFile = File(...)):
    # Validate file type
    if not (file.filename.endswith('.pdf') or file.filename.endswith('.docx')):
        raise HTTPException(status_code=400, detail='Only PDF and DOCX files are supported')

    doc_id = str(uuid.uuid4())
    tmp_path = os.path.join(tempfile.gettempdir(), f'{doc_id}_{file.filename}')

    # Save uploaded file temporarily
    with open(tmp_path, 'wb') as f:
        shutil.copyfileobj(file.file, f)

    try:
        # Extract text
        if file.filename.endswith('.pdf'):
            pages = extract_from_pdf(tmp_path)
        else:
            pages = extract_from_docx(tmp_path)

        if not pages:
            raise HTTPException(status_code=400, detail='Could not extract text from file')

        # Chunk + embed + index
        chunks = chunk_pages(pages)
        embeddings = get_embeddings([c['text'] for c in chunks])
        build_index(doc_id, chunks, embeddings)

    finally:
        # Always delete temp file even if something fails
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    return {
        'document_id': doc_id,
        'filename': file.filename,
        'chunks': len(chunks)
    }

@app.post('/query')
def query(req: QueryRequest):
    try:
        result = query_document(req.document_id, req.question, req.task)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))