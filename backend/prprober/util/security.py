from typing import Optional, Union
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import JWTError, jwt

from backend import config

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='user/login')
optional_oauth2_scheme = OAuth2PasswordBearer(tokenUrl='user/login', auto_error=False)
pwd_context = CryptContext(schemes=['bcrypt'])

bad_credential_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def verify_password(plain_password: str, encoded_password: str):
    return pwd_context.verify(plain_password, encoded_password)


def encode_password(password: str | bytes):
    return pwd_context.hash(password)


def generate_jwt(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.SECRETE_KEY, algorithm=config.JWT_ENCODE_ALGORITHM)
    return encoded_jwt


def generate_access_jwt(username: str, expires_delta: Union[timedelta, None] = None):
    """
    Invoked by service.login().
    :param username:
    :param expires_delta:
    :return:
    """
    return generate_jwt(data={"sub": username}, expires_delta=expires_delta)


def extract_payloads(token: str):
    payload = jwt.decode(token, config.SECRETE_KEY, algorithms=[config.JWT_ENCODE_ALGORITHM])
    return payload


def extract_username(token: str) -> str | None:
    """
    Extract username from a JWT.
    :param token: JWT.
    :return: username: extracted username.
    """
    try:
        payload = extract_payloads(token)
    except Exception as e:
        return None
    return payload.get("sub")
