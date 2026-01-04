from collections.abc import Callable
from dataclasses import dataclass

from fastclient.http import mock_http_call


@dataclass
class Configuration:
    base_url: str = "http://localhost:8000"
    http_call_func: Callable = mock_http_call
