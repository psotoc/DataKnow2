# Informe Técnico — Prueba DataKnow  
**Proyecto:** Consulta de histoia de demandas
---

## Explicación del caso
Un consultorio legal quiere **agilizar** la consulta de antecedentes de demandas (enfocadas en **redes sociales**) para orientar a clientes sobre **posibles acciones** y **probables sentencias**. Actualmente los abogados revisan un **Excel** con casos y resultados.  
El objetivo del PoC es **automatizar** esa consulta con un enfoque **RAG** (Retrieval-Augmented Generation): primero se **recupera** evidencia desde el Excel, luego un **LLM** genera una respuesta **coloquial y clara** usando **solo** ese contexto.

---

## Supuestos
- Dataset principal: `data/sentencias_pasadas.xlsx` (síntesis del caso, sentencia y metadatos).
- Tono **coloquial**, sin jerga legal innecesaria.
- Agente de OpenAi utilizado
- 
---

## Formas para resolver el caso y opción tomada
**Alternativas consideradas**
1. **Búsqueda full-text + reglas**
2. **Fine-tuning**
3. **RAG** 

**Arquitectura elegida**
- **Embeddings**: `text-embedding-3-small`.
- **Vector store**: **FAISS** (local).
- **Modelo generativo**: `gpt-4o-mini`.
- **UI**: **Streamlit** .

---

## Resultados del análisis de los datos y los modelos

- **Chunking**: fragmentos ~300–500 tokens para mejorar recuperación.
- **FAISS**: búsqueda vectorial local; `k` por defecto **4** 
- **Generación**: `gpt-4o-mini` con *prompt* que exige tono **coloquial**, **breve** y **limitado al contexto**.
- **Comportamiento esperado**
  - Preguntas cubiertas en el Excel → respuesta directa y clara.

---

## Futuros ajustes o mejoras
- **Trazabilidad** en UI: mostrar los fragmentos fuente usados.
- **Deployment**: alojamiento en azure o aws para el uso publico del PoC.

---

## Apreciaciones y comentarios (opcional)
RAG ofrece una solución **económica** y **actualizable** para este dominio.

---

## Guía de ejecución

### 1) Requisitos
- **Python 3.10+** (probado con 3.11)  
- Cuenta de **OpenAI** con API Key  

### 2) Configuración de la API Key
Crear un archivo `.env` en la raíz con:

**OpenAiKey**

git clone <URL_DEL_REPO>

cd <CARPETA_DEL_REPO>

python3 -m pip install -r requirements.txt

streamlit run app/ui.py


