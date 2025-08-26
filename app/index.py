# app/build_index.py
from __future__ import annotations
import json, math
from pathlib import Path

import numpy as np
import faiss
from dotenv import load_dotenv
from openai import OpenAI

from dataPrep import load_cases

load_dotenv()
client = OpenAI()


EMBED_MODEL = "text-embedding-3-small"
CHARS_PER_CHUNK = 1800
CHARS_OVERLAP = 200
BATCH_SIZE = 64  

def chunk_text(text: str, max_chars=CHARS_PER_CHUNK, overlap=CHARS_OVERLAP):
    chunks = []
    start = 0
    L = len(text)
    while start < L:
        end = min(start + max_chars, L)
        chunks.append(text[start:end])
        if end == L:
            break
        start = max(0, end - overlap)
    return chunks

def embed_batch(texts: list[str]) -> list[list[float]]:
    resp = client.embeddings.create(model=EMBED_MODEL, input=texts)
    return [d.embedding for d in resp.data]

def main():
    
    df = load_cases("data/sentencias_pasadas.xlsx")

    docs = df["doc"].tolist()
    # Metadatos útiles para citar
    metas_base = df[["providencia","fecha","tema"]].to_dict(orient="records")

   
    chunks, metas = [], []
    for i, (doc, mb) in enumerate(zip(docs, metas_base)):
        parts = chunk_text(doc)
        for p in parts:
            chunks.append(p)
            metas.append({"doc_id": i, "chunk": p, **mb})

    if not chunks:
        raise RuntimeError("No se generaron chunks. Revisa el ETL.")

   
    vectors = []
    total = len(chunks)
    steps = math.ceil(total / BATCH_SIZE)
    print(f"Generando embeddings: {total} chunks en {steps} lotes…")

    for i in range(0, total, BATCH_SIZE):
        batch = chunks[i:i+BATCH_SIZE]
        vectors.extend(embed_batch(batch))
        print(f"  Lote {i//BATCH_SIZE + 1}/{steps} listo")

    X = np.array(vectors, dtype="float32")
    faiss.normalize_L2(X)  

   
    index = faiss.IndexFlatIP(X.shape[1])
    index.add(X)
    print("Index ntotal:", index.ntotal)

   
    faiss.write_index(index, "faiss.index")
    with open("meta.json", "w", encoding="utf-8") as f:
        json.dump(metas, f, ensure_ascii=False)
    
    df.to_json("cases.json", orient="records", force_ascii=False)

    print("✅ Guardado: faiss.index, meta.json, cases.json")

if __name__ == "__main__":
    main()
