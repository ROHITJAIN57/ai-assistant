import streamlit as st
import tempfile
import os
from main import load_pdf, create_vector_store, answer_question

# Page configuration
st.set_page_config(page_title="Document Q&A Chatbot", layout="wide")

# Title and description
st.title("📄 Document Q&A Chatbot")
st.markdown(
    "Upload a PDF document and ask questions about its content using AI-powered search and retrieval."
)

# Initialize session state
if "db" not in st.session_state:
    st.session_state.db = None
if "documents" not in st.session_state:
    st.session_state.documents = None
if "uploaded_filename" not in st.session_state:
    st.session_state.uploaded_filename = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Sidebar for file upload
with st.sidebar:
    st.header("📁 Upload Document")
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

    if uploaded_file is not None:
        # Save the uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.getbuffer())
            tmp_path = tmp_file.name

        # Process the file if it's different from the last one
        if uploaded_file.name != st.session_state.uploaded_filename:
            with st.spinner("Loading and processing document..."):
                try:
                    # Load PDF
                    st.session_state.documents = load_pdf(tmp_path)
                    st.success(f"✅ Loaded {len(st.session_state.documents)} pages")

                    # Create vector store
                    with st.spinner("Creating search index..."):
                        st.session_state.db, _ = create_vector_store(
                            st.session_state.documents
                        )
                    st.success("✅ Vector store created successfully!")
                    st.session_state.uploaded_filename = uploaded_file.name
                    st.session_state.chat_history = (
                        []
                    )  # Clear chat history on new document
                except Exception as e:
                    st.error(f"Error processing file: {str(e)}")

        # Display document info
        if st.session_state.documents:
            with st.expander("📊 Document Info"):
                st.write(f"**File name:** {uploaded_file.name}")
                st.write(f"**Number of pages:** {len(st.session_state.documents)}")
                st.write(f"**File size:** {uploaded_file.size / 1024:.2f} KB")

    # Clear button
    if st.session_state.db is not None:
        if st.button("🔄 Clear Document", use_container_width=True):
            st.session_state.db = None
            st.session_state.documents = None
            st.session_state.uploaded_filename = None
            st.session_state.chat_history = []
            st.rerun()

# Main chat interface
if st.session_state.db is None:
    st.info("👈 Please upload a PDF document from the sidebar to get started!")
else:
    st.success(f"✅ Document loaded: {st.session_state.uploaded_filename}")

    # Chat history display
    if st.session_state.chat_history:
        st.divider()
        st.subheader("💬 Conversation History")
        for chat in st.session_state.chat_history:
            with st.chat_message("user"):
                st.write(chat["question"])
            with st.chat_message("assistant"):
                st.write(chat["answer"])
            st.divider()

    # Input section
    st.subheader("❓ Ask a Question")

    with st.form("question_form", clear_on_submit=True):
        user_question = st.text_input(
            "Enter your question about the document:",
            placeholder="What is the main topic of this document?",
        )
        submit_button = st.form_submit_button("Send", use_container_width=True)

    # Process question
    if submit_button and user_question.strip():
        with st.spinner("Finding relevant information and generating answer..."):
            try:
                answer, context = answer_question(st.session_state.db, user_question)

                # Add to chat history
                st.session_state.chat_history.append(
                    {"question": user_question, "answer": answer, "context": context}
                )

                # Display the answer
                st.divider()
                st.subheader("📝 Answer")
                st.write(answer)

                # Display context with expander
                with st.expander("📖 View Source Context"):
                    st.write(context)

                st.rerun()

            except Exception as e:
                st.error(f"Error generating answer: {str(e)}")
    elif submit_button and not user_question.strip():
        st.warning("Please enter a question!")

# Footer
st.divider()
st.markdown(
    """
---
**About this chatbot:**
- Uses HuggingFace embeddings for semantic search
- Retrieves relevant context from your document
- Powered by Qwen2.5-7B-Instruct LLM
- Answers are based on the document content
"""
)
