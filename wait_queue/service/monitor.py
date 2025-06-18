from repository.redis_repo import RedisRepo


class TokenMonitor:
    def __init__(self, redis:RedisRepo):
        self.redis=redis
        
        
    # 현재 접속자수 변수 get
    async def get_active_count(self) -> int:
        ...
        
    # 현재 접속자수 변수 set
    async def set_active_count(self) -> int:
        ...
        
        
    # TTL 만료 감지 (keyspace notification)
    # 감지시 접속자수 -1
    async def watch_key_expiration(self):
        ...

            
    # 주기적으로 현재 접속자 수 확인, 업데이트
    async def validate_active_count(self):
        ...

    # 유령 토큰 제거
    async def cleanup(self):
        ...