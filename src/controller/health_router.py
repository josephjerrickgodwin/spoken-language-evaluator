from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["Health Controller"])


@router.get("")
async def health_check():
    return {"message": "The system is up and running"}
