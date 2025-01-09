import uuid
from typing import Literal

from pydantic import BaseModel, validator


class Message(BaseModel):
    """
    Represents a message within a conversation thread.

    Attributes:
        role (Literal["user", "assistant"]): The role of the message sender.
        content (str): The content of the message.
    """

    role: Literal["user", "assistant"]
    content: str


class Thread(BaseModel):
    """
    Represents a threaded conversation consisting of multiple messages.

    Attributes:
        id (str | None): Unique identifier for the thread. Defaults to a
                         generated UUID if not provided.
        messages (list[Message]): A list of Message objects in the thread.
        user_id (str | None): Optional identifier for the user.
    """

    id: str | None = str(uuid.uuid4())
    messages: list[Message]
    user_id: str | None = None

    @validator("messages")
    def check_alternating_roles(cls, v):
        """
        Validates that the messages in the thread have alternating roles
        starting with a user role.

        Args:
            v (list[Message]): List of messages to validate.

        Raises:
            ValueError: If the list is empty, not starting with a 'user' role,
                        or if the roles do not alternate correctly.

        Returns:
            list[Message]: The validated list of messages.
        """
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
