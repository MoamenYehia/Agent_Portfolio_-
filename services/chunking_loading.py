from langchain_community.document_loaders import TextLoader , PyPDFLoader , DirectoryLoader , UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter 
from dotenv import load_dotenv
from pathlib import Path
import os 
from langchain_core.documents import Document
import re 

load_dotenv()

import re
from pathlib import Path
from langchain_core.documents import Document
from langchain_community.document_loaders import (
    TextLoader,
    PyPDFLoader,
    UnstructuredMarkdownLoader
)
from langchain_text_splitters import RecursiveCharacterTextSplitter

def enrich_metadata(doc: Document, file: Path) -> Document:
    file_name = file.name
    stem_lower = file.stem.lower()
    suffix_lower = file.suffix.lower()

    # 1. Base file information
    doc.metadata["file_name"] = file_name
    doc.metadata["file_ext"] = suffix_lower[1:]

    # 2. Categorize Document Type & Project ID
    if "cv" in stem_lower or "resume" in stem_lower or suffix_lower == ".pdf":
        doc.metadata["doc_type"] = "resume"
        doc.metadata["project_id"] = "none"
    elif "readme" in stem_lower or suffix_lower == ".md":
        doc.metadata["doc_type"] = "project"
        clean_id = re.sub(r'(^readme_|_readme$|^readme$)', '', stem_lower).strip('_')
        doc.metadata["project_id"] = clean_id if clean_id else stem_lower
    else:
        doc.metadata["doc_type"] = "general"
        doc.metadata["project_id"] = "none"

    return doc


def chunking_loading(file_path: str | Path) -> list[Document]:
    file_path = Path(file_path)
    all_documents = []

    for file in file_path.glob("*"):
        if not file.is_file():
            continue

        loader = None
        ext = file.suffix.lower()

        if ext == ".md":
            loader = UnstructuredMarkdownLoader(file_path=str(file))
        elif ext == ".pdf":
            loader = PyPDFLoader(file_path=str(file))
        elif ext == ".txt":
            loader = TextLoader(file_path=str(file), encoding="utf-8")

        if loader:
            loaded_docs = loader.load()
            
            # Enrich metadata for each document before adding to list
            for doc in loaded_docs:
                enrich_metadata(doc, file)
                
            all_documents.extend(loaded_docs)

    if not all_documents:
        return []

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=700,
        chunk_overlap=200,
        separators=["\n\n", "\n", " ", ""]
    )
    
    # RecursiveCharacterTextSplitter automatically preserves all metadata fields
    chunks = text_splitter.split_documents(all_documents)
    return chunks

if __name__=="__main__":
    test_path=r"E:\AdvancedProjects\Portfolio_Agent\services\assets" 
    results=chunking_loading(test_path)
    print(f"Total Chunks Generated: {len(results)}\n")
    for i, result in enumerate(results[:3]):  # Preview first 3 chunks
        print(f"--- Chunk #{i} ---")
        print(f"Metadata: {result.metadata}")
        print(f"Content Snippet: {result.page_content[:150]}...\n")