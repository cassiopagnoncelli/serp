from fastapi import APIRouter

health_router = APIRouter(prefix="/health-check", tags=["Health"])

@health_router.get("")
async def health_check():
    return {"status": "ok"} 