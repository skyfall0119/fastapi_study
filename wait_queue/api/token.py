from fastapi import APIRouter
from model.models import TokenResponse
from service.db_service import DbService
from repository.redis_repo import RedisRepo

router = APIRouter(prefix="/token")

@router.post("/", response_model=TokenResponse)
async def generate_token():
    redis = await RedisRepo.get_instance()
    db_service = DbService(redis)
    token = await db_service.create_token()
    return token

    
