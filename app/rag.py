from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import faiss
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

EMBED_MODEL = "text-embedding-3-small"
GEN_MODEL   = "gpt-4o-mini"

SYSTEM_PROMPT = (

      "Eres un asesor legal que responde en lenguaje coloquial. "
  "1) Si el CONTEXTO contiene la respuesta, úsalo y marca la sección como: 'Basado en el Excel'. "
  "2) Si el CONTEXTO no basta, ofrece una 'Información general' claramente separada. "
  "No afirmes hechos del Excel que no estén en el CONTEXTO. No des asesoría legal; solo información educativa."
)

SEP = "\n\n---\n\n"

def _load_artifacts():
    """Carga índice vectorial y metadatos persistidos por build_index.py"""
    idx_path  = Path("faiss.index")
    meta_path = Path("meta.json")
    cases_path= Path("cases.json")

    if not (idx_path.exists() and meta_path.exists() and cases_path.exists()):
        raise FileNotFoundError(
            "Faltan artefactos. Ejecuta antes: python app/build_index.py "
            "(debe generar faiss.index, meta.json, cases.json)."
        )

    index = faiss.read_index(str(idx_path))
    with meta_path.open("r", encoding="utf-8") as f:
        meta = json.load(f)
    with cases_path.open("r", encoding="utf-8") as f:
        cases = json.load(f)
    return index, meta, cases

def _embed(text: str) -> np.ndarray:
    e = client.embeddings.create(model=EMBED_MODEL, input=text).data[0].embedding
    v = np.array([e], dtype="float32")
    faiss.normalize_L2(v)
    return v

def _retrieve(index, meta, query: str, k: int = 4) -> str:
    """Busca los k chunks más relevantes y construye el CONTEXTO."""
    v = _embed(query)
    D, I = index.search(v, k)
    chunks = []
    for idx in I[0]:
        m = meta[idx]
        # Adjuntamos un encabezado corto con la providencia/fecha/tema para orientación
        header = f"[{m.get('providencia','?')} | {m.get('fecha','?')}]  TEMA: {m.get('tema','')}"
        body = m["chunk"]
        chunks.append(header + "\n" + body)
    return SEP.join(chunks)

def generate_answer(question: str, k: int = 4, temperature: float = 0.2) -> str:
    index, meta, _ = _load_artifacts()
    context = _retrieve(index, meta, question, k=k)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"CONTEXTO:{SEP}{context}{SEP}PREGUNTA: {question}\nResponde en español."}
    ]
    resp = client.chat.completions.create(
        model=GEN_MODEL,
        messages=messages,
        temperature=temperature
    )
    return resp.choices[0].message.content.strip()

def ask(question: str, k: int = 4) -> str:
    return generate_answer(question, k=k)

if __name__ == "__main__":
    print(ask("¿Cuál fue la sentencia del caso que habla de acoso escolar?"))