
"""
jwt 토큰을 사용해서 사용자 토큰 처리
현재는 TokenResponse 로 돼있

"""

from fastapi import Header, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta, timezone
import uuid
from jose import jwt, JWTError
from typing import Tuple, Optional
from model.models import TokenResponse
from utils import config
from utils.logger import get_logger

logger = get_logger(__name__)
auth_scheme = HTTPBearer()

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
   
## 헤더에서 jwt 토큰 추출
def verify_access_token(credentials:HTTPAuthorizationCredentials = Depends(auth_scheme))->dict:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, config.JWT_SECRET, algorithms=config.JWT_ALGORITHM)
        return payload
    except JWTError as e:
        logger.error(f"Token verification failed: {str(e)}")
        raise
    
def decode_token(token:str) -> dict:
    try:
        payload = jwt.decode(token, config.JWT_SECRET, algorithms=config.JWT_ALGORITHM)
        return payload
    except JWTError as e:
        logger.error(f"Token verification failed: {str(e)}")
        raise
   
   
    
def upgrade_access_token_active(token: TokenResponse):
    try:

        expire = datetime.now(timezone.utc) + config.TOKEN_EXP  
        token.exp = int(expire.timestamp())
        token.status = config.TOKEN_ACTIVE
        payload = token.model_dump()
        return jwt.encode(payload, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM)

    except JWTError as e:
        logger.error(f"upgrade token failed: {str(e)}")
        raise
    
    
def get_token_from_header(authorization: Optional[str] = Header(None)) -> str:
    logger.info(f"token: {authorization}")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=400, detail="invalid token")
    return authorization.split(" ", 1)[1]