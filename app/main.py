from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from .database import engine, SessionLocal, get_db 
from .models import Base, UserDB
from .schemas import UserCreate, UserRead
import os
import httpx

ACCOUNT_BASE_URL = os.getenv("ACCOUNT_BASE_URL", "http://localhost:8002")


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(lifespan=lifespan)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create user
@app.post("/api/users", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = UserDB(**user.model_dump())
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Email or phone number already exists"
        )


# Get all users
@app.get("/api/users", response_model=list[UserRead])
def get_users(db: Session = Depends(get_db)):
    stmt = select(UserDB).order_by(UserDB.id)
    return list(db.execute(stmt).scalars())


# Get single user
@app.get("/api/users/{user_id}", response_model=UserRead)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(UserDB, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# Update user
@app.put("/api/users/{user_id}", response_model=UserRead)
def update_user(user_id: int, updated: UserCreate, db: Session = Depends(get_db)):
    user = db.get(UserDB, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    for key, value in updated.model_dump().items():
        setattr(user, key, value)

    try:
        db.commit()
        db.refresh(user)
        return user
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Update failed")


# Delete user
@app.delete("/api/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(UserDB, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()

    # Best-effort cascade delete in Account service
    try:
        r = httpx.delete(f"{ACCOUNT_BASE_URL}/accounts/by-user/{user_id}", timeout=5.0)
        # idempotent delete: 204 or 404 are both fine
        if r.status_code not in (204, 404):
            # don’t fail user deletion because account service hiccuped
            pass
    except httpx.RequestError:
        # same idea: don't block user deletion if Account is down
        pass

