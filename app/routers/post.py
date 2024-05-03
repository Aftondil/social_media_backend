from fastapi import Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from ..schemas import Post, Reply, ReplyPost
from ..database import get_db
from sqlalchemy import desc, func
from typing import List, Optional
from .. import models, oauth2


router = APIRouter(tags=["Posts"], prefix="/posts")


# , response_model=List[Reply]
@router.get("/", response_model=List[ReplyPost])
def get_posts(db: Session = Depends(get_db), limit: int = 10, offset: int = 0, search: Optional[str] = ''):
    result = db.query(models.Post, func.count(models.Votes.post_id).label('votes')).join(models.Votes, models.Votes.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.title.contains(search)).limit(limit).offset(offset).all()
    return result


@router.get("/latests", response_model=Reply)
def get_latest_posts(db: Session = Depends(get_db)):
    post = db.query(models.Post).order_by(desc(models.Post.created_at)).first()
    return post


@router.get("/{id}", response_model=ReplyPost)
def get_post(id: int, response: Response, db: Session = Depends(get_db)):
    post = db.query(models.Post, func.count(models.Votes.post_id).label('votes')).join(models.Votes, models.Votes.post_id == models.Post.id, isouter=True).group_by(models.Post.id).where(
        id == models.Post.id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} not found")
    return post


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=Reply)
def post(post: Post, db: Session = Depends(get_db), user_data: int = Depends(oauth2.get_current_user)):
    print("\n\n\n\n\n\n", user_data, "\n\n\n\n\n")
    new_post = models.Post(**post.dict())
    new_post.owner_id = user_data.id
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), user_data: int = Depends(oauth2.get_current_user)):
    post = db.query(models.Post).where(id == models.Post.id)
    if not post.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} not found")

    if post.first().owner_id != user_data.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to alter this post")
    post.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}", response_model=Reply)
def update(id: int, post: Post, db: Session = Depends(get_db), user_data: int = Depends(oauth2.get_current_user)):
    posts = db.query(models.Post).where(id == models.Post.id)
    index = posts.first()
    if not index:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} not found")
    if posts.first().owner_id != user_data.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to alter this post")
    posts.update(post.dict(), synchronize_session=False)
    db.commit()
    # db.refresh(post)
    return posts.first()