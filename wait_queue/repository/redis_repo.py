from redis.asyncio import Redis
from redis.exceptions import RedisError, ConnectionError

class RedisRepo:
    """Redis 싱글톤 객체"""
    _instance = None
    
    @classmethod
    async def get_instance(cls)-> Redis:
        if cls._instance is None:
            try:
                cls._instance = Redis(
                    host="172.25.239.217/20",
                    port=6379,
                    decode_responses=True,
                    max_connections=10
                )
                ## TTL 만료 이벤트 설정
                await cls._instance.config_set("notify-keyspace-events", "Ex")

            except (ConnectionError, RedisError) as e:
                raise RuntimeError(f"Redis 초기화 실패 {e}") from e
        return cls._instance
    
    
    
    
