from services.retrieving import retrieving
from langchain_core.tools import tool
from pathlib import Path

hybrid_retriever=retrieving()

@tool 
def search_portfolio_kb(query:str)->str:
    """Searches the portfolio knowledge base for detailed information about Moamen's 
    background, work experience, project technical details, architectures, and resume details.
    Use this for open-ended or descriptive questions (e.g., 'What is his experience with PyTorch?' 
    or 'How does MythLens verify claims?')."""

    try:
        docs=hybrid_retriever.invoke(query)
        if not docs:
            return"No relevant context found in the portfolio knowledge base ."

        formatted_docs=[]
        for i , doc in enumerate(docs,start=1):
            source=doc.metadata.get("file_name") or doc.metadata.get("soruce","Unknown")
            formatted_docs.append(f"--- Document [{i}] ({source}) ---\n{doc.page_content.strip()}")
        return "\n\n".join(formatted_docs)
    except Exception as e:
        return f"Error retrieving context from knowledge base: {str(e)}"
