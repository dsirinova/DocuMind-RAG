# DocuMind RAG

PDF sənədini yükləyib onun haqqında Azərbaycan dilində sual verməyə imkan yaradan lokal RAG portfolio layihəsi. Cavabın yanında istifadə olunan PDF səhifələri də görünür.

![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB) ![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B) ![Vector_DB](https://img.shields.io/badge/Vector_DB-ChromaDB-7C3AED) ![LLM](https://img.shields.io/badge/LLM-Ollama-111111)

## Nə edir?

1. İstifadəçi mətnli PDF yükləyir.
2. Sistem PDF-dən mətni çıxarır və səhifə nömrəsini saxlayır.
3. Mətn kiçik hissələrə (**chunk**) bölünür.
4. Hər chunk `multilingual-e5-small` modeli ilə embedding-ə çevrilir.
5. Embedding-lər lokal ChromaDB vektor bazasında saxlanılır.
6. İstifadəçi sual verəndə semantic search ən uyğun 4 chunk-ı tapır.
7. Tapılmış mətnlər context kimi Ollama-da çalışan LLM-ə göndərilir.
8. LLM yalnız həmin context əsasında cavab yaradır və mənbə səhifələri UI-da göstərilir.

```text
PDF → text extraction → chunks → embeddings → ChromaDB
                                             ↓
User question → query embedding → semantic search → context → Ollama LLM → answer + source pages
```

## Texnologiyalar

| Mövzu | Layihədə rolu |
|---|---|
| LLM | `qwen3:4b-instruct` cavabı yaradır |
| RAG | LLM-ə bütün PDF yox, uyğun hissələr verilir |
| Embeddings | Sual və mətnin mənasını vektora çevirir |
| Semantic Search | Açar söz eyni olmasa da oxşar mənalı hissələri tapır |
| Vector Database | ChromaDB embedding-ləri lokal saxlayır və axtarır |
| Hugging Face Transformers | `sentence-transformers` vasitəsilə E5 embedding modeli işləyir |
| Ollama | LLM-i API xərci olmadan lokal işlədir |
| Streamlit | PDF yükləmə və chat interfeysi |

Bu demo üçün LangChain, reranking, PEFT/LoRA və fine-tuning qəsdən istifadə edilmir. Kiçik bir RAG pipeline üçün birbaşa Python kodu daha aydındır. Reranking yalnız çoxlu və bir-birinə yaxın nəticələr olduqda, LoRA/fine-tuning isə modelin xüsusi davranışını öyrətmək lazım olduqda məntiqlidir.

## Quraşdırma

### 1. Layihəni klonla

```bash
git clone https://github.com/USERNAME/documind-rag.git
cd documind-rag
```

### 2. Virtual mühit yarat və kitabxanaları yüklə

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

### 3. Ollama və modeli quraşdır

Ollama-nı [rəsmi saytından](https://ollama.com) quraşdır, sonra:

```bash
ollama pull qwen3:4b-instruct
ollama serve
```

Başqa terminalda tətbiqi başlat:

```bash
streamlit run app.py
```

Brauzerdə `http://localhost:8501` açılacaq.

> Daha yüngül model üçün: `OLLAMA_MODEL=qwen2.5:3b streamlit run app.py`

## İstifadə

- Sağ tərəfdən öz PDF-ni yüklə və ya nümunə sənəd seç.
- Soldakı chat sahəsində sualını yaz.
- Məsələn: `VPN nə vaxt məcburidir?`
- Cavabın altında tapılan PDF hissələri və səhifə nömrələri göstərilir.

`output/pdf/` içində test üçün iki sənəd var:

- `novatech_emekdas_qaydalari.pdf`
- `datastart_ai_telim_proqrami.pdf`

## Fayl strukturu

```text
documind-rag/
├── app.py                         # Streamlit interfeysi
├── requirements.txt               # Python asılılıqları
├── src/
│   ├── document_rag.py            # PDF → retrieval → LLM pipeline-ı
│   ├── embedding_model.py         # embedding modelinin yüklənməsi
│   └── ollama_client.py           # lokal LLM-ə HTTP sorğusu
├── scripts/create_sample_pdfs.py  # test PDF-lərini yaradır
├── output/pdf/                    # nümunə PDF-lər
└── docs/code_explanation.md       # kodun ətraflı izahı
```

## Müsahibə üçün qısa izah

> “DocuMind RAG PDF sənədləri üzrə lokal sual-cavab tətbiqidir. PDF mətnini səhifə metadata-sı ilə chunk-lara bölürəm. Hər chunk `multilingual-e5-small` ilə embedding-ə çevrilir və ChromaDB-də saxlanılır. İstifadəçi sual verəndə semantic search uyğun chunk-ları tapır. Yalnız bu hissələr Ollama-dakı LLM-ə context kimi göndərilir. Buna görə cavab mənbəyə bağlı olur və istifadəçi səhifəni görə bilir.”

Ətraflı kod və müsahibə izahı üçün [docs/code_explanation.md](docs/code_explanation.md) faylına bax.
