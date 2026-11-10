import json
from pathlib import Path


def create_chunks(chunk_size=800, overlap=100):

    guide_path = Path(__file__).parent / "commercial_kpi_guide.txt"
    output_path = Path(__file__).parent / "rag_chunks.json"

    text = guide_path.read_text(encoding="utf-8")

    chunks = []
    start = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))
        content = text[start:end].strip()

        if content:
            chunks.append({
                "chunk_id": len(chunks) + 1,
                "content": content
            })

        if end == len(text):
            break

        start = end - overlap

    output_path.write_text(
        json.dumps(chunks, indent=2),
        encoding="utf-8"
    )

    print(f"Source characters: {len(text)}")
    print(f"Chunks created: {len(chunks)}")
    print(f"Saved to: {output_path.name}")


if __name__ == "__main__":
    create_chunks()