import json

from fastapi import Response, Request
from fastapi_cache import Coder, JsonCoder

from ..model.schemas import UserInDB


def best50image_key_builder(func,
                            namespace: str = "",
                            *,
                            request: Request = None,
                            response: Response = None,
                            **kwargs
                            ):
    return ':'.join([namespace, request.method.lower(), request.url.path])


class PNGImageResponseCoder(Coder):
    @classmethod
    def encode(cls, value: Response) -> bytes:
        return value.body

    @classmethod
    def decode(cls, value: bytes) -> Response:
        return Response(content=value, media_type='image/png')


class UserInDBCoder(JsonCoder):
    @classmethod
    def decode(cls, value: str) -> UserInDB:
        return UserInDB.model_validate(json.loads(value))
