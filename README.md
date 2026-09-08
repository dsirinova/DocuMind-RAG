# DocuMind RAG

A local Retrieval-Augmented Generation (RAG) application that lets users upload a PDF, ask questions about it in Azerbaijani, and inspect the source pages used to produce the answer.

## Features

- Upload a text-based PDF or load a bundled sample document.
- Extract text while preserving page-level metadata.
- Split document text into overlapping chunks.
- Create multilingual embeddings with `intfloat/multilingual-e5-small`.
- Store and search vectors locally with ChromaDB.
- Generate grounded Azerbaijani answers with a local Ollama model.
- Display the retrieved source chunks, page numbers, and semantic similarity scores.

## How It Works

```text
PDF upload
   ↓
Text extraction with PyPDF
   ↓
Chunking with page metadata
   ↓
Embeddings with multilingual-e5-small
   ↓
ChromaDB vector store
   ↓
Semantic search for the user question
   ↓
Relevant chunks as context for Ollama
   ↓
Answer + source pages in Streamlit
```

The application does not send the entire PDF to the LLM. It retrieves only the most relevant chunks and uses them as context. This reduces token usage and helps keep answers grounded in the uploaded document.

## Tech Stack

- **Python**
- **Streamlit** for the web interface
- **PyPDF** for PDF text extraction
- **Sentence Transformers / Hugging Face** for embeddings
- **ChromaDB** as the local vector database
- **Ollama** for local LLM inference
- **Qwen 3 4B Instruct** as the default generation model

## Project Structure

```text
DocuMind-RAG/
├── app.py
├── requirements.txt
├── README.md
├── src/
│   ├── document_rag.py
│   ├── embedding_model.py
│   └── ollama_client.py
├── output/
│   └── pdf/
│       ├── novatech_emekdas_qaydalari.pdf
│       └── datastart_ai_telim_proqrami.pdf
```

> Keep this structure exactly as shown. `app.py` imports modules from `src/` and loads sample PDFs from `output/pdf/`.

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/dsirinova/DocuMind-RAG.git
cd DocuMind-RAG
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows:

```powershell
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Install and run Ollama

Install Ollama from [ollama.com](https://ollama.com), then download the default model:

```bash
ollama pull qwen3:4b-instruct
ollama serve
```

### 5. Start the application

Open another terminal in the project directory and run:

```bash
streamlit run app.py
```

The application will be available at `http://localhost:8501`.

## Usage

1. Upload your own text-based PDF from the right panel, or load a sample PDF.
2. Enter a question in the chat panel.
3. Click **Generate Answer**.
4. Review the generated answer and the retrieved source chunks below it.

Example questions for the NovaTech sample:

- `VPN nə vaxt məcburidir?`
- `İllik məzuniyyət sorğusu nə qədər əvvəl göndərilməlidir?`
- `Şübhəli e-poçt alan əməkdaş nə etməlidir?`

## Configuration

The default LLM is `qwen3:4b-instruct`. You can switch to another locally installed Ollama model:

```bash
OLLAMA_MODEL=qwen2.5:3b streamlit run app.py
