import os
from typing import List, Tuple

from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_huggingface import (
    HuggingFaceEmbeddings,
    HuggingFaceEndpoint,
    ChatHuggingFace,
)

load_dotenv()


# ----------------------------
# Embeddings
# ----------------------------
def get_embeddings():
    return HuggingFaceEmbeddings(model="sentence-transformers/all-MiniLM-L6-v2")


# ----------------------------
# LLM (Chat model wrapper)
# ----------------------------
def get_llm():
    endpoint = HuggingFaceEndpoint(
        repo_id="Qwen/Qwen2.5-7B-Instruct",
        task="conversational",  # IMPORTANT: must be conversational for Qwen
        max_new_tokens=512,
        provider="auto",
    )
    return ChatHuggingFace(llm=endpoint)


# ----------------------------
# Load single PDF
# ----------------------------
def load_pdf(path: str):
    loader = PyPDFLoader(path)
    return loader.load()


# ----------------------------
# Load entire OneDrive/SharePoint folder (local sync)
# ----------------------------
def load_folder_recursive(root_folder: str):
    documents = []

    for root, _, files in os.walk(root_folder):
        for file in files:
            path = os.path.join(root, file)

            try:
                if file.lower().endswith(".pdf"):
                    documents.extend(PyPDFLoader(path).load())
                elif file.lower().endswith(".docx"):
                    documents.extend(Docx2txtLoader(path).load())
                elif file.lower().endswith(".txt"):
                    documents.extend(TextLoader(path, encoding="utf-8").load())
                else:
                    print(f"⚠️ Skipping {path}: unsupported file type")

            except Exception as e:
                print(f"⚠️ Skipping {path}: {e}")

    return documents


# ----------------------------
# Public API for SharePoint loader (used by app.py)
# ----------------------------
def load_sharepoint_local(root_folder: str):
    """
    Loads all supported documents from a local OneDrive-synced SharePoint folder.
    Supports: PDF, DOCX, TXT
    """
    documents = load_folder_recursive(root_folder)

    if not documents:
        raise ValueError("No supported documents found in the selected folder.")

    return documents


# ----------------------------
# Vector store
# ----------------------------
def create_vector_store(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=700,
        chunk_overlap=100,
    )

    chunks = splitter.split_documents(documents)
    embeddings = get_embeddings()

    db = FAISS.from_documents(chunks, embeddings)
    return db, len(chunks)


# ----------------------------
# PDF / Document Q&A (RAG)
# ----------------------------
def answer_question(db, question: str) -> Tuple[str, str]:
    retriever = db.as_retriever(
        search_type="mmr", search_kwargs={"k": 6, "fetch_k": 20}
    )
    docs = retriever.invoke(question)

    context_text = "\n\n".join(d.page_content for d in docs)

    llm = get_llm()

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are an helpful assistant and need to give the answer based on the query and try to give as much close answer you can.",
            ),
            ("human", "Context:\n{context}\n\nQuestion: {question}"),
        ]
    )

    chain = prompt | llm
    result = chain.invoke({"context": context_text, "question": question})

    return result.content, context_text


# ----------------------------
# General Chat (no documents)
# ----------------------------
def general_chat(question: str, history: List[dict]) -> str:
    llm = get_llm()

    messages = [("system", "You are a helpful assistant.")]
    for h in history:
        messages.append(("human", h["question"]))
        messages.append(("assistant", h["answer"]))

    messages.append(("human", question))

    prompt = ChatPromptTemplate.from_messages(messages)
    chain = prompt | llm

    result = chain.invoke({})
    return result.content
