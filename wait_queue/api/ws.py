from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from service.observer import  get_observer, WaitQueueObserver
from model.models import TokenResponse
import json

router = APIRouter(prefix="/ws")

@router.websocket("/")
async def websocket_endpoint(websocket: WebSocket,
                        observer:WaitQueueObserver = Depends(get_observer)
                        ):
    await websocket.accept()
    
    try:
        data = await websocket.receive_text()
        # {"uuid": "abcd-1234", "status": "wait"}
        parsed = json.loads(data)
        token = TokenResponse(**parsed)
        
        # 웹소켓 추가
        if not await observer.attach(token, websocket):
            return
        
        # 웹소켓 연결 유지
        while True:
            client_msg = await websocket.receive_text()
            print(client_msg)
        
    except WebSocketDisconnect:
        await observer.detach(token.uuid)
    



## Option 2 : polling 기반 대기순번 받기
@router.get("/wait")
async def wait_position(token: str,
                        observer:WaitQueueObserver = Depends(get_observer)
                        ):
    ...