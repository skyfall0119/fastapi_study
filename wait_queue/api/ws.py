from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from service.observer import  get_observer, WaitQueueObserver
from model.models import TokenResponse
import json
from utils.logger import get_logger
from utils import config, util

logger = get_logger(__name__)

router = APIRouter(prefix="/ws")

@router.websocket("/")
async def websocket_endpoint(websocket: WebSocket,
                        observer:WaitQueueObserver = Depends(get_observer)
                        ):
    token = None
    try:
        await websocket.accept()
        data = await websocket.receive_text()
        token = json.loads(data)['access_token']
        token_decoded = TokenResponse(**util.decode_token(token))
        # 웹소켓 추가
        attch = await observer.attach(token_decoded, websocket)
        logger.info(attch)
        if not attch:
            return
        
        # 웹소켓 연결 유지
        while True:
            client_msg = await websocket.receive_text()
            logger.info(f"ws msg: {client_msg}")
            print(client_msg)
        
    except WebSocketDisconnect:
        if token:
            await observer.detach(token_decoded.uuid)
    