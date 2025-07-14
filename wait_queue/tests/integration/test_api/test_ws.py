import pytest
import asyncio
import websockets
import httpx
import json
from utils import config, util

TOKEN_URL = "http://localhost:8000/token/"
WS_URL = "ws://localhost:8000/ws/"
NUM_CLIENT = 6

@pytest.mark.asyncio
async def test_multiple_websocket_clients():
    async def connect_and_listen(jwt_token):
        async with websockets.connect(WS_URL) as ws:
            
            await ws.send(json.dumps(jwt_token))
            msg = await ws.recv()
            msg_data = json.loads(msg)
            assert isinstance(msg_data["position"], int)
            return msg_data["position"]

    # uuid 받기. (테스트 유저 수만큼)
    tokens = []
    async with httpx.AsyncClient() as client:
        for _ in range(NUM_CLIENT):
            resp = await client.post(TOKEN_URL)
            assert resp.status_code == 200

            token = resp.json()
            tokens.append(token)

    # WebSocket 병렬 연결
    results = await asyncio.gather(*[connect_and_listen(tk) for tk in tokens])

    print("Queue positions:", results)
    ans = [i for i in range(1, NUM_CLIENT+1)]
    ## test_token 함께 테스트 진행시 포지션 +1
    ans_with_test_token = [i+1 for i in range(1, NUM_CLIENT+1)]
    assert sorted(results) == ans or sorted(results) == ans_with_test_token