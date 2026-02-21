from langchain_huggingface import (
    ChatHuggingFace,
    HuggingFaceEndpoint,
    HuggingFaceEmbeddings,
)
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader
from langchain.messages import SystemMessage, HumanMessage
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import tempfile
import os

load_dotenv()


def load_pdf(pdf_path):
    """Load a PDF file and return documents."""
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()
    return documents


def create_vector_store(documents):
    """Create a FAISS vector store from documents."""
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(documents)

    embeddings = HuggingFaceEmbeddings(model="sentence-transformers/all-MiniLM-L6-v2")
    db = FAISS.from_documents(chunks, embeddings)

    return db, embeddings


def get_chat_model():
    """Initialize the chat model."""
    llm = ChatHuggingFace(
        llm=HuggingFaceEndpoint(
            repo_id="Qwen/Qwen2.5-7B-Instruct",
            task="conversational",
            max_new_tokens=512,
            provider="auto",
        )
    )
    return llm


def answer_question(db, question):
    """Answer a question using the vector store and LLM."""
    retriever = db.as_retriever(search_kwargs={"k": 3})
    retriever_text = retriever.invoke(question)
    context_text = "\n\n".join(doc.page_content for doc in retriever_text)

    llm = get_chat_model()

    message = [
        (
            "system",
            "Answer ONLY using the provided context. "
            "If the answer is not in the context, say 'I don't know'. "
            "Keep the answer short and factual.",
        ),
        ("human", "Context:\n{context}\n\nQuestion: {question}"),
    ]

    prompt = ChatPromptTemplate.from_messages(message)
    chat_model = prompt | llm

    result = chat_model.invoke({"context": context_text, "question": question})
    return result.content, context_text


# Main execution (for testing)
if __name__ == "__main__":
    loader = PyPDFLoader("C:\\Users\\v-rohijain\\Downloads\\HF2609I015241984.pdf")
    document = loader.load()
    print(f"Loaded {len(document)} pages")

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(document)
    print(f"Split into {len(chunks)} chunks")

    embeddings = HuggingFaceEmbeddings(model="sentence-transformers/all-MiniLM-L6-v2")

    db = FAISS.from_documents(chunks, embeddings)
    retriever = db.as_retriever(search_kwargs={"k": 1})

    query = "What is the gst number?"
    retriever_text = retriever.invoke(query)
    context_text = "\n\n".join(doc.page_content for doc in retriever_text)

    llm = ChatHuggingFace(
        llm=HuggingFaceEndpoint(
            repo_id="Qwen/Qwen2.5-7B-Instruct",
            task="conversational",
            max_new_tokens=512,
            provider="auto",
        )
    )

    message = [
        (
            "system",
            "Answer ONLY using the provided context. "
            "If the answer is not in the context, say 'I don't know'. "
            "Keep the answer short and factual.",
        ),
        ("human", "Context:\n{context}\n\nQuestion: {question}"),
    ]

    prompt = ChatPromptTemplate.from_messages(message)
    chat_model = prompt | llm

    result = chat_model.invoke({"context": context_text, "question": query})
    print(result.content)
