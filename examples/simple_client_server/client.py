"""A client module that imports backend endpoint definitions and uses them for client-side usage."""

from examples.simple_client_server.server import (
    ItemData,
    get_item,
    greeting_message,
    post_endpoint,
)
from http_clientlib import set_default_configuration, wrap_backend_call
from http_clientlib.http import make_http_request

set_default_configuration(
    base_url="http://localhost:8080", http_request_function=make_http_request
)


# Example usage: Simple GET request without parameters
greeting_message_http = wrap_backend_call(greeting_message)
response = greeting_message_http()
print(response)

# Example usage: GET request with path and query parameters
get_item_http = wrap_backend_call(get_item)
response = get_item_http(item_id=42, query="test")
print(response)

# Example usage: POST request with request body
create_item_http = wrap_backend_call(post_endpoint)
response = create_item_http(data=ItemData(id=1, name="A Box"))

# Example usage: POST request using a dictionary for the request body directly
# response = create_item_http(data={"id": 1, "name": "Sample Item"})
print(response)
