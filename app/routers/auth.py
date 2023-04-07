from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

from .. import models, schemas, utils, oauth2, database

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post('/login', response_model=schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):

    #user = db.query(models.User).filter(models.User.email == user_credentials.email).first()
    # Because it's a form the parameters need to be sent as form fields rather than json object. The form data will consist of username & password as key value pairs.
    user = db.query(models.User).filter(
        models.User.email == user_credentials.username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")

    if not utils.verify(user_credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials")

    # create token

    access_token = oauth2.create_access_token(data={"user_id": user.id})

    # return token

    return {"access_token": access_token, "token_type": "Bearer"}
