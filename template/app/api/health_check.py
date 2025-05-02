from fastapi import APIRouter, HTTPException, Query, Depends
from sqlmodel import Session, SQLModel, select, update
from typing import Annotated
from subprocess import check_output, CalledProcessError

router = APIRouter(tags=["Health Check API"])

def get_git_revision_short_hash() -> str:
  try:
    return check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('ascii').strip()
  except CalledProcessError:
    return "unknown"

@router.get("/health-check")
async def health_check():
  return {
    "status": "ok",
    "revision": get_git_revision_short_hash()
  }
