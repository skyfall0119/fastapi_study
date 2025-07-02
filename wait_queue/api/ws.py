from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from service.observer import  get_observer, WaitQueueObserver
from model.models import TokenResponse
import json
from utils.logger import get_logger
from utils import config

logger = get_logger(__name__)

router = APIRouter(prefix="/ws")

@router.websocket("")
async def websocket_endpoint(websocket: WebSocket,
                        observer:WaitQueueObserver = Depends(get_observer)
                        ):
    
    try:
        await websocket.accept()
        data = await websocket.receive_text()
        # {"uuid": "abcd-1234"}
        parsed = json.loads(data)
        
        token = TokenResponse(uuid=parsed['uuid'],
                              status=config.TOKEN_WAIT)
        
        # 웹소켓 추가
        attch = await observer.attach(token, websocket)
        logger.info(attch)
        if not attch:
            return
        
        # 웹소켓 연결 유지
        while True:
            client_msg = await websocket.receive_text()
            logger.info(f"ws msg: {client_msg}")
            print(client_msg)
        
    except WebSocketDisconnect:
        logger.info(f"ws disconnected {token.uuid}")
        await observer.detach(token.uuid)
    



# ## Option 2 : polling 기반 대기순번 받기
# @router.get("/wait")
# async def wait_position(token: str,
#                         observer:WaitQueueObserver = Depends(get_observer)
#                         ):
#     ...