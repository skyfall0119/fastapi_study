import pytest
import asyncio
import websockets
import json
from utils import config

TOKEN_URL = "http://localhost:8000/token"
WS_URL = "ws://localhost:8000/ws"  
NUM_CLIENT = 6

@pytest.mark.asyncio
async def test_multiple_websocket_clients():
    async def connect_and_listen(uuid):
        async with websockets.connect(WS_URL) as ws:
            await ws.send(json.dumps({
                "uuid": uuid,
                "status" : config.TOKEN_WAIT
            }))
            msg = await ws.recv()
            msg_data = json.loads(msg)
            assert isinstance(msg_data["position"], int)
            return msg_data["position"]

    # uuid 받기. (테스트 유저 수만큼)
    import httpx
    tokens = []
    async with httpx.AsyncClient() as client:
        for _ in range(NUM_CLIENT):
            resp = await client.post(TOKEN_URL)
            assert resp.status_code == 200
            tokens.append(resp.json()["uuid"])

    # WebSocket 병렬 연결
    results = await asyncio.gather(*[
        connect_and_listen(uuid) for uuid in tokens
    ])

    print("Queue positions:", results)
    ans = [i for i in range(1, NUM_CLIENT+1)]
    assert sorted(results) == ans