"""
A mature user management service client.

Demonstrates usage of fastclient to build a client library for a backend API that includes:
- Authentication and token management
- Error handling
- Pagination
- Type-safe HTTP calls using fastclient
"""

import httpx

from examples.user_service.server import (
    UserCreate,
    UserUpdate,
    create_user,
    delete_user,
    get_user,
    list_users,
    login,
    update_user,
)
from http_clientlib.api import set_default_configuration, wrap_backend_call
from http_clientlib.configuration import Configuration
from http_clientlib.http import make_http_request
from http_clientlib.types import HTTPResponse


class UserServiceClient:
    """
    A client service for interacting with the user management backend.

    This demonstrates how fastclient makes it easy to wrap backend endpoints
    and build a type-safe service layer without manual HTTP handling.
    """

    def __init__(self, base_url: str = "http://localhost:8081"):
        """Initialize the client with a base URL."""
        config = Configuration(
            base_url=base_url, http_request_function=make_http_request
        )
        set_default_configuration(config)

        # Wrap backend endpoints with HTTP call behavior
        self.login_http = wrap_backend_call(login)
        self.list_users_http = wrap_backend_call(list_users)
        self.get_user_http = wrap_backend_call(get_user)
        self.create_user_http = wrap_backend_call(create_user)
        self.update_user_http = wrap_backend_call(update_user)
        self.delete_user_http = wrap_backend_call(delete_user)

        self.token: str | None = None

    def handle_response(self, response: HTTPResponse):
        """Handle HTTP response, raising exceptions for error status codes."""
        try:
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.RequestError as e:
            print(f"Request error occurred: {e}")
            raise

    def authenticate(self, username: str, password: str) -> bool:
        """
        Authenticate with the backend and store the access token.

        Returns True if authentication was successful, False otherwise.
        """
        try:
            response = self.login_http(username=username, password=password)
            result = self.handle_response(response)
            if "access_token" not in result:
                raise ValueError("Authentication response missing access_token")
            self.token = result["access_token"]
            print(f"Authenticated successfully. Token: {self.token}")
            return True

        except Exception as e:
            print(f"Authentication failed: {e}")
            return False

    def get_users(self, skip: int = 0, limit: int = 10):
        """
        Fetch a paginated list of users.

        Args:
            skip: Number of users to skip (for pagination)
            limit: Maximum number of users to return

        Returns:
            PaginatedResponse with users and pagination info, or None if failed.
        """
        try:
            response = self.list_users_http(skip=skip, limit=limit, token=self.token)
            result = self.handle_response(response)
            if "items" not in result or "total" not in result:
                raise ValueError("List users response missing required fields")
            print(f"Fetched {len(result['items'])} users (total: {result['total']})")
            return result

        except Exception as e:
            print(f"Failed to fetch users: {e}")
            return None

    def get_user_by_id(self, user_id: int):
        """
        Fetch a specific user by ID.

        Args:
            user_id: The ID of the user to retrieve

        Returns:
            User object, or None if not found or request failed.
        """
        try:
            response = self.get_user_http(user_id=user_id, token=self.token)
            result = self.handle_response(response)
            print(f"✓ Fetched user: {result['name']} ({result['email']})")
            return result

        except Exception as e:
            print(f"✗ Failed to fetch user {user_id}: {e}")
            return None

    def create_new_user(self, name: str, email: str):
        """
        Create a new user.

        Args:
            name: User's full name
            email: User's email address

        Returns:
            Created User object, or None if request failed.
        """
        try:
            user_data = UserCreate(name=name, email=email)
            response = self.create_user_http(user=user_data, token=self.token)
            result = self.handle_response(response)
            if "id" not in result:
                raise ValueError("Create user response missing user ID")
            if "name" not in result:
                raise ValueError("Create user response missing user name")

            print(f"Created user: {result['name']} (ID: {result['id']})")
            return result
        except Exception as e:
            print(f"Failed to create user: {e}")
            return None

    def update_user_info(self, user_id: int, **kwargs):
        """
        Update a user's information.

        Args:
            user_id: The ID of the user to update
            **kwargs: Fields to update (name, email, is_active)

        Returns:
            Updated User object, or None if request failed.
        """
        try:
            user_update = UserUpdate(**kwargs)
            response = self.update_user_http(
                user_id=user_id, user_update=user_update, token=self.token
            )
            result = self.handle_response(response)
            print(f"✓ Updated user {user_id}")
            return result
        except Exception as e:
            print(f"✗ Failed to update user {user_id}: {e}")
            return None

    def delete_user(self, user_id: int) -> bool:
        """
        Delete a user.

        Args:
            user_id: The ID of the user to delete

        Returns:
            True if deletion was successful, False otherwise.
        """
        try:
            response = self.delete_user_http(user_id=user_id, token=self.token)
            result = self.handle_response(response)
            print(result)
            print(f"Deleted user {user_id}")
            return True
        except Exception as e:
            print(f"Failed to delete user {user_id}: {e}")
            return False


# Example usage
if __name__ == "__main__":
    print("=" * 60)
    print("User Management Service Client - Demonstration")
    print("=" * 60)

    client = UserServiceClient(base_url="http://localhost:8081")

    # 1. Authenticate
    print("\n[1] Authenticating...")
    if not client.authenticate("admin", "password"):
        print("Cannot continue without authentication")
        exit(1)

    # 2. Create a few users
    print("\n[2] Creating users...")
    alice = client.create_new_user("Alice Johnson", "alice@example.com")
    bob = client.create_new_user("Bob Smith", "bob@example.com")
    charlie = client.create_new_user("Charlie Brown", "charlie@example.com")

    # 3. List users with pagination
    print("\n[3] Listing all users (first page, limit 2)...")
    users_page = client.get_users(skip=0, limit=2)

    if users_page:
        for user in users_page["items"]:
            print(f"  - {user['name']} ({user['email']}) - Active: {user['is_active']}")

    # 4. Get a specific user
    print("\n[4] Getting specific user (ID: 1)...")
    user = client.get_user_by_id(1)
    if user:
        print(f"  Details: {user['name']} - {user['email']}")

    # 5. Update a user
    print("\n[5] Updating user (ID: 2)...")
    updated = client.update_user_info(2, name="Robert Smith", is_active=True)
    if updated:
        print(f"  Updated to: {updated['name']} - Active: {updated['is_active']}")

    # 6. Delete a user
    print("\n[6] Deleting user (ID: 3)...")
    client.delete_user(3)

    # 7. List users again to show deletion
    print("\n[7] Listing users again (after deletion)...")
    users_page = client.get_users(skip=0, limit=10)
    if users_page:
        print(f"  Total users: {users_page['total']}")
        for user in users_page["items"]:
            print(f"  - {user['name']} ({user['email']})")

    print("\n" + "=" * 60)
    print("Demonstration complete!")
    print("=" * 60)
