import secrets

from fastapi import UploadFile, Depends, HTTPException

from backend import config
from backend.model import schemas, entities
from backend.router.user import router
from backend.service import user as user_service


@router.post('/upload/csv', response_model=schemas.UploadFileResponse)
async def upload_csv(csv_file: UploadFile,
                     current_user: entities.User = Depends(user_service.get_current_user_or_none)):
    if current_user is None:
        raise HTTPException(status_code=401, detail='Unauthorized')
    if not csv_file:
        raise HTTPException(status_code=400, detail='No file is provided')
    if csv_file.content_type != 'text/csv':
        raise HTTPException(status_code=400, detail='Upload only CSV files')
    content = await csv_file.read()
    filename = '_'.join([current_user.username, 'b50', str(secrets.token_hex(6))]) + '.csv'

    with open(config.UPLOAD_CSV_PATH + filename, 'wb') as f:
        f.write(content)
        f.close()

    return {'filename': filename}


@router.post('/upload/img', response_model=schemas.UploadFileResponse)
async def upload_img(img_file: UploadFile,
                     current_user: entities.User = Depends(user_service.get_current_user_or_none)):
    if current_user is None:
        raise HTTPException(status_code=401, detail='Unauthorized')
    if current_user.is_admin is False:
        raise HTTPException(status_code=401, detail='You are not admin')
    if not img_file:
        raise HTTPException(status_code=400, detail='No file is provided')
    if img_file.content_type not in ['image/jpg', 'image/jpeg', 'image/png']:
        raise HTTPException(status_code=400, detail='Upload only *.jpg, *.jpeg, *.png files')
    content = await img_file.read()
    filename = img_file.filename

    with open(config.UPLOAD_COVER_PATH + filename, 'wb') as f:
        f.write(content)
        f.close()

    return {'filename': filename}
