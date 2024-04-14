from typing import Any
from fastapi_cache import Coder

class PassthroughCoder(Coder):
    @classmethod
    def encode(cls, value: Any) -> Any:
        return value

    @classmethod
    def decode(cls, value: Any) -> Any:
        return value