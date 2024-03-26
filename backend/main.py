from fastapi import FastAPI

from .router import song
import backend.util as util

# util.init_db()
app = FastAPI()

app.include_router(song.router)

