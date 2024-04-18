from fastapi_cache.decorator import cache
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from slowapi import Limiter
from slowapi.util import get_remote_address

from backend.model import schemas
from backend.model.schemas import UserInDB
from backend.util.database import get_db
from ..service import user as user_service

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.post('/user/register', response_model=schemas.User)
@limiter.limit("10/10minutes")
async def register(request: Request,
                   user: schemas.UserCreate,
                   db: Session = Depends(get_db)):
    user.username = user.username.lower()
    user = user_service.create_user(db, user)
    return user


@router.post('/user/login', response_model=schemas.Token)
@limiter.limit("10/minute")
async def login(request: Request,
                form_data: OAuth2PasswordRequestForm = Depends(),
                db: Session = Depends(get_db)):
    form_data.username = form_data.username.lower()
    token = user_service.login(db, form_data.username, form_data.password)
    if token is None:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    return schemas.Token(access_token=token, token_type="bearer")


@router.post('/user/me/upload-token', response_model=schemas.UploadToken)
async def login(current_user: UserInDB = Depends(user_service.get_current_user), db: Session = Depends(get_db)):
    token = user_service.refresh_upload_token(db, current_user.username)
    return {'upload_token': token}


@router.get('/user/me', response_model=schemas.User)
async def get_my_info(user: UserInDB = Depends(user_service.get_current_user)):
    return user


@router.patch('/user/me', response_model=schemas.User)
async def update_user(update_info: schemas.UserUpdate,
                      user: UserInDB = Depends(user_service.get_current_user_or_none),
                      db: Session = Depends(get_db)):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    user = user_service.update_user(db, user, update_info)
    return user
