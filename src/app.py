import streamlit as st
import tempfile

from main import load_pdf, create_vector_store, answer_question, general_chat

st.set_page_config(page_title="AI Chat Assistant", layout="wide")
st.title("🤖 AI Assistant — Chat & PDF Q&A")

# -------- Session State --------
if "mode" not in st.session_state:
    st.session_state.mode = "general"  # or "pdf"

if "db" not in st.session_state:
    st.session_state.db = None
if "documents" not in st.session_state:
    st.session_state.documents = None
if "uploaded_filename" not in st.session_state:
    st.session_state.uploaded_filename = None
if "general_history" not in st.session_state:
    st.session_state.general_history = []
if "doc_history" not in st.session_state:
    st.session_state.doc_history = []

# -------- Mode Selector (Tabs-like header, no radios) --------
col1, col2 = st.columns(2)
with col1:
    if st.button("💬 General Chat", use_container_width=True):
        st.session_state.mode = "general"
with col2:
    if st.button("📄 PDF Chat", use_container_width=True):
        st.session_state.mode = "pdf"

st.divider()

# -------- PDF Upload (only in PDF mode) --------
if st.session_state.mode == "pdf":
    st.subheader("📄 PDF Chat")

    uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])

    if uploaded_file is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.getbuffer())
            tmp_path = tmp_file.name

        if uploaded_file.name != st.session_state.uploaded_filename:
            with st.spinner("Indexing document..."):
                st.session_state.documents = load_pdf(tmp_path)
                st.session_state.db, _ = create_vector_store(st.session_state.documents)
                st.session_state.uploaded_filename = uploaded_file.name
                st.session_state.doc_history = []
            st.success("✅ PDF loaded successfully!")

# -------- Chat History UI --------
if st.session_state.mode == "general":
    st.subheader("💬 General Chat")
    for chat in st.session_state.general_history:
        with st.chat_message("user"):
            st.write(chat["question"])
        with st.chat_message("assistant"):
            st.write(chat["answer"])
else:
    if st.session_state.db is None:
        st.info("Upload a PDF to start chatting.")
    else:
        for chat in st.session_state.doc_history:
            with st.chat_message("user"):
                st.write(chat["question"])
            with st.chat_message("assistant"):
                st.write(chat["answer"])

# -------- Chat Input (ROOT LEVEL ONLY) --------
prompt = st.chat_input(
    "Ask anything..."
    if st.session_state.mode == "general"
    else "Ask about the document..."
)

if prompt:
    if st.session_state.mode == "general":
        with st.spinner("Thinking..."):
            answer = general_chat(prompt, st.session_state.general_history)
            st.session_state.general_history.append(
                {"question": prompt, "answer": answer}
            )
    else:
        if st.session_state.db is None:
            st.warning("Please upload a PDF first.")
        else:
            with st.spinner("Searching document..."):
                answer, _ = answer_question(st.session_state.db, prompt)
                st.session_state.doc_history.append(
                    {"question": prompt, "answer": answer}
                )
