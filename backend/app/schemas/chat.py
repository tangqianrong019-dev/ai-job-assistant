from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str


class InterviewSession(BaseModel):
    session_id: str
    messages: list[ChatMessage]
    topic: str
