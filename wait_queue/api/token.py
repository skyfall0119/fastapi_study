from fastapi import APIRouter
from model.models import TokenResponse


router = APIRouter(prefix="/token")

@router.post("", response_model=TokenResponse)
async def generate_token():
    ## 1. 토큰 생성. 초기상태 waiting
    ## 3. redis wait 큐 등록
    ...
    
