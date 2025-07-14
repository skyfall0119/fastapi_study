from redis.asyncio import Redis
from service.db_service import DbService
from fastapi import WebSocket
from utils import config, util
from model.models import TokenResponse
from repository.redis_repo import get_redis_sync
import asyncio
from utils.logger import get_logger

logger = get_logger(__name__)


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
            logger.info(f"websocket received {token.uuid}")
            self.ws_dict[token.uuid] = ws
            return True
        else:
            logger.info("websocket is not valid. closing")
            await ws.close(code=4001)  # Invalid token
            return False
    
    # 대기열 큐에서 유저 제거. ## 웹소켓 연결 끊김 확인시
    async def detach(self, token_uuid:str):
        if token_uuid in self.ws_dict:
            logger.info(f"{token_uuid}")
            del self.ws_dict[token_uuid]
        
    
    async def notify_loop(self):
        while True:
            # 1. 대기순번 전달
            await self._notify_wait_number()
            
            # 2. 입장 가능 인원 체크
            available_slots = await self._is_there_active_room()
            
            # 3. 그 수만큼 프로모트
            logger.info(f"available slot? {available_slots}")
            for _ in range(available_slots):
                res = await self._promote_and_notify()
                if res is None:
                    break

            await asyncio.sleep(config.WAIT_NOTIFY_INTERVAL)  # 1~2초 간격
    

    # 웹소켓으로 대기열 -> active 상태변경 알려주기
    async def _promote_and_notify(self)->TokenResponse:
        token = await self.db_service.promote_to_active()
        logger.info(f"{token}")
        if token:
            if token.uuid in self.ws_dict:
                ws = self.ws_dict.get(token.uuid)
                
                encoded = util.upgrade_access_token_active(token)
                
                
                await ws.send_json({"access_token":encoded})
                await ws.close()
                del self.ws_dict[token.uuid]
        return token

    
    # 대기순번 날려주기
    async def _notify_wait_number(self)->None:
        wait_list = await self.db_service.wait_queue.get_all_waiting()
        logger.info(f"current wait list {wait_list}")
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
        logger.info(f"current {count} < max active {config.MAX_ACTIVE_SET}")
        if count < config.MAX_ACTIVE_SET:
            return config.MAX_ACTIVE_SET - count
        else:
            return 0
        
    
        


## 단일객체로 옵저버 유지
wait_observer:WaitQueueObserver = None


async def get_observer()->WaitQueueObserver:
    global wait_observer
    if wait_observer is None:
        redis = get_redis_sync()
        wait_observer = WaitQueueObserver(redis)
    return wait_observer