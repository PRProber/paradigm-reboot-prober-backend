from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend

from .router import song, user

# from .util import database
# database.init_db()

app = FastAPI(root_path="/api/v1")


@app.on_event("startup")
async def startup():
    FastAPICache.init(InMemoryBackend(), prefix="fastapi-cache")


app.include_router(song.router)
app.include_router(user.router)

