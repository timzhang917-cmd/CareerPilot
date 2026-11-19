"""Split rag/help.md into one chunk per "## " heading and save them to rag/chunks.json."""

import json
from pathlib import Path

RAG_DIR = Path(__file__).resolve().parent
SOURCE = RAG_DIR / "help.md"
OUTPUT = RAG_DIR / "chunks.json"


def split_by_heading(markdown):
    sections = []

    for line in markdown.splitlines():
        if line.startswith("## "):  # a "## " line starts a new chunk
            sections.append({"title": line[3:].strip(), "body": []})
        elif sections and line.strip():  # skip the "# " title above the first "## " and blank lines
            sections[-1]["body"].append(line.strip())

    return sections


def build_chunks(sections):
    chunks = []

    for number, section in enumerate(sections, start=1):
        body = "\n".join(section["body"])
        chunks.append(
            {
                "id": f"help-{number:02d}",
                "source": f"rag/{SOURCE.name}",
                "title": section["title"],
                "text": f"{section['title']}\n{body}",  # the title also helps retrieval
            }
        )

    return chunks


def main():
    chunks = build_chunks(split_by_heading(SOURCE.read_text(encoding="utf-8")))

    OUTPUT.write_text(
        json.dumps(chunks, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    for chunk in chunks:
        print(f"{chunk['id']}  {len(chunk['text']):>3} chars  {chunk['title']}")

    print(f"\n{len(chunks)} chunks saved to {OUTPUT.name}")


if __name__ == "__main__":
    main()
