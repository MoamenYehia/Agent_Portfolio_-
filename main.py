import os
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from services.agent import portfolio_agent
from services.schemas import ChatRequest, ChatResponse, HealthResponse

load_dotenv()

app = FastAPI(
    title="Moamen's Portfolio AI Agent API",
    description="Backend API powering the interactive portfolio AI assistant using LangGraph & ChromaDB.",
    version="1.0.0"
)

# -------------------------------------------------------------
# CORS Configuration
# -------------------------------------------------------------
# Replace "*" with your actual GitHub Pages URL in production 
# (e.g., "https://moamenyehia.github.io")
allowed_origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://moamenyehia.github.io",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------------
# Endpoints
# -------------------------------------------------------------
@app.get("/", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint to verify backend status."""
    return HealthResponse(status="online", service="Portfolio Agent API")


@app.post(
    "/api/chat", 
    response_model=ChatResponse, 
    status_code=status.HTTP_200_OK,
    tags=["Agent"]
)
async def chat_endpoint(request: ChatRequest):
    """Processes user queries through the LangGraph portfolio agent."""
    if not request.message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Message field cannot be empty."
        )

    try:
        # Pass inputs to the agent graph
        inputs = {"messages": [("user", request.message)]}
        
        # Configure thread context for state management
        config = {"configurable": {"thread_id": request.thread_id}}
        
        # Invoke the LangGraph workflow
        output = portfolio_agent.invoke(inputs, config=config)
        
        # Extract the final AI message payload
        final_message = output["messages"][-1].content
        
        return ChatResponse(
            response=final_message,
            thread_id=request.thread_id,
            status="success"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent execution failed: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    # Bind to 0.0.0.0 instead of 127.0.0.1
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)