from redis.asyncio import Redis

class RedisRepo:
    """Redis 싱글톤 객체"""
    _instance = None
    
    @classmethod
    async def get_instance(cls)-> Redis:
        if cls._instance is None:
            cls._instance = Redis(
                host="127.0.0.1",
                port=6379,
                decode_responses=True,
                max_connections=10
            )
            ## TTL 만료 이벤트 설정
            await cls._instance.config_set("notify-keyspace-events", "Ex")
        return cls._instance
    
    
