from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..utils import verify
from ..schemas import Token
from ..models import User
from ..oauth2 import create_jwt
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(tags=['Auth'])


@router.post("/login", response_model=Token)
def login(login_cred: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).where(login_cred.username == User.email).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invallid Credentials")
    if not verify(login_cred.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invallid Credentials")

    token = create_jwt(data={"user_id": user.id})
    return {"token": token, "token_type": "bearer"}