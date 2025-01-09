import traceback
from copy import deepcopy

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

import src.models as models
from src.llm import handle_user_chat
from src.utils import DirectReturnException, create_logger

logger = create_logger(logger_name="main", log_file="api.log", log_level="info")

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

# Create a route to serve the HTML file
@app.get("/ui", response_class=HTMLResponse)
async def read_html(request: Request):
    with open("static/index.html", "r") as file:
        html_content = file.read()
    return HTMLResponse(content=html_content, status_code=200)

origins = [
    "*"
]


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
    """
    logger.info("Root endpoint accessed")
    return {"message": "Hello World"}


@app.post("/chat")
async def create_chat(thread: models.Thread) -> models.Thread:
    """
    Process chat thread in a conversation.

    The chat conversation consists of alternating messages with roles that start
    with a 'user' role followed by an 'assistant' role, and is enforced through validation.

    Args:
        thread (Thread): An object containing a list of messages in the chat.
                         Each message must have a role of either 'user' or 'assistant'
                         and must follow an alternating role sequence starting with 'user'.

    Returns:
        Thread: The updated thread with the assistant's response appended.

    Raises:
        HTTPException: If an error occurs during chat processing, an HTTP 500 error is raised
                       with details about the failure.
    """
    logger.info("Chat endpoint accessed with thread: %s", thread)
    response = deepcopy(thread)
    try:
        # Call the function to handle chat interaction
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

# Log that the app is starting
logger.info("Starting the application")