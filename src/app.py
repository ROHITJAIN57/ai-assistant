import streamlit as st

from main import (
    load_sharepoint_local,
    create_vector_store,
    answer_question,
    general_chat,
)

st.set_page_config(page_title="AI Chat Assistant", layout="wide")
st.title("🤖 AI Assistant — Chat & SharePoint Q&A")

# -------- Session State --------
if "mode" not in st.session_state:
    st.session_state.mode = "general"  # "general" or "sharepoint"

if "db" not in st.session_state:
    st.session_state.db = None

if "documents" not in st.session_state:
    st.session_state.documents = None

if "general_history" not in st.session_state:
    st.session_state.general_history = []

if "doc_history" not in st.session_state:
    st.session_state.doc_history = []

if "sharepoint_loaded" not in st.session_state:
    st.session_state.sharepoint_loaded = False


# -------- Mode Selector --------
col1, col2 = st.columns(2)

with col1:
    if st.button("💬 General Chat", use_container_width=True):
        st.session_state.mode = "general"

with col2:
    if st.button("📄 SharePoint Chat", use_container_width=True):
        st.session_state.mode = "sharepoint"

st.divider()

# -------- SharePoint Loader (only in SharePoint mode) --------
if st.session_state.mode == "sharepoint":
    st.subheader("📄 SharePoint Chat (via OneDrive Sync)")

    sharepoint_path = st.text_input(
        "📂 Enter your local OneDrive-synced SharePoint folder path",
        placeholder="Please provide the path",
    )

    if st.button("🔄 Load SharePoint Knowledge Base", use_container_width=True):
        if not sharepoint_path:
            st.warning("Please enter a valid folder path.")
        else:
            with st.spinner("Indexing SharePoint folder..."):
                documents = load_sharepoint_local(sharepoint_path)
                db, _ = create_vector_store(documents)

                st.session_state.db = db
                st.session_state.documents = documents
                st.session_state.doc_history = []
                st.session_state.sharepoint_loaded = True

            st.success("✅ SharePoint knowledge base loaded!")
            st.write(f"Loaded {len(st.session_state.documents)} documents")
            st.write(st.session_state.documents[0].page_content[:1000])

# -------- Chat History UI --------
if st.session_state.mode == "general":
    st.subheader("💬 General Chat")

    for chat in st.session_state.general_history:
        with st.chat_message("user"):
            st.write(chat["question"])
        with st.chat_message("assistant"):
            st.write(chat["answer"])

else:
    if not st.session_state.sharepoint_loaded:
        st.info("Load your SharePoint folder to start chatting.")
    else:
        for chat in st.session_state.doc_history:
            with st.chat_message("user"):
                st.write(chat["question"])
            with st.chat_message("assistant"):
                st.write(chat["answer"])


# -------- Chat Input (ROOT LEVEL ONLY — no rerun loop) --------
prompt = st.chat_input(
    "Ask anything..."
    if st.session_state.mode == "general"
    else "Ask about SharePoint documents..."
)

if prompt:
    if st.session_state.mode == "general":
        with st.spinner("Thinking..."):
            answer = general_chat(prompt, st.session_state.general_history)
            st.session_state.general_history.append(
                {"question": prompt, "answer": answer}
            )

    else:
        if not st.session_state.sharepoint_loaded or st.session_state.db is None:
            st.warning("Please load SharePoint first.")
        else:
            with st.spinner("Searching SharePoint..."):
                answer, _ = answer_question(st.session_state.db, prompt)
                st.session_state.doc_history.append(
                    {"question": prompt, "answer": answer}
                )

    st.rerun()
