from typing import List, Dict, Any


async def search_inbox(query: str) -> List[dict]:
    """
    Placeholder function to simulate searching an email inbox.
    
    In a real application, this would use OAuth2 and call the 
    Gmail API (e.g., users.messages.list).
    """
    print(f" Simulating SEARCH for: {query}")
    
    # Simulate finding one email if the query is "hello"
    if "hello" in query.lower():
        return
    return


async def draft_email(to: str, subject: str, body: str) -> Dict[str, Any]:
    """
    Placeholder function to simulate drafting an email.
    
    In a real application, this would call the
    Gmail API (e.g., users.drafts.create).
    """
    print(f" Simulating DRAFT to: {to} with subject: {subject}")
    
    return {
        "status": "draft_simulated_successfully",
        "draft_id": "draft_abc_987",
        "to": to,
        "subject": subject,
        "body": body
    }