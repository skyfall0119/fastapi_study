
"""
jwt 토큰을 사용해서 사용자 토큰 처리
현재는 TokenResponse 로 돼있

"""

from fastapi import HTTPException
from datetime import datetime, timedelta, timezone
import uuid
from jose import jwt, JWTError

from utils import config
from utils.logger import get_logger

logger = get_logger(__name__)

def create_access_token(expires_delta: timedelta = config.TOKEN_EXP):
    expire = datetime.now(timezone.utc) + expires_delta  
    payload = {
        "uuid": str(uuid.uuid4()),
        "status": config.TOKEN_WAIT,
        "exp": int(expire.timestamp())
    }
    token = jwt.encode(payload, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM)
    return token

def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, 
                             config.JWT_SECRET, 
                             algorithms=config.JWT_ALGORITHM)
        # payload['exp'] = datetime.fromtimestamp(payload['exp'],timezone.utc)

        return payload
    except JWTError as e:
        logger.error(f"Token verification failed: {str(e)}")
        raise
