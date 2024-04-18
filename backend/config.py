# TODO: Use hierarchical toml file to store configs
from datetime import timedelta
import os

DATABASE_URL = os.environ.get('PRP_DATABASE_URL')

# Security Settings
SECRETE_KEY = os.environ.get('PRP_SECRETE_KEY')
JWT_ENCODE_ALGORITHM = 'HS256'
TOKEN_EXPIRE_MINUTES = timedelta(minutes=1800)

UPLOAD_CSV_PATH = 'temp/upload/b50csv/'
UPLOAD_COVER_PATH = 'temp/upload/cover/'
RESOURCE_COVER_PATH = 'resources/image/cover/'
RESOURCE_COVER_STATIC_PATH = 'resources/static/cover/'

CHARACTERS = {
    "Para_Summer": 'resources/image/character/para_summer.png',
    "Para_Young_Awaken": 'resources/image/character/para_young_awaken.png',
    "Yun_Summer": 'resources/image/character/yun_summer.png',
    "Eden": 'resources/image/character/eden.png',
    "Geopelia": 'resources/image/character/geopelia.png'
}
