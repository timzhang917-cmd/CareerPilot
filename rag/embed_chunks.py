"""Turn each chunk in rag/chunks.json into a vector and save the result."""

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

RAG_DIR = Path(__file__).resolve().parent
INPUT = RAG_DIR / "chunks.json"
OUTPUT = RAG_DIR / "chunks_with_embeddings.json"

EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSIONS = 1536


def main():
    load_dotenv(RAG_DIR.parent / ".env")
    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url="https://api.openai.com/v1",
    )

    chunks = json.loads(INPUT.read_text(encoding="utf-8"))

    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=[chunk["text"] for chunk in chunks],
    )
    vectors = [item.embedding for item in response.data]

    # stop before saving if any chunk is missing a vector or has the wrong size
    if len(vectors) != len(chunks):
        raise ValueError(f"Expected {len(chunks)} vectors, got {len(vectors)}.")

    for chunk, vector in zip(chunks, vectors):
        if len(vector) != EMBEDDING_DIMENSIONS:
            raise ValueError(f"{chunk['id']} has {len(vector)} dimensions.")

        chunk["embedding_model"] = EMBEDDING_MODEL
        chunk["embedding"] = vector

    OUTPUT.write_text(
        json.dumps(chunks, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"{len(chunks)} chunks, {EMBEDDING_DIMENSIONS} dimensions each")
    print(f"Tokens used: {response.usage.total_tokens}")
    print(f"Saved to {OUTPUT.name}")


if __name__ == "__main__":
    main()
