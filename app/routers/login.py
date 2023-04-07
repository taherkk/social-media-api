from fastapi import status, HTTPException, Depends, APIRouter
from .. import models, schemas
from sqlalchemy.orm import Session
from ..database import get_db

router = APIRouter(
        prefix="/auth",
        tags=["Auth"]
        )


