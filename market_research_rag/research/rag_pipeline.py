import os
import time
from typing import List, Dict, Any
import chromadb
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
import numpy as np
from research.models import Document

# DOC LOADING AND CHUNKING

def load_and_chunk_docs():
    """
    Load documents and chunk them into pieces
    chunk size is 500words, with an overlap of 50words
    """
    # import the document
    documents = Document.objects.all()

    # the structure of how my splitting is designed
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 500,
        chunk_overlap = 50,
        length_function = len,
        separators = ["\n\n", "\n", " ", ""])
    
    all_chunks = []

    for doc in documents:
        chunks = text_splitter.split_text(doc.content)
        for i, chunk in enumerate(chunks):
            all_chunks.append({
                "document_id": doc.id,
                "chunk_index": i,
                "content": chunk,
                "metadata": {
                    "title": doc.title,
                    "company": doc.company,
                    "doc_type": doc.doc_type,
                    "date_filed": str(doc.date_filed)
                }
            })
    return all_chunks

# VECTOR DB SETUP

# chunks is a list of dictionaries- each dictionary represents a doc chunk with content and metadata
# https://docs.trychroma.com/docs/overview/getting-started is the chromadb docs

def vector_db(chunks: List[Dict]):
    """
    Setup chromadb vector db and store doc chunks with embeddings
    Everything that will ever be inputed into this RAG will nest itself into our chromadb called "financial_documents"
    This is basically creating the brain of our RAG, this is the only data the RAG will ever generate responses off of.
    """

    # this is how you initialize a chromadb client
    client= chromadb.Client()

    # this tries to create a collection in chromadb call "financial_documents"
    try:
        # collection in chromadb is a table database that holds all your doc chunks and embeddings
        collection = client.create_collection(
            name="financial_documents",
            # tells chroma to use cosine similarity for vector comparisions
            metadata={"hnsw:space": "cosine"}
        )
    # if collection already exists just retrieve it 
    except Exception:
        collection = client.get_collection("financial_documents")

    # all-MiniLM-L6-v2 is the model that converts text into numeric vectors that captures semantic meaning
    model = SentenceTransformer("all-MiniLM-L6-v2")
    # all-MiniLM-L6-v2 converts chunk texts into vector of numbers and then numpy uses "tolist" to convert those 
    # numbers into a list
    embeddings = [model.encode(chunk["content"]).tolist() for chunk in chunks]

    # failsafe if statement to prevent duplication
    if collection.count() == 0:
        # chromadb table db adds ids, documents, embeddings(numeric vector of chunks), metadata into 1 table collection
        collection.add(
            ids=[f"{chunk['document_id']}_{chunk['chunk_index']}" for chunk in chunks],
            documents=[chunk["content"] for chunk in chunks],
            embeddings=embeddings,
            metadatas=[chunk["metadata"] for chunk in chunks]
        )
        # Stored 10 chunks in ChromaDB collection financial_documents
        print(f"Stored {len(chunks)} chunks in ChromaDB collection '{collection.name}'")
    else:
        print(f"Collection already contains {collection.count()} chunks")

    return collection