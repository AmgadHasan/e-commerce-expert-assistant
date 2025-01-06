import traceback
from typing import List, Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, validator

from src.llm import handle_user_chat
from src.utils import create_logger, DirectReturnException

logger = create_logger(logger_name="main", log_file="api.log", log_level="info")

app = FastAPI()


class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class Chat(BaseModel):
    messages: List[Message]

    @validator("messages")
    def check_alternating_roles(cls, v):
        if not v:
            raise ValueError("The list of messages cannot be empty.")
        if v[0].role != "user":
            raise ValueError("The first message must have the role 'user'.")
        for i in range(1, len(v)):
            if i % 2 == 1 and v[i].role != "assistant":
                raise ValueError(
                    f"Message at index {i} must have the role 'assistant'."
                )
            if i % 2 == 0 and v[i].role != "user":
                raise ValueError(f"Message at index {i} must have the role 'user'.")
        return v


@app.get("/")
async def root() -> dict:
    """
    Root endpoint that returns a welcome message.

    Returns:
        dict: A dictionary containing a welcome message.
    """
    return {"message": "Hello World"}

@app.post("/chat")
async def create_chat(chat: Chat) -> Message:
    """
    Process chat messages in a conversation.

    The chat conversation consists of alternating messages with roles that start
    with a 'user' role followed by an 'assistant' role, and is enforced through validation.

    Args:
        chat (Chat): An object containing a list of messages in the chat. 
                     Each message must have a role of either 'user' or 'assistant'
                     and must follow an alternating role sequence starting with 'user'.

    Returns:
        Message: The response message generated during chat processing.

    Raises:
        HTTPException: If an error occurs during chat processing, an HTTP 500 error is raised
                       with details about the failure.
    """
    try:
        # Call the function to handle chat interaction
        response = handle_user_chat(messages=chat.messages)
        return Message(**response)
    except DirectReturnException as e:
        return Message(**e.message)
    except Exception:
        # Log the traceback and raise an HTTP exception if an error occurs
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500, detail=f"Error generating response for chat: {str(chat)}"
        )
