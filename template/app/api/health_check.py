from fastapi import APIRouter, HTTPException, Query, Depends
from sqlmodel import Session, SQLModel, select, update
from typing import Annotated
from subprocess import check_output

router = APIRouter(tags=["Health Check API"])

def get_git_revision_short_hash() -> str:
  return check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('ascii').strip()

@router.get("/health-check")
def health_check():
  return {
    "status": "ok",
    "revision": get_git_revision_short_hash()
  }
