from typing import Any
import json

from fastapi_cache import Coder, JsonCoder

from ..model.schemas import UserInDB


class PassthroughCoder(Coder):
    @classmethod
    def encode(cls, value: Any) -> Any:
        return value

    @classmethod
    def decode(cls, value: Any) -> Any:
        return value


class UserInDBCoder(JsonCoder):
    @classmethod
    def decode(cls, value: str) -> UserInDB:
        return UserInDB.model_validate(json.loads(value))