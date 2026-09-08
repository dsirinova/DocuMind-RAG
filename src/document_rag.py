from __future__ import annotations

import re
from io import BytesIO
from pathlib import Path

import chromadb
from pypdf import PdfReader

try:
    from .ollama_client import chat
    from .embedding_model import get_embedding_model
except ImportError:
    from ollama_client import chat
    from embedding_model import get_embedding_model


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CHROMA_PATH = PROJECT_ROOT / "data" / "chroma_db"
COLLECTION_NAME = "uploaded_document"


def split_text(text: str, max_chars: int = 700, overlap_chars: int = 120) -> list[str]:
    cleaned = re.sub(r"\s+", " ", text).strip()
    sentences = re.split(r"(?<=[.!?])\s+", cleaned)
    chunks: list[str] = []
    current = ""
    for sentence in sentences:
        candidate = f"{current} {sentence}".strip()
        if current and len(candidate) > max_chars:
            chunks.append(current)
            current = current[-overlap_chars:] + " " + sentence
        else:
            current = candidate
    if current:
        chunks.append(current)
    return chunks


def extract_pdf_chunks(file_bytes: bytes, filename: str) -> list[dict]:
    reader = PdfReader(BytesIO(file_bytes))
    records: list[dict] = []
    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        for chunk_number, chunk in enumerate(split_text(text)):
            records.append(
                {
                    "id": f"page-{page_number}-chunk-{chunk_number}",
                    "text": chunk,
                    "metadata": {"source": filename, "page": page_number, "chunk": chunk_number + 1},
                }
            )
    return records


def index_pdf(file_bytes: bytes, filename: str) -> int:
    chunks = extract_pdf_chunks(file_bytes, filename)
    if not chunks:
        raise ValueError("PDF-dən oxuna bilən mətn çıxmadı. Bu, skan olunmuş PDF ola bilər.")
    vectors = get_embedding_model().encode(
        [f"passage: {chunk['text']}" for chunk in chunks], normalize_embeddings=True
    ).tolist()
    client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    try:
        client.delete_collection(COLLECTION_NAME)
    except (ValueError, chromadb.errors.NotFoundError):
        pass
    collection = client.create_collection(COLLECTION_NAME, metadata={"hnsw:space": "cosine"})
    collection.add(
        ids=[chunk["id"] for chunk in chunks],
        documents=[chunk["text"] for chunk in chunks],
        embeddings=vectors,
        metadatas=[chunk["metadata"] for chunk in chunks],
    )
    return len(chunks)


def retrieve(question: str, top_k: int = 4) -> list[dict]:
    query_vector = get_embedding_model().encode(f"query: {question}", normalize_embeddings=True).tolist()
    collection = chromadb.PersistentClient(path=str(CHROMA_PATH)).get_collection(COLLECTION_NAME)
    result = collection.query(query_embeddings=[query_vector], n_results=top_k, include=["documents", "metadatas", "distances"])
    return [
        {"text": text, "metadata": metadata, "similarity": 1 - distance}
        for text, metadata, distance in zip(result["documents"][0], result["metadatas"][0], result["distances"][0])
    ]


def answer(question: str) -> tuple[str, list[dict]]:
    results = retrieve(question)
    context = "\n\n".join(
        f"[MƏNBƏ {i} | səhifə {item['metadata']['page']}]\n{item['text']}"
        for i, item in enumerate(results, start=1)
    )
    prompt = f"""You are a document assistant. Answer in Azerbaijani.
Use only the CONTEXT below. If the answer is not present, say: \"Bu məlumat yüklənmiş sənəddə tapılmadı.\"
Be short, factual, and cite the relevant page as [Səhifə N].

CONTEXT:
{context}

QUESTION: {question}
ANSWER:"""
    response = chat([{"role": "user", "content": prompt}])
    if len(response.split()) < 4:
        response = f"{results[0]['text']} [Səhifə {results[0]['metadata']['page']}]"
    return response, results
