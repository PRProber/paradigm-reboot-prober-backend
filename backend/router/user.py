from typing import List
from fastapi import APIRouter, File, Form, UploadFile, Depends, HTTPException, Query
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from starlette import status

from ..model import schemas, entities
from ..util.database import get_db
from ..service import user as user_service
from ..util.b50 import json2img, json2csv, csv2json

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


@router.get('/records/{username}', response_model=schemas.PlayRecordResponse)
async def get_play_records(username: str,
                           export_type: str | None = Query(default=None, alias='export-type'),
                           best: bool = True, underflow: int = 0,
                           page_size: int | None = Query(default=None, alias='page-size'),
                           page_index: int | None = Query(default=None, alias='page-index'),
                           sort_by: str | None = Query(default=None, alias='sort-by'),
                           order: str | None = Query(default=None, alias='order'),
                           current_user: entities.User = Depends(user_service.get_current_user),
                           db: Session = Depends(get_db)):
    user = user_service.get_user(db, username)
    if user is None:
        raise HTTPException(status_code=400, detail="User not found")
    if user.anonymous_probe is False and user != current_user:
        raise HTTPException(status_code=400, detail="Anonymous probes are not allowed")

    if best is True:
        if underflow <= 15:
            b35, b15 = user_service.get_best_records(db, username, underflow)
        else:
            raise HTTPException(status_code=400, detail="# of underflow records out of range")
    else:
        b35, b15 = user_service.get_all_records(db, username)
    # if export_type == "csv":
    #     return json2csv(play_records)
    # if export_type == "img":
    #     return json2img(play_records)
    return {"b35": b35, "b15": b15}


@router.get('/records/{username}/{song_level_id}')
async def get_single_play_records(username: str, song_level_id: int, scope: str | None = 'month'):
    # TODO: Get play records of a single song
    # scope 意味着获取 record 的周期
    # month/season/year 代表获取过去一个月/三个月/一年的相关单曲记录
    pass


@router.post('/records/{username}', status_code=201, response_model=List[schemas.PlayRecord])
async def post_record(username: str,
                      records: schemas.BatchPlayRecordCreate,
                      use_csv: bool | None = Query(default=False, alias="use-csv"),
                      current_user: entities.User | None = Depends(user_service.get_current_user_or_none),
                      db: Session = Depends(get_db)):
    if not use_csv:
        if current_user and current_user.username == username:
            response_msg = user_service.create_record(db, username, records.play_records)
        elif records.upload_token and records.upload_token == user_service.get_user(db, username).upload_token:
            response_msg = user_service.create_record(db, username, records.play_records)
        else:
            raise HTTPException(status_code=401, detail="Unauthorized")
    else:
        # TODO: upload a .csv file
        response_msg = user_service.create_record(db, username, csv2json(username))
    user_service.update_b50_record(db, username)
    return response_msg


@router.get('/statistics/{username}')
async def get_b50_trends(username: str, db: Session = Depends(get_db)):
    trends = user_service.get_b50_trends(db, username)
    return trends
