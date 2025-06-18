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
        return cls._instance
    
    
