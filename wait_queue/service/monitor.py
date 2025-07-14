from redis.asyncio import Redis
from utils import config
import asyncio
from service.db_service import ActiveList
from repository.redis_repo import get_redis_sync
from utils.logger import get_logger

logger = get_logger(__name__)

class TokenMonitor:
    def __init__(self, redis:Redis):
        self.redis=redis
        self.active_list = ActiveList(redis)
        self.active_count_key = config.ACTIVE_COUNT_KEY
        self.token_prefix = config.TOKEN_PREFIX
        self.validate_interval = config.ACTIVE_VALIDATE_INTERVAL
        
    # 현재 접속자수 get
    async def get_active_count(self) -> int:
        count = await self.redis.get(self.active_count_key)
        logger.info(f"{count}")
        return 0 if count is None else count
        
    # 현재 접속자수 set
    async def set_active_count(self, count) -> None:
        logger.info(f"{count}")
        await self.redis.set(self.active_count_key, count)
        
    # TTL 만료 감지 (keyspace notification) 루프
    # 감지시 접속자수 -1
    async def watch_key_expiration(self) -> None:
        pubsub = self.redis.pubsub()
        await pubsub.psubscribe("__keyevent@0__:expired")

        async for message in pubsub.listen():
            if message["type"] == "pmessage":
                logger.info(f"{message}")
                
                expired_key = message["data"]

                if isinstance(expired_key, bytes):
                    expired_key = expired_key.decode()

                if expired_key.startswith(config.TOKEN_PREFIX):
                    token_uuid = expired_key.split(config.TOKEN_PREFIX)[1]
                    await self.active_list.remove(token_uuid)

            
    # 주기적으로 현재 접속자 수 확인 후 업데이트 루프
    async def validate_active_count(self) -> None:
        while True:
            logger.info(f"")
            await self._cleanup()
            await self._update_active_count()
            await asyncio.sleep(self.validate_interval)
    
    
    # 접속자수 업데이트
    async def _update_active_count(self)-> None:
        active_count = await self.active_list.count()
        logger.info(f"current active_list count = {active_count}")
        
        await self.set_active_count(count=active_count)


    # 유령 토큰 제거 (토큰은 만료됐는데 오류로 인해 active set 에서 제거가 안됐을 경우)
    async def _cleanup(self) -> None:
        uuids = await self.active_list.get_members()
        for token_uuid in uuids:
            exists = await self.active_list.exists(token_uuid=token_uuid)
            if not exists:
                logger.info(f"{token_uuid} expired but still in active_list")
                await self.active_list.remove(token_uuid)




## 단일객체로 모니터 유지
active_monitor:TokenMonitor = None


async def get_monitor()->TokenMonitor:
    global active_monitor
    if active_monitor is None:
        redis = get_redis_sync()
        active_monitor = TokenMonitor(redis)

    return active_monitor