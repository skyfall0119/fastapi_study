from fastapi import APIRouter
from model.models import TokenResponse
from service.db_service import DbService
from repository.redis_repo import RedisRepo
from utils.logger import get_logger

router = APIRouter(prefix="/token")

logger = get_logger(__name__)

@router.post("/", response_model=TokenResponse)
async def generate_token():
    try:
        redis = await RedisRepo.get_instance()
        db_service = DbService(redis)
        token = await db_service.create_token()
        return token
    except Exception as e:
        logger.error(f"{e}")

    
