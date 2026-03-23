import requests
import os
from dotenv import load_dotenv
from embeddings import get_embeddings
from vector_store import search

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found")

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.1-8b-instant"


TASK_PROMPTS = {
    'qa': (
        'You are a knowledgeable document assistant. '
        'Answer the question using the provided context as your primary source, citing page numbers like (Page X). '
        'If the context only partially answers the question, use your general knowledge to fill the gaps — '
        'but clearly label it: start document-based answers with "From the document:" '
        'and general knowledge additions with "Additionally:" '
        'Never fabricate specific claims about the document itself.'
    ),
    'summarise': (
        'You are a document analyst. Write a detailed structured summary using the context below. '
        'Use bold headings for each section. '
        'After the summary, add a brief "Context" section using your general knowledge '
        'to explain why this topic matters in the real world. '
        'Clearly label this section as "General context:"'
    ),
    'extract': (
        'Extract all action items, recommendations, and conclusions from the context below. '
        'Use bullet points. '
        'After each point add a short note explaining why it matters, drawing on your general knowledge. '
        'Label extracted points as "From document:" and your notes as "Why it matters:"'
    ),
    'explain': (
        'Using the context below as the foundation, explain the content in simple language for a complete beginner. '
        'Use real world analogies and examples from your general knowledge to make concepts clear. '
        'Structure it as: first explain what the document says, then give a simple analogy, then give a real world example. '
        'Never make the reader feel like they need prior knowledge.'
    ),
}


def _call_groq(messages: list) -> str:
    response = requests.post(
        GROQ_URL,
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": MODEL,
            "messages": messages,
            "max_tokens": 1024
        }
    )

    response.raise_for_status()

    return response.json()["choices"][0]["message"]["content"]


def rewrite_query(question: str) -> str:
    try:
        messages = [
            {
                "role": "system",
                "content": "Expand this into better semantic search query. Return only query."
            },
            {"role": "user", "content": question}
        ]
        return _call_groq(messages)
    except:
        return question


def query_document(doc_id: str, question: str, task: str = "qa") -> dict:
    # Step 1: rewrite
    expanded = rewrite_query(question)

    # Step 2: embed
    q_vec = get_embeddings([expanded])[0]

    # Step 3: retrieve
    chunks = search(doc_id, q_vec)

    if not chunks:
        return {
            "answer": "No relevant content found in document.",
            "sources": []
        }

    # Step 4: deduplicate context
    seen = set()
    unique_chunks = []

    for c in chunks:
        if c["text"] not in seen:
            seen.add(c["text"])
            unique_chunks.append(c)

    context = "\n\n".join(c["text"] for c in unique_chunks)

    task_instruction = TASK_PROMPTS.get(task, TASK_PROMPTS["qa"])

    messages = [
        {"role": "system", "content": task_instruction},
        {
            "role": "user",
            "content": f"Context:\n{context}\n\nQuestion: {question}"
        }
    ]

    # Step 5: LLM
    answer = _call_groq(messages)

    sources = sorted(set(c["page"] for c in unique_chunks))

    return {
        "answer": answer,
        "sources": sources
    }