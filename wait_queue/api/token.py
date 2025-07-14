from fastapi import APIRouter
from model.models import TokenResponse
from service.db_service import DbService
from repository.redis_repo import get_redis_sync
from utils.logger import get_logger
from utils.util import create_access_token

router = APIRouter(prefix="/token")

logger = get_logger(__name__)

@router.post("/")
async def generate_token()->dict:
    try:
        redis = get_redis_sync()
        db_service = DbService(redis)
        token = await db_service.create_token()
        return {"access_token":token}
    except Exception as e:
        logger.error(f"{e}")
        

# @router.post("/jwt/")
# async def generate_token():
#     try:
#         token = create_access_token()
#         return token
#     except Exception as e:
#         logger.error(f"{e}")

    
