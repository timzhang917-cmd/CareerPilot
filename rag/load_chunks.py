"""Save the chunks and vectors from rag/chunks_with_embeddings.json into PostgreSQL."""

import json
import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv

RAG_DIR = Path(__file__).resolve().parent
INPUT = RAG_DIR / "chunks_with_embeddings.json"

CREATE_TABLE = """
    CREATE TABLE IF NOT EXISTS rag_chunk (
        id text PRIMARY KEY,
        source text NOT NULL,
        title text NOT NULL,
        content text NOT NULL,
        embedding_model text NOT NULL,
        embedding vector(1536) NOT NULL,
        updated_at timestamptz NOT NULL DEFAULT now()
    )
"""

# HNSW finds nearby vectors without comparing every row
CREATE_INDEX = """
    CREATE INDEX IF NOT EXISTS rag_chunk_embedding_idx
    ON rag_chunk USING hnsw (embedding vector_cosine_ops)
"""

# running the script again updates existing rows instead of adding duplicates
UPSERT = """
    INSERT INTO rag_chunk (id, source, title, content, embedding_model, embedding)
    VALUES (%s, %s, %s, %s, %s, %s::vector)
    ON CONFLICT (id) DO UPDATE SET
        source = EXCLUDED.source,
        title = EXCLUDED.title,
        content = EXCLUDED.content,
        embedding_model = EXCLUDED.embedding_model,
        embedding = EXCLUDED.embedding,
        updated_at = now()
"""


def main():
    load_dotenv(RAG_DIR.parent / ".env")
    chunks = json.loads(INPUT.read_text(encoding="utf-8"))

    # the block commits at the end, or saves nothing if any step fails
    with psycopg.connect(os.environ["DATABASE_URL"]) as connection:
        connection.execute(CREATE_TABLE)
        connection.execute(CREATE_INDEX)

        with connection.cursor() as cursor:
            cursor.executemany(
                UPSERT,
                [
                    (
                        chunk["id"],
                        chunk["source"],
                        chunk["title"],
                        chunk["text"],
                        chunk["embedding_model"],
                        json.dumps(chunk["embedding"]),
                    )
                    for chunk in chunks
                ],
            )

    print(f"{len(chunks)} chunks saved to rag_chunk")


if __name__ == "__main__":
    main()
