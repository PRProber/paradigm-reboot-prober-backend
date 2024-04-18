from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from .router import song, user, record, upload

from .util import database
database.init_db()

app = FastAPI(root_path="/api/v1")
app.state.limiter = user.limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(song.router)
app.include_router(user.router)
app.include_router(record.router)
app.include_router(upload.router)


@app.on_event("startup")
async def startup():
    FastAPICache.init(InMemoryBackend(), prefix="fastapi-cache")
