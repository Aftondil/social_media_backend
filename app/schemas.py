from pydantic import BaseModel, EmailStr, conint
from datetime import datetime


class Post(BaseModel):
    id: int
    title: str
    content: str
    published: bool = True
    owner_id: int



class UserOut(BaseModel):
    id: int
    email: EmailStr


class Reply(Post):
    # owner_id: int
    id: int
    owner: UserOut


class ReplyPost(BaseModel):
    Post: Post
    votes: int



class UserCreate(BaseModel):
    email: EmailStr
    password: str


class Login(BaseModel):
    email: EmailStr
    password: str


class TokenData(BaseModel):
    id: str


class Token(BaseModel):
    token: str
    token_type: str


class Vote(BaseModel):
    post_id: int
    direction: conint(ge=0, le=1)
