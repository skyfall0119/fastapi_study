
"""
jwt 토큰을 사용해서 사용자 토큰 처리
현재는 TokenResponse 로 돼있

"""

from datetime import datetime, timedelta, timezone
import uuid
from jose import jwt, JWTError
from typing import Tuple

from utils import config
from utils.logger import get_logger

logger = get_logger(__name__)

def create_access_token(expires_delta: timedelta = config.TOKEN_EXP,
                        status:str = config.TOKEN_WAIT
                        )->Tuple[str, str]:
    expire = datetime.now(timezone.utc) + expires_delta  
    user_uuid = str(uuid.uuid4())
    payload = {
        "uuid": user_uuid,
        "status": status,
        "exp": int(expire.timestamp())
    }
    token = jwt.encode(payload, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM)
    return token, user_uuid

def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, config.JWT_SECRET, algorithms=config.JWT_ALGORITHM)
        return payload
    except JWTError as e:
        logger.error(f"Token verification failed: {str(e)}")
        raise
    
    
def upgarde_access_token_active(token: str):
    try:
        payload = jwt.decode(token, config.JWT_SECRET, algorithms=config.JWT_ALGORITHM)
        payload['status'] = config.TOKEN_ACTIVE
        return jwt.encode(payload, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM)

    except JWTError as e:
        logger.error(f"upgrade token failed: {str(e)}")
        raise
