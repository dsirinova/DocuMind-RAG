from pathlib import Path

import streamlit as st

from src.document_rag import answer, index_pdf


PROJECT_ROOT = Path(__file__).resolve().parent
SAMPLE_DIR = PROJECT_ROOT / "output" / "pdf"
SAMPLES = {
    "NovaTech əməkdaş qaydaları": "novatech_emekdas_qaydalari.pdf",
    "DataStart AI təlim proqramı": "datastart_ai_telim_proqrami.pdf",
}

st.set_page_config(page_title="DocuMind RAG", page_icon="📄", layout="wide")
st.markdown(
    """
    <style>
      .block-container { max-width: 1120px; padding-top: 3rem; }
      h1 { color: #0b1838; letter-spacing: -0.035em; }
      .subtitle { color: #526079; font-size: 1.06rem; margin-bottom: 1.6rem; }
      .step { color: #1769e8; font-weight: 700; font-size: .88rem; letter-spacing: .04em; }
      .active-doc { background: #eaf2ff; border-radius: 10px; padding: .75rem 1rem; color: #0b1838; }
      .source-card { border: 1px solid #dbe2ef; border-radius: 12px; padding: 1rem 1.15rem;
                     margin: .7rem 0; background: #fff; color: #0b1838; }
      .meta { color: #526079; font-size: .88rem; margin-top: .65rem; }
      .score { color: #1769e8; font-weight: 700; }
      div[data-testid="stFormSubmitButton"] > button, div[data-testid="stButton"] > button {
        background: #1769e8; color: #fff; border: 1px solid #1769e8; font-weight: 700; }
    </style>
    """,
    unsafe_allow_html=True,
)


def load_into_rag(file_name: str, file_bytes: bytes) -> None:
    with st.spinner("PDF hazırlanır..."):
        chunk_count = index_pdf(file_bytes, file_name)
    st.session_state.indexed_file = file_name
    st.session_state.chunk_count = chunk_count
    st.session_state.last_answer = None


st.title("DocuMind RAG")
st.markdown('<p class="subtitle">PDF-ni yüklə və onun haqqında sual ver.</p>', unsafe_allow_html=True)

chat_col, upload_col = st.columns([1.4, 1], gap="large")

with chat_col:
    st.markdown('<p class="step">ADDIM 2</p>', unsafe_allow_html=True)
    st.subheader("Sual ver")
    ready = bool(st.session_state.get("indexed_file"))

    if ready:
        st.markdown(
            f'<div class="active-doc">Aktiv sənəd: <b>{st.session_state.indexed_file}</b></div>',
            unsafe_allow_html=True,
        )
    else:
        st.info("Sual vermək üçün sağ tərəfdən PDF seç.")

    with st.form("question_form", clear_on_submit=False):
        question = st.text_area(
            "Sənəddən nə bilmək istəyirsən?",
            placeholder="Məsələn: VPN nə vaxt məcburidir?",
            height=150,
            disabled=not ready,
        )
        ask = st.form_submit_button("Cavab yarat", use_container_width=True, disabled=not ready)

    if ask:
        if not question.strip():
            st.warning("Sualını yaz, sonra yenidən cəhd et.")
        else:
            try:
                with st.spinner("Cavab hazırlanır..."):
                    response, results = answer(question.strip())
                st.session_state.last_answer = (response, results)
            except Exception as error:
                st.error(f"Cavab yaradıla bilmədi: {error}")

    if ready:
        st.caption("Sınaq: “VPN nə vaxt məcburidir?” və ya “Məzuniyyət sorğusu nə vaxt göndərilir?”")

with upload_col:
    st.markdown('<p class="step">ADDIM 1</p>', unsafe_allow_html=True)
    st.subheader("PDF yüklə")
    uploaded_file = st.file_uploader("PDF faylını seç", type="pdf")

    if uploaded_file is not None:
        file_key = f"upload:{uploaded_file.name}:{uploaded_file.size}"
        if st.session_state.get("file_key") != file_key:
            try:
                load_into_rag(uploaded_file.name, uploaded_file.getvalue())
                st.session_state.file_key = file_key
                st.success("PDF yükləndi. Solda sualını ver.")
            except Exception as error:
                st.error(f"PDF indekslənmədi: {error}")

    st.caption("və ya nümunə sənəd seç")
    for label, filename in SAMPLES.items():
        if st.button(label, key=f"sample-{filename}", use_container_width=True):
            try:
                load_into_rag(filename, (SAMPLE_DIR / filename).read_bytes())
                st.session_state.file_key = f"sample:{filename}"
                st.rerun()
            except Exception as error:
                st.error(f"Nümunə sənəd açıla bilmədi: {error}")

if st.session_state.get("last_answer"):
    response, results = st.session_state.last_answer
    st.divider()
    st.subheader("Cavab")
    st.success(response)
    st.subheader("Mənbələr")
    for rank, result in enumerate(results, start=1):
        meta = result["metadata"]
        st.markdown(
            f'''<div class="source-card"><b>{rank}. Səhifə {meta['page']}</b><br>{result['text']}
            <div class="meta">{meta['source']} &nbsp;•&nbsp; Uyğunluq:
            <span class="score">{result['similarity']:.3f}</span></div></div>''',
            unsafe_allow_html=True,
        )
