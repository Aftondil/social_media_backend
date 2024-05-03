from .database import get_db, engine
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from .routers import post, user, auth, vote
from . import models

models.Base.metadata.create_all(bind=engine)
app = FastAPI()

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)

@app.get("/")
def root():
    return {"Hello": "World"}


@app.get("/sql")
def sql(session: Session = Depends(get_db)):
    posts = session.query(models.Post).all()
    return {"posts": posts}






