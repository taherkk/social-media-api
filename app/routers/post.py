from fastapi import status, HTTPException, Depends, APIRouter
from .. import models, schemas, oauth2
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import get_db
from typing import List, Optional

router = APIRouter(
    prefix="/posts",
    tags=['Posts']
)


# We are returning a list in the response, so for response validation of a list we use the List class from typing
@router.get("/", response_model=List[schemas.PostOut])
#@router.get("/")
# implemented pagination using skip and limit
def get_posts(db: Session = Depends(get_db), current_user = Depends(oauth2.get_current_user), limit: int = 10, skip: int = 0, search: Optional[str] = ""):

    #posts = db.query(models.Post).filter( models.Post.title.contains(search)).offset(skip).limit(limit).all()

    posts = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.title.contains(search)).offset(skip).limit(limit).all()

    return posts

# Get operation using an id of the post
@router.get("/{id}", response_model=schemas.PostOut)
# This converts the passed id into an integer. Remove response if using exceptions
def get_posts_id(id: int, db: Session = Depends(get_db), current_user = Depends(oauth2.get_current_user)):

    #post = db.query(models.Post).filter(models.Post.id == id).first()
    post = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.id == id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} not found")

    return post


# POST Operation

# POST request should return 201 instead of 200

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db), current_user = Depends(oauth2.get_current_user)):

    # Unpacks the dict into arguments
    new_post = models.Post(owner_id=current_user.id, **post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


# DELETE Operation

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), current_user = Depends(oauth2.get_current_user)):

    post_query = db.query(models.Post).filter(models.Post.id == id)

    post = post_query.first()

    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} does not exist")

    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to perform requested action")

    post_query.delete(synchronize_session=False)
    db.commit()

    return  # delete api call should not return anything


# Update Operation

@router.put("/{id}", status_code=status.HTTP_202_ACCEPTED, response_model=schemas.Post)
def change_post(id: int, post_update: schemas.PostCreate, db: Session = Depends(get_db), current_user = Depends(oauth2.get_current_user)):

    post_query = db.query(models.Post).filter(models.Post.id == id)

    post = post_query.first()

    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} not found")

    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to perform requested action")

    post_query.update(post_update.dict(), synchronize_session=False)
    db.commit()

    return post_query.first()
