from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.src.app.routers import chat

app = FastAPI(title="ChatBot")

origins = ["http://localhost:5173"]

# Add the CORSMiddleware to the application
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # List of specific origins allowed
    allow_credentials=True,    # Allow cookies and Authorization headers
    allow_methods=["*"],       # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],       # Allow all HTTP headers
)

app.include_router(chat.router, prefix="/api", tags=["Chat"])

@app.get("/")
async def root():
    """
    Root endpoint for basic health check.
    """
    return {"message": "ChatBot is running"}