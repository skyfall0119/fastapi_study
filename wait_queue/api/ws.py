from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from service.observer import WaitQueueObserver


router = APIRouter(prefix="/ws")

@router.websocket("")
async def register_token(ws:WebSocket, token:str):
    ## observer 에 웹소켓 등록
    # 
    ...
    
    
@router.get("/wait")
async def wait_enter(ws:WebSocket, token:str):
    ## 대기화면
    # 
    ...