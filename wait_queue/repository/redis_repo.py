from redis.asyncio import Redis, ConnectionPool
from redis.exceptions import RedisError, ConnectionError
from utils import config

class RedisRepo:
    """Redis 싱글톤 객체"""
    _instance = None
    
    @classmethod
    async def get_instance(cls)-> Redis:
        if cls._instance is None:
            try:
                cls._instance = Redis(
                    host=config.REDIS_HOST,
                    port=config.REDIS_PORT,
                    decode_responses=True,
                    max_connections=300
                )
                ## TTL 만료 이벤트 설정
                result = await cls._instance.config_set("notify-keyspace-events", "Ex")
                current = await cls._instance.config_get("notify-keyspace-events")
                print("notify-keyspace-events set result:", result, "current value:", current)
            except (ConnectionError, RedisError) as e:
                raise RuntimeError(f"Redis 초기화 실패 {e}") from e
        return cls._instance
    
    
    
    
