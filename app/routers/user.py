from fastapi import status, Depends, APIRouter, HTTPException
from ..schemas import UserCreate, UserOut
from sqlalchemy.orm import Session
from ..database import get_db
from ..utils import hash
from .. import models


router = APIRouter(tags=["Users"], prefix="/users")


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserOut)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    user.password = hash(user.password)
    user_created = models.User(**user.dict())
    db.add(user_created)
    db.commit()
    db.refresh(user_created)
    return user_created


@router.get("/{id}", response_model=UserOut)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(id == models.User.id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id: {id} does not exist")
    return user