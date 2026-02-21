import streamlit as st
import tempfile

from main import load_pdf, create_vector_store, answer_question, general_chat

st.set_page_config(page_title="AI Chat Assistant", layout="wide")
st.title("🤖 AI Assistant — Chat & PDF Q&A")

# -------- Session State --------
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

tab1, tab2 = st.tabs(["💬 General Chat", "📄 PDF Chat"])

# -------- General Chat --------
with tab1:
    st.subheader("💬 General Chat")

    for chat in st.session_state.general_history:
        with st.chat_message("user"):
            st.write(chat["question"])
        with st.chat_message("assistant"):
            st.write(chat["answer"])

    user_input = st.chat_input("Ask anything...")
    if user_input:
        with st.spinner("Thinking..."):
            answer = general_chat(user_input, st.session_state.general_history)
            st.session_state.general_history.append(
                {"question": user_input, "answer": answer}
            )
        st.rerun()

# -------- PDF Chat --------
with tab2:
    st.subheader("📄 Chat with your PDF")

    # Upload UI ONLY here
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

    if st.session_state.db is None:
        st.info("Upload a PDF to start asking questions.")
    else:
        for chat in st.session_state.doc_history:
            with st.chat_message("user"):
                st.write(chat["question"])
            with st.chat_message("assistant"):
                st.write(chat["answer"])

        doc_input = st.chat_input("Ask about the document...")
        if doc_input:
            with st.spinner("Searching document..."):
                answer, _ = answer_question(st.session_state.db, doc_input)
                st.session_state.doc_history.append(
                    {"question": doc_input, "answer": answer}
                )
            st.rerun()
