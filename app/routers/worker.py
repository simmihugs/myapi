from fastapi import APIRouter
from lib.worker import processing_status

router = APIRouter(
    prefix="/worker",
    tags=["worker"],
    responses={404: {"description": "Worker not found"}},
)

@router.get("/")
async def worker_status():
    print(processing_status)
    return processing_status
