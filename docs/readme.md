# HTTP Client Library Documentation

## Table of Contents

- [Quick Start](#quick-start)
- [Installation](#installation)
- [Core Concepts](#core-concepts)
- [Configuration](#configuration)
- [API Reference](#api-reference)
  - [Core Functions](#core-functions)
  - [Types](#types)
  - [Configuration Class](#configuration-class)
  - [HTTP Functions](#http-functions)
  - [Parser Functions](#parser-functions)
- [Examples](#examples)
- [Advanced Usage](#advanced-usage)
- [Best Practices](#best-practices)

## Quick Start

Here's how to get started with the HTTP Client Library in just a few steps:

### 1. Install the library

```bash
pip install http_clientlib
```

### 2. Import your server endpoints

```python
from my_backend.server import (
    get_user,
    create_user,
    UserCreate  # Pydantic model
)
```

### 3. Configure the client

```python
from http_clientlib import set_default_configuration, wrap_backend_call
from http_clientlib.http import perform_http_call

set_default_configuration(
    base_url="http://localhost:8000",
    http_call_func=perform_http_call # Use HTTP method we provide
)
```

### 4. Wrap and call your endpoints

```python
# Wrap the backend function
get_user_http = wrap_backend_call(get_user)
create_user_http = wrap_backend_call(create_user)

# Make type-safe HTTP calls
response = get_user_http(user_id=123)
user = response.json()

# Create a user with Pydantic model
new_user = UserCreate(name="John Doe", email="john@example.com")
response = create_user_http(user=new_user)
created_user = response.json()
```

## Installation

### Via pip

```bash
pip install http_clientlib
```

### Via uv

```bash
uv add http_clientlib
```

### From source

```bash
git clone https://github.com/yourusername/http-clientlib.git
cd http-clientlib
pip install -e .
```

## Core Concepts

### How It Works

1. **Function Introspection**: The library analyzes your FastAPI/Flask endpoint functions to extract:
   - HTTP method and route path
   - Path parameters (e.g., `/users/{user_id}`)
   - Query parameters
   - Request body parameters (Pydantic models)

2. **Automatic Request Generation**: When you call a wrapped function, the library:
   - Separates arguments into path, query, and body parameters
   - Serializes Pydantic models to JSON
   - Constructs the full HTTP request metadata

3. **Configurable HTTP Execution**: The actual HTTP call is delegated to a configurable function, allowing you to:
   - Use the built-in `httpx`-based implementation
   - Provide custom implementations with retry logic, caching, logging, etc.

### Key Benefits

- **Type Safety**: Full type information from server functions is preserved in the client
- **IDE Support**: Auto-completion, type checking, and inline documentation
- **No Code Generation**: Changes to server signatures are immediately reflected
- **Transparency**: HTTP details are not hidden - you work with standard HTTP responses
- **Flexibility**: Plug in your own HTTP implementation with custom logic

## Configuration

### Basic Configuration

The `Configuration` class controls how HTTP calls are made:

```python
from http_clientlib.configuration import Configuration
from http_clientlib.http import perform_http_call

config = Configuration(
    base_url="http://localhost:8000",  # Your backend URL
    http_call_func=perform_http_call   # Function to execute HTTP requests
)
```

### Global vs Local Configuration

#### Global Configuration (Recommended for most cases)

```python
from http_clientlib import set_default_configuration

# Set once for all wrapped functions
set_default_configuration(config)

# All wrapped functions will use this config
wrapped_func = wrap_backend_call(my_endpoint)
```

#### Local Configuration

```python
# Pass configuration to specific wrapper
wrapped_func = wrap_backend_call(my_endpoint, configuration=config)
```

### Custom HTTP Implementation

You can provide your own HTTP implementation:

```python
import requests
from http_clientlib.types import HTTPRequestMetadata

def custom_http_call(request: HTTPRequestMetadata):
    """Custom HTTP implementation with retry logic."""
    import time
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.request(
                method=request.method,
                url=request.url,
                params=request.query_values,
                json=request.body
            )
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
                continue
            raise

# Use custom implementation
config = Configuration(
    base_url="http://api.example.com",
    http_call_func=custom_http_call
)
```

## API Reference

### Core Functions

#### `wrap_backend_call(func, configuration=None)`

Wraps a FastAPI/Flask endpoint function to make HTTP calls.

**Parameters:**
- `func` (Callable): The backend function to wrap
- `configuration` (Configuration, optional): Configuration to use. If None, uses global default

**Returns:**
- Callable that makes HTTP requests and returns HTTPResponse

**Example:**
```python
from my_backend import get_user

get_user_http = wrap_backend_call(get_user)
response = get_user_http(user_id=123)
```

---

#### `set_default_configuration(configuration)`

Sets the global default configuration for all wrapped functions.

**Parameters:**
- `configuration` (Configuration): The configuration to set as default

**Example:**
```python
config = Configuration(base_url="http://localhost:8000")
set_default_configuration(config)
```

---

#### `http_client_decorator(configuration=None)`

Creates a decorator for wrapping multiple functions.

**Parameters:**
- `configuration` (Configuration, optional): Configuration to use

**Returns:**
- Decorator function

**Example:**
```python
@http_client_decorator(config)
def my_endpoint(user_id: int) -> Annotated[User, "GET /users/{user_id}"]:
    pass
```

### Types

#### `HTTPRequestMetadata`

Represents a complete HTTP request with all typed information.

**Attributes:**
- `base_url` (str): Base URL of the API
- `method` (str): HTTP method (GET, POST, etc.)
- `path` (str): URL path template (e.g., `/users/{user_id}`)
- `path_values` (dict): Values for path parameters
- `query_values` (dict): Query parameter values
- `body` (dict, optional): Serialized request body

**Properties:**
- `full_path`: Path with substituted parameters
- `url`: Complete URL for the request

**Example:**
```python
request = HTTPRequestMetadata(
    base_url="http://api.example.com",
    method="GET",
    path="/users/{user_id}",
    path_values={"user_id": 123},
    query_values={"include_details": True},
    body=None
)
print(request.url)  # http://api.example.com/users/123
```

---

#### `HTTPResponse` (Protocol)

A library-agnostic protocol for HTTP responses. Compatible with both `requests.Response` and `httpx.Response`.

**Attributes:**
- `status_code` (int): HTTP status code
- `headers` (Dict[str, str]): Response headers
- `encoding` (str): Response encoding
- `url` (Any): Request URL

**Methods:**
- `json()`: Parse response as JSON
- `text`: Get response as text
- `content`: Get raw bytes
- `raise_for_status()`: Raise exception for error status codes

**Example:**
```python
response = wrapped_func()
if response.status_code == 200:
    data = response.json()
else:
    response.raise_for_status()
```

### Configuration Class

#### `Configuration`

Holds configuration for HTTP client behavior.

**Attributes:**
- `base_url` (str): Base URL for API calls (default: "http://localhost:8000")
- `http_call_func` (Callable): Function to execute HTTP requests

**Example:**
```python
config = Configuration(
    base_url="https://api.production.com",
    http_call_func=perform_http_call
)
```

### HTTP Functions

#### `perform_http_call(http_request)`

Built-in HTTP implementation using `httpx`.

**Parameters:**
- `http_request` (HTTPRequestMetadata): Request metadata

**Returns:**
- `httpx.Response`: HTTP response

**Example:**
```python
from http_clientlib.http import perform_http_call

response = perform_http_call(request_metadata)
```

---

#### `mock_http_call(http_request)`

Mock implementation for testing that prints request details.

**Parameters:**
- `http_request` (HTTPRequestMetadata): Request metadata

**Example:**
```python
from http_clientlib.http import mock_http_call

# Use for debugging
config = Configuration(http_call_func=mock_http_call)
```

### Parser Functions

#### `extract_route_info(func)`

Extracts route information from function's return type annotation.

**Parameters:**
- `func` (Callable): Function with annotated return type

**Returns:**
- str: Route info (e.g., "GET /users/{user_id}")

---

#### `parse_route_info(route_info)`

Parses route info into HTTP method and path.

**Parameters:**
- `route_info` (str): Route string

**Returns:**
- tuple[str, str]: (method, path)

---

#### `extract_path_params(route_info)`

Extracts path parameter names from route.

**Parameters:**
- `route_info` (str): Route string with path parameters

**Returns:**
- set[str]: Parameter names

---

#### `extract_param_types(func, path_params)`

Distinguishes between query and body parameters.

**Parameters:**
- `func` (Callable): Function to analyze
- `path_params` (set[str]): Known path parameters

**Returns:**
- tuple[set[str], set[str]]: (query_params, body_params)

---

#### `serialize_body(body_params, body_param_names)`

Serializes Pydantic models to JSON-compatible dict.

**Parameters:**
- `body_params` (dict): Parameter values
- `body_param_names` (set[str]): Names of body parameters

**Returns:**
- dict or None: Serialized body

## Examples

### Simple GET Request

```python
from my_backend import greeting_message
from http_clientlib import wrap_backend_call

# Backend function signature:
# def greeting_message() -> Annotated[str, "GET /greeting"]:

greeting_http = wrap_backend_call(greeting_message)
response = greeting_http()
print(response.json())  # "Hello, World!"
```

### GET with Path and Query Parameters

```python
from my_backend import get_item

# Backend function signature:
# def get_item(item_id: int, include_details: bool = False) -> Annotated[Item, "GET /items/{item_id}"]:

get_item_http = wrap_backend_call(get_item)
response = get_item_http(item_id=42, include_details=True)
item = response.json()
```

### POST with Pydantic Model

```python
from my_backend import create_user, UserCreate

# Backend function signature:
# def create_user(user: UserCreate) -> Annotated[User, "POST /users"]:

create_user_http = wrap_backend_call(create_user)

# Using Pydantic model
new_user = UserCreate(name="Alice", email="alice@example.com", age=30)
response = create_user_http(user=new_user)

# Or using dict directly
response = create_user_http(user={"name": "Bob", "email": "bob@example.com"})
```

### Complete Client Service Example

```python
from http_clientlib import set_default_configuration, wrap_backend_call
from http_clientlib.configuration import Configuration
from http_clientlib.http import perform_http_call
from my_backend.api import login, get_user, create_user, UserCreate

class APIClient:
    def __init__(self, base_url: str):
        config = Configuration(
            base_url=base_url,
            http_call_func=perform_http_call
        )
        set_default_configuration(config)
        
        # Wrap all endpoints
        self.login_http = wrap_backend_call(login)
        self.get_user_http = wrap_backend_call(get_user)
        self.create_user_http = wrap_backend_call(create_user)
        
        self.token = None
    
    def authenticate(self, username: str, password: str) -> bool:
        """Login and store authentication token."""
        response = self.login_http(username=username, password=password)
        if response.status_code == 200:
            self.token = response.json()["access_token"]
            return True
        return False
    
    def get_user(self, user_id: int):
        """Fetch user with authentication."""
        response = self.get_user_http(user_id=user_id, token=self.token)
        response.raise_for_status()
        return response.json()
    
    def create_user(self, name: str, email: str):
        """Create new user."""
        user_data = UserCreate(name=name, email=email)
        response = self.create_user_http(user=user_data, token=self.token)
        response.raise_for_status()
        return response.json()

# Usage
client = APIClient("http://api.example.com")
if client.authenticate("admin", "secret"):
    user = client.get_user(123)
    new_user = client.create_user("Jane Doe", "jane@example.com")
```


## Troubleshooting

### Common Issues

**1. "No configuration provided" Error**

```python
# Problem: Calling wrap_backend_call without setting configuration
wrapped = wrap_backend_call(my_func)  # Error!

# Solution: Set default configuration first
set_default_configuration(Configuration(base_url="http://localhost:8000"))
wrapped = wrap_backend_call(my_func)  
```

**2. Missing Type Annotations**

```python
# Problem: Backend function missing return annotation
def get_user(user_id: int):  # No route info!
    pass

# Solution: Add proper annotation
def get_user(user_id: int) -> Annotated[User, "GET /users/{user_id}"]:
    pass
```

**3. Pydantic Model Serialization Issues**

```python
# Problem: Passing dict when Pydantic model expected
response = create_user_http(user={"name": "John"})  # Type Warning

# Solution: Use the Pydantic model
user_data = UserCreate(name="John", email="john@example.com")
response = create_user_http(user=user_data)
```

## Migration Guide

### From Manual HTTP Calls

Before:
```python
import requests

def get_user(user_id: int):
    response = requests.get(f"http://api.example.com/users/{user_id}")
    response.raise_for_status()
    return response.json()
```

After:
```python
from backend import get_user as get_user_backend
from http_clientlib import wrap_backend_call

get_user = wrap_backend_call(get_user_backend)
# Now you have type safety and IDE support!
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.