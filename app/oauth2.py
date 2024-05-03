import jwt
from datetime import datetime, timedelta
from .schemas import TokenData
from jwt import PyJWTError
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from .database import get_db
from .models import User
from .settings import settings

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.expire_minutes
oauth_schema = OAuth2PasswordBearer(tokenUrl="login")


def create_jwt(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token


def verify_jwt(token: str, exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("user_id")
        # print(user_id)
        if user_id is None:
            raise exception
        token_data = TokenData(id=str(user_id))
    except PyJWTError:
        raise exception
    return token_data


def get_current_user(token: str = Depends(oauth_schema), db: Session = Depends(get_db)):
    exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials",
                              headers={"WWW-Authenticate": "Bearer"})
    token_data = verify_jwt(token, exception)
    user = db.query(User).where(token_data.id == User.id).first()
    print(user)
    return token_data
