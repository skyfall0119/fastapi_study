from repository.redis_repo import RedisRepo
from fastapi import WebSocket

class WaitQueueObserver:
    def __init__(self, redis:RedisRepo):
        self.redis=redis
        self.ws_dict = {}  # 소켓 목록 "token_uuid": websocket

        
    # 웹소켓 딕셔너리에 추가
    # ***** 사용자 웹소켓을 받았을 때, 토큰으로 redis 대기열에 있는지 검증하고 저장. 
    async def attach(self, ws:WebSocket):
        ...
        

    # 대기열 큐에서 pop, 토큰 상태 active 반환, active_token_list 로 옮기기
    async def move_to_active(self):
        ...
        self.notify_active()
        ...
    
    # 대기열 큐에서 유저 제거. ## 웹소켓 연결 끊김 확인시
    async def detach(self):
        ...
        
    
    # 대기순번 날려주기
    async def notify_wait_number(self):
        ...
        
    # 사용자에게 입장 가능 알리기
    async def notify_active(self):
        ...
        
        
    # 접속자리 있는지 확인
    async def is_there_active_room(self):
        ...