import os
from pathlib import Path
from dotenv import load_dotenv

from langchain_core.runnables import RunnableParallel, RunnableLambda
from langchain_community.vectorstores import Chroma
from langchain_community.retrievers import BM25Retriever 
from langchain_huggingface.embeddings import HuggingFaceEmbeddings

from services.chunking_loading import chunking_loading

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
PERSIST_DIR = str(BASE_DIR / "chroma_db")
ASSETS_DIR = BASE_DIR / "assets"


def retrieving():
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vector_store = Chroma(persist_directory=PERSIST_DIR, embedding_function=embeddings)
    
    # 1. Load local documents
    all_chunks = chunking_loading(ASSETS_DIR)
    if not all_chunks:
        raise ValueError(f"No files found in the directory: {ASSETS_DIR}")

    # 2. Check existing documents in ChromaDB using normalized paths
    existing_docs = vector_store.get()
    indexed_sources = set()

    if existing_docs and "metadatas" in existing_docs and existing_docs["metadatas"]:
        for meta in existing_docs["metadatas"]:
            if meta and "source" in meta:
                indexed_sources.add(os.path.normpath(meta["source"]))

    # 3. Add only new chunks
    new_chunks = []
    for chunk in all_chunks:
        source = chunk.metadata.get("source")
        if source and os.path.normpath(source) not in indexed_sources:
            new_chunks.append(chunk)

    if new_chunks:
        print(f"Adding {len(new_chunks)} new chunk(s) to Chroma DB...")
        vector_store.add_documents(new_chunks)
    else:
        print("Chroma DB is already up to date.")

    # 4. Construct Retrievers (Always executes and returns runnable chain)
    dense_retriever = vector_store.as_retriever(search_kwargs={"k": 3})
    
    bm25_retriever = BM25Retriever.from_documents(all_chunks)
    bm25_retriever.k = 3

    parallel_retriever = RunnableParallel(
        dense=dense_retriever,
        bm25=bm25_retriever
    )

    def merge_and_deduplicate(retrieved_docs):
        all_docs = retrieved_docs["dense"] + retrieved_docs["bm25"]
        unique_docs = {doc.page_content: doc for doc in all_docs}
        return list(unique_docs.values())

    return parallel_retriever | RunnableLambda(merge_and_deduplicate)


if __name__ == "__main__":
    test_query = "Start the frontend"
    
    # Initialize the hybrid retriever chain
    hybrid_retriever = retrieving()
    
    # Run retrieval query
    results = hybrid_retriever.invoke(test_query)
    
    print(f"\nFound {len(results)} relevant document(s) for query: '{test_query}'")
    print("=" * 50)
    
    for i, doc in enumerate(results, start=1):
        source = doc.metadata.get("file_name") or doc.metadata.get("source", "Unknown")
        doc_type = doc.metadata.get("doc_type", "N/A")
        project_id = doc.metadata.get("project_id", "N/A")
        
        print(f"[{i}] File: {source} | Type: {doc_type} | Project ID: {project_id}")
        print(f"Content:\n{doc.page_content.strip()}")
        print("-" * 50)