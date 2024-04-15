# TODO: Use hierarchical toml file to store configs
from datetime import timedelta


DATABASE_URL = 'sqlite:///resources/sql.db'

# Security Settings
SECRETE_KEY = 'edf16f010d14b78f86cf432884d8a2123b3b272d3ec9a96d4669a98732efb34e'
JWT_ENCODE_ALGORITHM = 'HS256'
TOKEN_EXPIRE_MINUTES = timedelta(minutes=1800)
