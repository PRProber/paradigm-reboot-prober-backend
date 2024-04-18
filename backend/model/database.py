from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .. import config

DATABASE_URL = config.DATABASE_URL
engine = create_engine(DATABASE_URL)

# 数据库会话
SessionLocal = sessionmaker(engine, future=True)
# ORM Base
Base = declarative_base()
