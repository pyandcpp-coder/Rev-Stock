from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
import sys,os
from datetime import datetime , timedelta
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..')))
from core import database,security

# defineing pydantic models for request / response

class UserCreate(BaseModel):
    email: str
    password :str

class Token(BaseModel):
    access_token :str
    token_type :str

router = APIRouter(
    prefix= "/users",
    tags=["users"],
)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/signup",status_code = status.HTTP_201_CREATED)
def create_user (user: UserCreate,db: Session = Depends(get_db)):
    db_user = db.query(database.User).filter(database.User.email==user.email).first()
    if db_user:
        raise HTTPException(status_code =400, detail =" Email Already Exists")
    hashed_password = security.get_password_hash(user.password)
    new_user = database.User(email = user.email,hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message":"User created successfully"}

@router.post("/login",response_model=Token)
def login_for_access_token(form_data: UserCreate, db: Session = Depends(get_db)):
    user = db.query(database.User).filter(database.User.email == form_data.email).first()
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
