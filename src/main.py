import traceback
from copy import deepcopy
import os

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

import src.models as models
from src.llm import handle_user_chat
from src.utils import DirectReturnException, create_logger

logger = create_logger(logger_name="main", log_file="api.log", log_level="info")

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# CORS settings to allow all origins
origins = ["*"]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=[
        "Content-Type",
        "Authorization",
        "X-Auth-Token",
        "X-User-Identifier",
    ],
)

@app.get("/")
async def root() -> dict:
    """
    Root endpoint that returns a welcome message.

    Returns:
        dict: A dictionary containing a welcome message.
        dict: Dictionary containing a welcome message.
    """
    logger.info("Root endpoint accessed")
    return {"message": "Hello World"}

@app.post("/chat")
async def create_chat(thread: models.Thread) -> models.Thread:
    """
    Handle chat interactions by processing the conversation thread.

    The conversation should consist of messages alternating between 'user' and 'assistant' roles, starting with 'user'.

    Args:
        thread (Thread): An object containing a list of messages in the chat.
                         Each message must have a role of either 'user' or 'assistant'
                         and must follow an alternating role sequence starting with 'user'.

    Returns:
        Thread: The updated thread with the assistant's response appended.

    Raises:
        HTTPException: Raised if an error occurs during chat processing.
    """
    logger.info("Chat endpoint accessed with thread: %s", thread)
    response = deepcopy(thread)
    try:
        # Process chat interaction
        assistant_response = handle_user_chat(thread=thread)
        response.messages.append(assistant_response)
        logger.info("Assistant response generated: %s", assistant_response)
        return response
    except DirectReturnException as direct_return_response:
        response.messages.append(direct_return_response.message)
        logger.info("Direct return response appended: %s", direct_return_response.message)
        return response
    except Exception:
        # Log the traceback and raise an HTTP exception if an error occurs
        logger.error("Error processing chat: %s", traceback.format_exc())
        raise HTTPException(
            status_code=500, detail=f"Error generating response for chat: {str(thread)}"
        )
        raise HTTPException(status_code=500, detail=f"Error generating response for chat: {str(thread)}")

@app.get("/chat-ui", response_class=HTMLResponse)
async def chat_ui(request: Request) -> HTMLResponse:
    """
    Render the chat UI in HTML format, passing the API URL.

    Args:
        request (Request): The request object.

    Returns:
        HTMLResponse:  Rendered HTML template.
    """
    api_url = os.environ.get("API_URL", "/chat")  # Default to /chat if not set
    return templates.TemplateResponse("chat.html", {"request": request, "api_url": api_url})


@app.post("/chat-ui", response_class=JSONResponse)
async def chat_ui_post(request: Request) -> JSONResponse:
    """
    Handles POST requests from the chat UI, processes the message,
    and returns the updated messages as JSON.  This avoids re-rendering
    the entire page, making the chat more responsive.

    Args:
        request (Request): The request object.

    Returns:
        JSONResponse:  The updated thread, including the assistant's response.
    """
    try:
        form_data = await request.form()
        user_message = form_data.get("message")
        if not user_message:
            raise HTTPException(status_code=400, detail="Message is required")

        thread = models.Thread(
            messages=[models.Message(role="user", content=user_message)]
        )
        response_thread = await create_chat(thread)
        return response_thread # Return the full thread

    except HTTPException as http_exc:
        # Re-raise HTTP exceptions to be handled by FastAPI
        raise http_exc
    except Exception as e:
        logger.error("Error in chat_ui_post: %s", traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


# Log application startup
logger.info("Starting the application")