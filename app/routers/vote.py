from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import database, models, oauth2, settings, schemas

router = APIRouter(
    prefix="/vote",
    tags=["vote"]
)


@router.post("/", status_code=status.HTTP_201_CREATED)
def vote(vote: schemas.Vote, db: Session = Depends(database.get_db), current_user: int = Depends(oauth2.get_current_user)):
    vote_query = db.query(models.Votes).filter(vote.post_id == models.Votes.post_id, current_user.id == models.Votes.user_id)
    post = db.query(models.Post).where(vote.post_id == models.Post.id).first()
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No post found with id: {vote.post_id}")
    if vote.direction == 1:
        if vote_query.first():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Already voted")
        vote = models.Votes(user_id=current_user.id, post_id=vote.post_id)
        db.add(vote)
        db.commit()
        return {"message": "Vote successfully added"}

    else:
        if not vote_query.first():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="This action cannot be completed")
        vote_query.delete(synchronize_session=False)
        db.commit()
        return {"message": "Vote successfully deleted"}

