from typing import List

from fastapi import Depends, HTTPException, Response
from fastapi_cache.decorator import cache
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address

from backend.prprober.model import schemas
from backend.prprober.model.schemas import UserInDB
from backend.prprober.router.user import router
from backend.prprober.service import record as record_service
from backend.prprober.service import user as user_service
from backend.prprober.service.user import check_probe_authority
from backend.prprober.util.b50.csv import generate_csv, get_records_from_csv
from backend.prprober.util.b50.img import generate_b50_img, image_to_byte_array
from backend.prprober.util.cache import PNGImageResponseCoder, best50image_key_builder
from backend.prprober.util.database import get_db
import logging

limiter = Limiter(key_func=get_remote_address)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SORT_BY_RECORD = ['rating', 'score', 'record_time']
SORT_BY_LEVEL = ['level', 'fitting_level']
SORT_BY_SONG = ['song_id', 'title', 'version', 'bpm']


@router.get('/records/{username}', response_model=schemas.PlayRecordResponse)
@cache(expire=30)
async def get_play_records(username: str,
                           scope: str = "b50", underflow: int = 0,
                           page_size: int = 50,
                           page_index: int = 1,
                           sort_by: str = "rating",
                           order: str = "desc",
                           current_user: UserInDB = Depends(user_service.get_current_user_or_none),
                           db: Session = Depends(get_db)):
    await check_probe_authority(db, username, current_user)
    if sort_by not in SORT_BY_RECORD + SORT_BY_LEVEL + SORT_BY_SONG:
        raise HTTPException(status_code=400, detail='Invalid sort_by parameter')
    if order != "desc" and order != "asce":
        raise HTTPException(status_code=400, detail='Invalid order parameter')

    sort_type = 0
    if sort_by in SORT_BY_RECORD:
        sort_type = 1
    elif sort_by in SORT_BY_LEVEL:
        sort_type = 2
    elif sort_by in SORT_BY_SONG:
        sort_type = 3

    if scope == "b50":
        records = record_service.get_best50_records(db, username, underflow)
    elif scope == "best":
        records = record_service.get_best_records(db, username, page_size, page_index, (sort_by, sort_type), order)
    elif scope == "all":
        records = record_service.get_all_records(db, username, page_size, page_index, (sort_by, sort_type), order)
    else:
        raise HTTPException(status_code=400, detail='Invalid scope parameter')
    response = {"username": username, "records": records}
    if scope == "best":
        response["total"] = record_service.count_best_records(db, username)
    if scope == "all":
        response["total"] = record_service.count_all_records(db, username)
    return response


@router.get('/records/{username}/export/b50')
@limiter.limit('10/10minutes')
@cache(expire=60,
       coder=PNGImageResponseCoder,
       key_builder=best50image_key_builder)
async def get_b50_img(username: str,
                      current_user: UserInDB = Depends(user_service.get_current_user),
                      db: Session = Depends(get_db)):
    if current_user.username == username:
        records = record_service.get_best50_records(db, username)
        try:
            b50_img = await generate_b50_img(records, current_user.nickname)
            b50_img = image_to_byte_array(b50_img)
            return Response(content=b50_img, media_type="image/png")
        except Exception as e:
            logger.error(f"Error occurs while generating Best 50 image for user {username}: {e}", exc_info=True)
            raise HTTPException(status_code=500,
                                detail=f"Error occurs while generating Best 50 image, please contact admin.")
    else:
        raise HTTPException(status_code=401, detail="Unauthorized")


@router.get('/records/{username}/export/csv')
def export_csv(username: str,
               current_user: UserInDB = Depends(user_service.get_current_user),
               db: Session = Depends(get_db)):
    if current_user.username == username:
        records = record_service.get_all_levels_with_best_scores(db, username)
        b50_csv = generate_csv(records).encode('utf-8-sig')
        return Response(content=b50_csv, media_type="text/csv")
    else:
        raise HTTPException(status_code=401, detail="Unauthorized")


@router.post('/records/{username}', status_code=201, response_model=List[schemas.PlayRecord])
async def post_record(username: str,
                      records: schemas.BatchPlayRecordCreate,
                      current_user: UserInDB = Depends(user_service.get_current_user_or_none),
                      db: Session = Depends(get_db)):
    if (records.play_records is None) == (records.csv_filename is None):
        raise HTTPException(status_code=400, detail='Ambiguous data')
    if records.play_records is not None:
        if current_user and current_user.username == username:
            response_msg = record_service.create_record(db, username, records.play_records, records.is_replace)
        else:
            user = await user_service.get_user(db, username)
            if user is None:
                raise HTTPException(status_code=401, detail="Cannot find user")
            if records.upload_token and records.upload_token == user.upload_token:
                response_msg = record_service.create_record(db, username, records.play_records, records.is_replace)
            else:
                raise HTTPException(status_code=401, detail="Unauthorized")
    else:
        records.play_records = get_records_from_csv(records.csv_filename)
        response_msg = record_service.create_record(db, username, records.play_records, is_replaced=True)
    if records and len(records.play_records) > 0:
        record_service.update_b50_record(db, username)
    return response_msg


@router.get('/statistics/{username}/b50')
@cache(expire=30)
async def get_b50_trends(username: str, scope: str | None = 'month',
                         current_user: UserInDB = Depends(user_service.get_current_user_or_none),
                         db: Session = Depends(get_db)):
    await check_probe_authority(db, username, current_user)
    trends = record_service.get_b50_trends(db, username, scope)
    return trends
