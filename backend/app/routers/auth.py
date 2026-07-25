from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db import get_db
from app import models
from app.schemas import user as user_schemas
from app.core import security
from app.models.user import User as UserModel

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/signup", response_model=user_schemas.UserOut)
def signup(payload: user_schemas.UserCreate, db: Session = Depends(get_db)):
    # unique username/email check
    if db.query(UserModel).filter(UserModel.username == payload.username).first():
        raise HTTPException(status_code=400, detail="username already registered")                          
    elif db.query(UserModel).filter(UserModel.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    elif db.query(UserModel).filter(UserModel.mobile == payload.mobile).first():
        raise HTTPException(status_code=400, detail="Mobile Number already registered")
    
    hashed = security.get_password_hash(payload.password)
    user = models.user.User(
        username=payload.username,
        email=payload.email,
        hashed_password=hashed,
        first_name=payload.first_name,
        last_name=payload.last_name,
        mobile=payload.mobile
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/login", response_model=user_schemas.Token)
def login(payload: user_schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.mobile == payload.mobile).first()
    if not user or not security.verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = security.create_access_token(subject=user.mobile)
    return {"access_token": token, "token_type": "bearer"}