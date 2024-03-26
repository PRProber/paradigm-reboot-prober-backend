from fastapi import APIRouter, File, Form, UploadFile

from ..model import schemas

router = APIRouter()


@router.get('/v1/api/user/me')
async def get_my_info():
    # TODO: According to authentication info to get info from user service
    my_info: schemas.User = schemas.User()

    return my_info


@router.get('/v1/api/user/records')
async def get_play_records(username: str | None = None, export: str | None = None):
    # TODO: Invoke user service
    play_records: list[schemas.PlayRecord] = []

    return play_records


@router.post('/v1/api/user/records/batch')
async def import_records(username: str = Form(), file: UploadFile = File()):
    # TODO: Analyze .csv file and invoke user service to *replace* records
    response_msg = None

    return response_msg


@router.post('/v1/api/user/records')
async def post_record(record: schemas.PlayRecordCreate):
    # TODO: Invoke user service
    response_msg = None

    return response_msg
