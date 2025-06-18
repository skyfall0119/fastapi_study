from repository.redis_repo import RedisRepo 


class QueueService:
    def __init__(self):
        self.redis = RedisRepo.get_instance()
        
        
    ## 대기열 추가
    async def insert(self):
        ...
        
    ## 대기열 pop 
    async def pop(self):
        ...


    