import random
import uuid
import time
from redis.asyncio import Redis
from model.models import TokenResponse
from utils import config, util
from utils.logger import get_logger

logger = get_logger(__name__)


WAIT = config.TOKEN_WAIT
ACTIVE = config.TOKEN_ACTIVE

## 레디스 리스트 기반 선입선출 큐
## rpush, lpop
## 
class FIFOQueue: 
    def __init__(self, redis:Redis):
        self.redis = redis
        self.queue_key = config.WAIT_QUEUE_KEY
        self.token_prefix = config.TOKEN_PREFIX
        self.token_ttl = config.TTL_EXPIRE
        
    ## 대기열 추가 ## user uuid 
    async def insert(self, user_id: str) -> None:
        token_key = self.token_prefix + user_id
        logger.info(f"{token_key}")
        await self.redis.rpush(self.queue_key, user_id)
        await self.redis.set(token_key, config.TOKEN_WAIT)
        
        
    ## 대기열 pop 
    async def pop(self)-> TokenResponse | None:
        try:
            uuid = await self.redis.lpop(self.queue_key)
            if uuid:
                logger.info(f"{uuid}. status to active")
                return TokenResponse(uuid=uuid, status=ACTIVE)
            return None
        except Exception as e:
            logger.error(f"error {e}")
    
    # 대기열 리스트 반환
    async def get_all_waiting(self) -> list[str]:
        return await self.redis.lrange(self.queue_key, 0, -1)

    
    ## 대기열에서 토큰 확인
    async def validate(self, token: TokenResponse) -> bool:
        token_key = self.token_prefix + token.uuid
        stored_status = await self.redis.get(token_key)
        logger.info(f"{stored_status} is not None, {token.status}")
        return stored_status is not None and stored_status == token.status
        

class PriorityQueue:
    def __init__(self, redis:Redis):
        self.redis = redis
        self.queue_key = config.WAIT_QUEUE_KEY
        self.token_prefix = config.TOKEN_PREFIX
        self.token_ttl = config.TTL_EXPIRE
        
    ## 대기열 추가
    # time 기반으로 우선순위 설정.
    # 들어오는 시간이 겹쳐서 꼬임 방지 
    # score = time.time() + random.uniform(0, 0.01)
    async def insert(self, token:TokenResponse)->None:
        token_key = f"{self.token_prefix}{token.uuid}"
        score = time.time()
        await self.redis.zadd(self.queue_key, {token.uuid: score})
        await self.redis.set(token_key, WAIT)
        
    ## 대기열 pop 
    async def pop(self)->TokenResponse | None:
        # 가장 작은 score 1개 조회
        result = await self.redis.zrange(self.queue_key, 0, 0)  
        if not result:
            return None

        uuid = result[0]
        await self.redis.zrem(self.queue_key, uuid)
        return TokenResponse(uuid=uuid, status=WAIT)
    
    
    
    ## 대기열에서 토큰 확인
    async def validate(self, token: TokenResponse) -> bool:
        token_key = f"{self.token_prefix}{token.uuid}"
        stored_status = await self.redis.get(token_key)
        return stored_status is not None and stored_status == token.status


class ActiveList:
    def __init__(self, redis:Redis):
        self.redis = redis
        self.set_key = config.ACTIVE_SET_KEY
        self.token_prefix = config.TOKEN_PREFIX
        self.ttl = config.TTL_EXPIRE
        self.active_count_key = config.ACTIVE_COUNT_KEY
    
    # 유저 추가
    async def add_to_active(self, token: TokenResponse) -> None:
        # add token
        await self.redis.sadd(self.set_key, token.uuid)
        token_key = self.token_prefix + token.uuid 

        # set key status to active
        await self.redis.set(token_key, ACTIVE)
        # set key expiration
        await self.redis.expire(token_key, self.ttl) 

        logger.info(f"set token active, TTL: {token_key}")
        
        # 변수 업데이트
        await self.redis.incr(self.active_count_key)
        logger.info(f"increment active_count")

    # 유저 제거 (토큰 만료시 이 함수를 부르면 될듯)
    async def remove(self, token_uuid:str) -> None:
        logger.info(f"{token_uuid}")
        try:
            # if await self.exists(token_uuid=token_uuid):
            await self.redis.srem(self.set_key, token_uuid) #삭제
            await self.redis.decr(self.active_count_key) # -1
        except Exception as e:
            logger.error(f"error {e}")
            
    # 사용자 uuid 있는지 검사
    async def exists(self, token_uuid: str) -> bool:
        # activelist에 있는지
        try:
            in_set = await self.redis.sismember(self.set_key, token_uuid)
            if not in_set:
                return False
            
            # 토큰이 있는지.
            token_key = self.token_prefix + token_uuid
            token_exists = await self.redis.exists(token_key)
            return token_exists == 1
        except Exception as e:
            logger.error(f"error {e}")
            return False

    # 현재 사용자수 리턴
    async def count(self) -> int:
        return await self.redis.scard(self.set_key)
    
    # 전체 사용자 반환
    async def get_members(self) -> list[str]:
        return await self.redis.smembers(self.set_key)
        

class DbService:
    def __init__(self, redis:Redis):
        self.redis = redis
        self.wait_queue = FIFOQueue(redis) ## 대기열 큐 갈아끼우기 편하게
        self.active_set = ActiveList(redis)
        self.max_user = config.MAX_ACTIVE_SET


    # 토큰 생성 / db에 추가, 사용자에게 반환
    async def create_token(self) -> str:

        token, user_uuid = util.create_access_token()
        await self.wait_queue.insert(user_uuid)

        return token
    
    # 대기열 pop. 사용자리스트로 push
    async def promote_to_active(self)->TokenResponse:
        token = await self.wait_queue.pop()
        if token:
            token.status = ACTIVE
            await self.active_set.add_to_active(token)
        return token
    


    

