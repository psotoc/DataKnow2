# Dockerfile (índice horneado)
FROM python:3.11-slim

# FAISS (faiss-cpu) requiere OpenMP en runtime
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código y datos (NO copiar .env)
COPY app ./app
COPY data ./data

# Copiar los artefactos ya generados (horneados)
COPY faiss.index ./faiss.index
COPY meta.json   ./meta.json
COPY cases.json  ./cases.json

# Streamlit expone 8501
EXPOSE 8501

# El índice ya está incluido: solo levantar la UI
CMD streamlit run app/ui.py --server.port 8501 --server.address 0.0.0.0
