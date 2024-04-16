from fastapi_cache.decorator import cache
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..model import schemas
from ..model.schemas import UserInDB
from ..util.database import get_db
from ..service import user as user_service

router = APIRouter()


@router.post('/user/register', response_model=schemas.User)
async def register(user: schemas.UserCreate,
                   db: Session = Depends(get_db)):
    # TODO: 过滤同 IP 重复的成功注册
    user = user_service.create_user(db, user)
    return user


@router.post('/user/login', response_model=schemas.Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(),
                db: Session = Depends(get_db)):
    # TODO: 屏蔽同 IP 重复的接口访问
    token = user_service.login(db, form_data.username, form_data.password)
    if token is None:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    return schemas.Token(access_token=token, token_type="bearer")


@router.get('/user/me', response_model=schemas.User)
@cache(expire=60)
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
