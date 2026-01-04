"""
FastAPI server with introspectable endpoint metadata.

This module explores using Annotated return types to attach route information
to endpoint functions. This allows API clients to introspect server functions
directly (via typing.get_type_hints) and automatically generate HTTP calls.
"""

import logging
from typing import Annotated

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


@app.get("/")
def greeting_message() -> Annotated[dict, "GET /"]:
    """A simple GET endpoint that takes no parameters and returns a greeting message"""
    return {"message": "Hello, World!"}


@app.get("/items/{item_id}")
def get_item(item_id: int, page: int = 0) -> Annotated[dict, "GET /items/{item_id}"]:
    """A GET endpoint with both path and query parameters."""
    return {"item_id": item_id}


class ItemData(BaseModel):
    id: int
    name: str


@app.post("/items")
def post_endpoint(data: ItemData) -> Annotated[dict, "POST /items"]:
    """A POST endpoint that accepts a Pydantic model as the request body."""
    return {"message": f"Item {data} created"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
