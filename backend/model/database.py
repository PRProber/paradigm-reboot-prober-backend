from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .. import config

DATABASE_URL = config.DATABASE_URL
engine = create_engine(DATABASE_URL,
                       connect_args={"check_same_thread": False})

# 数据库会话
SessionLocal = sessionmaker(engine)
# ORM Base
Base = declarative_base()
