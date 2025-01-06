import uuid
from typing import Literal

from pydantic import BaseModel, validator


class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class Thread(BaseModel):
    id: str | None = str(uuid.uuid4())
    messages: list[Message]
    user_id: str | None = None

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
