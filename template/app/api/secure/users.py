from fastapi import APIRouter, HTTPException, Query, Depends
from sqlmodel import Session, SQLModel, select, update
from typing import Annotated
from app.models.user import *
from app.schemas.user import *
from config.core.database import *

router = APIRouter(tags=["Users API"])

@router.post("/users/", response_model=UserPublic)
async def create_user(user: UserCreate, session: SessionDep) -> UserPublic:
  user = User.model_validate(user)
  session.add(user)
  session.commit()
  session.refresh(user)
  return user

@router.get("/users/", response_model=list[UserPublic])
async def read_users(session: SessionDep, offset: int = 0, limit: Annotated[int, Query(ge=0, le=100)] = 100) -> list[UserPublic]:
  users = session.exec(select(User).offset(offset).limit(limit)).all()
  return users

@router.get("/users/{user_id}", response_model=UserPublic)
async def read_user(user_id: int, session: SessionDep) -> UserPublic:
  user = session.get(User, user_id)
  if not user:
    raise HTTPException(status_code=404, detail="User not found")
  return user

@router.patch("/users/{user_id}", response_model=UserPublic)
async def update_user(user_id: int, user: UserUpdate, session: SessionDep) -> UserPublic:
  user_record = session.get(User, user_id)
  if not user_record:
    raise HTTPException(status_code=404, detail="User not found")
  user_data = user.model_dump(exclude_unset=True)
  print(user_data)
  user_record.sqlmodel_update(user_data)
  session.add(user_record)
  session.commit()
  session.refresh(user_record)
  return user_record

@router.delete("/users/{user_id}")
async def delete_user(user_id: int, session: SessionDep):
  user = session.get(User, user_id)
  if not user:
    raise HTTPException(status_code=404, detail="User not found")
  session.delete(user)
  session.commit()
  return {"ok": True}
