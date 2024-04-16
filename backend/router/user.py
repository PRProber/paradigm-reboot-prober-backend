from typing import List

from fastapi_cache.decorator import cache
from fastapi import APIRouter, Depends, HTTPException
from fastapi import File, Form, UploadFile, Query
from fastapi.responses import FileResponse, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..model import schemas, entities
from ..model.schemas import UserInDB
from ..util.database import get_db
from ..service import user as user_service
from ..service.user import check_probe_authority
from ..util.b50 import generate_b50_img, json2csv, csv2json, image_to_byte_array
from ..util.cache import PNGImageResponseCoder, best50image_key_builder

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


@router.get('/records/{username}', response_model=schemas.PlayRecordResponse)
@cache(expire=60)
async def get_play_records(username: str,
                           scope: str = "b50", underflow: int = 0,
                           page_size: int = 50,
                           page_index: int = 1,
                           sort_by: str = "rating",
                           order: str = "desc",
                           current_user: UserInDB = Depends(user_service.get_current_user_or_none),
                           db: Session = Depends(get_db)):
    await check_probe_authority(db, username, current_user)
    if sort_by not in schemas.PlayRecordInfo.model_fields.keys():
        raise HTTPException(status_code=400, detail='Invalid sort_by parameter')
    if order != "desc" and order != "asce":
        raise HTTPException(status_code=400, detail='Invalid order parameter')

    if scope == "b50":
        records = user_service.get_best50_records(db, username, underflow)
    elif scope == "best":
        records = user_service.get_best_records(db, username, page_size, page_index, sort_by, order)
    elif scope == "all":
        records = user_service.get_all_records(db, username, page_size, page_index, sort_by, order)
    else:
        raise HTTPException(status_code=400, detail='Invalid scope parameter')
    # if export_type == "csv":
    #     return json2csv(play_records)
    return {"username": username, "records": records}


@router.get('/records/{username}/export/b50')
@cache(expire=300,
       coder=PNGImageResponseCoder,
       key_builder=best50image_key_builder)
async def get_b50_img(username: str,
                      current_user: UserInDB = Depends(user_service.get_current_user),
                      db: Session = Depends(get_db)):
    if current_user.username == username:
        records = user_service.get_best50_records(db, username)
        try:
            b50_img = await generate_b50_img(records, current_user.nickname)
            b50_img = image_to_byte_array(b50_img)
            return Response(content=b50_img, media_type="image/png")
        except Exception:
            raise HTTPException(status_code=500,
                                detail="Error occurs while generating Best 50 image, please contact admin")
    else:
        raise HTTPException(status_code=401, detail="Unauthorized")


@router.post('/records/{username}', status_code=201, response_model=List[schemas.PlayRecord])
async def post_record(username: str,
                      records: schemas.BatchPlayRecordCreate,
                      use_csv: bool = False,
                      current_user: UserInDB = Depends(user_service.get_current_user_or_none),
                      db: Session = Depends(get_db)):
    if not use_csv:
        if current_user and current_user.username == username:
            response_msg = user_service.create_record(db, username, records.play_records)
        else:
            user = await user_service.get_user(db, username)
            if records.upload_token and records.upload_token == user.upload_token:
                response_msg = user_service.create_record(db, username, records.play_records)
            else:
                raise HTTPException(status_code=401, detail="Unauthorized")
    else:
        # TODO: upload a .csv file
        response_msg = user_service.create_record(db, username, csv2json(username))
    user_service.update_b50_record(db, username)
    return response_msg


@router.get('/statistics/{username}/b50')
@cache(expire=60)
async def get_b50_trends(username: str, scope: str | None = 'month',
                         current_user: UserInDB = Depends(user_service.get_current_user_or_none),
                         db: Session = Depends(get_db)):
    await check_probe_authority(db, username, current_user)
    trends = user_service.get_b50_trends(db, username, scope)
    return trends
