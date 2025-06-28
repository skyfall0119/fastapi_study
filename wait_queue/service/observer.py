from redis.asyncio import Redis
from service.db_service import DbService
from fastapi import WebSocket
from utils import config
from model.models import TokenResponse
from repository.redis_repo import RedisRepo
import asyncio

WAIT = config.TOKEN_WAIT
ACTIVE = config.TOKEN_ACTIVE


class WaitQueueObserver:
    def __init__(self, redis:Redis):
        self.db_service = DbService(redis)
        self.ws_dict = {}  # 소켓 목록 "token_uuid": websocket

        
    # 웹소켓 딕셔너리에 추가
    # ***** 사용자 웹소켓을 받았을 때, 토큰으로 redis 대기열에 있는지 검증하고 저장. 
    async def attach(self, token:TokenResponse, ws:WebSocket)->bool:
    
        # 대기열에 존재하는지 검증
        is_valid = await self.db_service.wait_queue.validate(token)
        if is_valid:
            await ws.accept()
            self.ws_dict[token.uuid] = ws
            return True
        else:
            await ws.close(code=4001)  # Invalid token
        return False
    
    # 대기열 큐에서 유저 제거. ## 웹소켓 연결 끊김 확인시
    async def detach(self, token_uuid:str):
        if token_uuid in self.ws_dict:
            del self.ws_dict[token_uuid]
        
    
    async def notify_loop(self):
        while True:
            # 1. 대기순번 전달
            await self._notify_wait_number()
            
            # 2. 입장 가능 인원 체크
            available_slots = await self._is_there_active_room()
            
            # 3. 그 수만큼 프로모트
            for _ in range(available_slots):
                await self._promote_and_notify()

            await asyncio.sleep(config.WAIT_NOTIFY_INTERVAL)  # 1~2초 간격 추천
    

    # 웹소켓으로 대기열 -> active 상태변경 알려주기
    async def _promote_and_notify(self)->TokenResponse:
        token = await self.db_service.promote_to_active()
    
        if token:
            if token.uuid in self.ws_dict:
                ws = self.ws_dict.get(token.uuid)
                token.status = ACTIVE
                await ws.send_json(token.model_dump())
                await ws.close()
                del self.ws_dict[token.uuid]
        return token

    
    # 대기순번 날려주기
    async def _notify_wait_number(self)->None:
        wait_list = await self.db_service.wait_queue.get_all_waiting()
        for i, id in enumerate(wait_list):
            ws = self.ws_dict.get(id)
            if ws:
                try:
                    await ws.send_json({
                        "status": WAIT,
                        "position" : i +1
                    })
                except :
                    await self.detach(id)
        
        
    # 입장가능 확인
    async def _is_there_active_room(self) -> int:
        count = await self.db_service.active_set.count()
        if count < config.MAX_ACTIVE_SET:
            return config.MAX_ACTIVE_SET - count
        else:
            return 0
        
    
        


## 단일객체로 옵저버 유지
wait_observer:WaitQueueObserver = None


async def get_observer()->WaitQueueObserver:
    global wait_observer
    if wait_observer is None:
        redis = await RedisRepo.get_instance()
        wait_observer = WaitQueueObserver(redis)
    return wait_observer