import traceback

from fastapi import FastAPI, HTTPException
from copy import deepcopy

from src.llm import handle_user_chat
from src.utils import create_logger, DirectReturnException
import src.models as models
logger = create_logger(logger_name="main", log_file="api.log", log_level="info")

app = FastAPI()





@app.get("/")
async def root() -> dict:
    """
    Root endpoint that returns a welcome message.

    Returns:
        dict: A dictionary containing a welcome message.
    """
    return {"message": "Hello World"}

@app.post("/chat")
async def create_chat(thread: models.Thread) -> models.Thread:
    """
    Process chat thread in a conversation.

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
    response = deepcopy(thread)
    try:
        # Call the function to handle chat interaction
        assistant_response = handle_user_chat(thread=thread)
        response.messages.append(assistant_response)
        return response
    except DirectReturnException as direct_return_response:
        response.messages.append(direct_return_response.message)
        return response
    except Exception:
        # Log the traceback and raise an HTTP exception if an error occurs
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500, detail=f"Error generating response for chat: {str(thread)}"
        )
