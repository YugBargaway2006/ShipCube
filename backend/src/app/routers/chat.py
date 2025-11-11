from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# Import the decoupled services
from backend.src.app.services import nlp_service, email_service
from backend.src.summarizer import get_n_tokens_summary

# --- Pydantic Models (as defined above) ---
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, alias="text")

    class Config:
        populate_by_name = True


class ExtractedEntity(BaseModel):
    text: str
    label: str

class FoundEmail(BaseModel):
    id: str
    from_email: str = Field(..., alias="from")
    subject: str
    body: str
    class Config:
        populate_by_name = True 

class ChatResponse(BaseModel):
    reply: str
    entities: List[ExtractedEntity]
    found_emails: Optional[List[FoundEmail]] = None
    draft_details: Optional[dict] = None


def highlight_entities(text, entities):
    for entity in entities:
        text = text.replace(entity["text"], f"<strong>{entity['text']}</strong>")
    return text



# --- APIRouter Instance ---
router = APIRouter()

# --- API Endpoints ---
@router.get("/health")
async def health_check():
    """
    Health check endpoint for the chat router.
    """
    return {"status": "ok", "router": "chat"}


@router.post("/chat/query", response_model=ChatResponse)
async def handle_chat_message(request: ChatRequest):
    """
    Main endpoint for the chat UI to interact with the AI agent.
    
    1. Validates the incoming ChatRequest.
    2. Processes the message for NLP entities.
    3. (Simulates) action based on the message.
    4. Returns a structured ChatResponse.
    """
    try:
        # 1. Call NLP service
        entities = nlp_service.process_text_for_entities(request.message)
        
        reply_message = "Message processed."
        found_emails = None
        draft_details = None

        summary = get_n_tokens_summary(request.message)
        highlighted_summary = highlight_entities(summary, entities)
        reply_message = highlighted_summary

        # 2. Simple logic to call email service (simulation)
        # if "search" in request.message.lower() or "find" in request.message.lower():
        #     query = request.message.replace("search", "").replace("find", "").strip()
        #     found_emails = await email_service.search_inbox(query)
        #     reply_message = f"Search complete. Found {len(found_emails)} email(s)."
            
        # elif "draft" in request.message.lower():
        #     # (This is a simplified example; a real agent would parse 'to', 'subject')
        #     draft_details = await email_service.draft_email(
        #         to="test@example.com", 
        #         subject="Test Draft", 
        #         body=request.message
        #     )
        #     reply_message = "Draft simulated successfully."

        # print("Returning ChatResponse:", reply_message)


        # 3. Assemble and return the structured response
        return ChatResponse(
            reply=reply_message,
            entities=entities
        )
        
    except Exception as e:
        # Generic error handling
        raise HTTPException(status_code=500, detail=str(e))