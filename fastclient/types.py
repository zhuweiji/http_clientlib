from dataclasses import dataclass
from typing import Optional


@dataclass
class HTTPRequestMetadata:
    """Represents a complete HTTP request with all typed information."""

    base_url: str
    method: str  # e.g., "GET", "POST"
    path: str  # e.g., "/items/{item_id}"
    path_values: dict  # {"item_id": 123}
    query_values: dict  # {"skip": 0, "limit": 10}
    body: Optional[dict] = None  # Serialized request body

    @property
    def full_path(self) -> str:
        """Reconstruct full path with parameter substitution."""
        path = self.path
        for key, value in self.path_values.items():
            path = path.replace(f"{{{key}}}", str(value))
        return path

    def __str__(self) -> str:
        return (
            f"GeneratableHTTPRequest(method={self.method}, "
            f"path={self.full_path}, "
            f"query_values={self.query_values}, "
            f"body={self.body})"
        )

    @property
    def url(self) -> str:
        """Construct the full URL for the request."""
        return f"{self.base_url}{self.full_path}"
