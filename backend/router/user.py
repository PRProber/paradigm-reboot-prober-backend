from fastapi import APIRouter, File, Form, UploadFile, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..model import schemas, entities
from ..util.database import get_db
from ..service import user as user_service

router = APIRouter()


@router.post('/user/register', response_model=schemas.User)
async def register(user: schemas.UserCreate,
                   db: Session = Depends(get_db)):
    user = user_service.create_user(db, user)
    return user


@router.post('/user/login', response_model=schemas.Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(),
                db: Session = Depends(get_db)):
    token = user_service.login(db, form_data.username, form_data.password)
    if token is None:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    return schemas.Token(access_token=token, token_type="bearer")


@router.get('/user/me', response_model=schemas.User)
async def get_my_info(user: entities.User = Depends(user_service.get_current_user)):
    return user


@router.get('/user/records')
async def get_play_records(username: str | None = None, export: str | None = None,
                           user: entities.User = Depends(user_service.get_current_user)):
    # TODO: Invoke user service
    play_records: list[schemas.PlayRecord] = []

    return play_records


@router.post('/user/records/batch')
async def import_records(username: str = Form(), file: UploadFile = File()):
    # TODO: Analyze .csv file and invoke user service to *replace* records
    response_msg = None

    return response_msg


@router.post('/user/records')
async def post_record(record: schemas.PlayRecordCreate):
    # TODO: Invoke user service
    response_msg = None

    return response_msg
