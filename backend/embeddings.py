# backend/embeddings.py
import requests, os
from dotenv import load_dotenv
load_dotenv()

JINA_API_KEY = os.getenv('JINA_API_KEY')

def get_embeddings(texts: list[str]) -> list[list[float]]:
    all_embeddings = []

    for i in range(0, len(texts), 32):
        batch = texts[i:i+32]

        response = requests.post(
            'https://api.jina.ai/v1/embeddings',
            headers={
                'Authorization': f'Bearer {JINA_API_KEY}',
                'Content-Type': 'application/json'
            },
            json={
                'model': 'jina-embeddings-v2-base-en',
                'input': batch
            }
        )

        response.raise_for_status()
        data = response.json()

        all_embeddings.extend([item['embedding'] for item in data['data']])

    return all_embeddings
