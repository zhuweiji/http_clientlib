"""
A more realistic backend API server with user management endpoints.

Demonstrates:
- Authentication with tokens
- CRUD operations (Create, Read, Update, Delete)
- Pagination
- Structured error responses
- Input validation with Pydantic models
"""

from typing import Annotated

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

app = FastAPI(title="User Management API")

# In-memory user store (in real app, would be a database)
USERS_DB = {}
NEXT_USER_ID = 1


class User(BaseModel):
    id: int | None = None
    name: str = Field(..., min_length=1, max_length=100)
    email: str
    is_active: bool = True


class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: str


class UserUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    is_active: bool | None = None


class PaginatedResponse(BaseModel):
    items: list[User]
    total: int
    skip: int
    limit: int


class AuthToken(BaseModel):
    access_token: str
    token_type: str


# Mock auth - in real app would validate JWT or similar
VALID_TOKEN = "mock-token-12345"


def verify_token(token: str):
    if token != VALID_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        )


@app.post("/auth/login")
def login(username: str, password: str) -> Annotated[AuthToken, "POST /auth/login"]:
    """Authenticate and receive a bearer token."""
    if username == "admin" and password == "password":
        return AuthToken(access_token=VALID_TOKEN, token_type="bearer")
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
    )


@app.get("/users")
def list_users(
    skip: int = 0, limit: int = 10, token: str | None = None
) -> Annotated[PaginatedResponse, "GET /users"]:
    """List all users with pagination."""
    if token:
        verify_token(token)

    all_users = list(USERS_DB.values())
    total = len(all_users)
    items = all_users[skip : skip + limit]

    return PaginatedResponse(items=items, total=total, skip=skip, limit=limit)


@app.get("/users/{user_id}")
def get_user(
    user_id: int, token: str | None = None
) -> Annotated[User, "GET /users/{user_id}"]:
    """Retrieve a specific user by ID."""
    if token:
        verify_token(token)

    user = USERS_DB.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    return user


@app.post("/users")
def create_user(
    user: UserCreate, token: str | None = None
) -> Annotated[User, "POST /users"]:
    """Create a new user."""
    if token:
        verify_token(token)

    global NEXT_USER_ID
    user_id = NEXT_USER_ID
    NEXT_USER_ID += 1

    new_user = User(id=user_id, name=user.name, email=user.email)
    USERS_DB[user_id] = new_user
    return new_user


@app.put("/users/{user_id}")
def update_user(
    user_id: int, user_update: UserUpdate, token: str | None = None
) -> Annotated[User, "PUT /users/{user_id}"]:
    """Update an existing user."""
    if token:
        verify_token(token)

    user = USERS_DB.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")

    if user_update.name is not None:
        user.name = user_update.name
    if user_update.email is not None:
        user.email = user_update.email
    if user_update.is_active is not None:
        user.is_active = user_update.is_active

    return user


@app.delete("/users/{user_id}")
def delete_user(
    user_id: int, token: str | None = None
) -> Annotated[dict, "DELETE /users/{user_id}"]:
    """Delete a user."""
    if token:
        verify_token(token)

    if user_id not in USERS_DB:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")

    del USERS_DB[user_id]
    return {"message": f"User {user_id} deleted"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8081)
