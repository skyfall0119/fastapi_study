import time
import pytest
import asyncio
import websockets
import httpx
import json
from utils import config

TOKEN_URL = "http://localhost:8000/token/"
WS_URL = "ws://localhost:8000/ws/"
LIMITED_URL = "http://localhost:8000/limited/deco/"
NUM_CLIENT = 2  # match the rate limit for easier test

@pytest.mark.asyncio
async def test_rate_limiter_deco_fixed():
    async def connect_and_listen(jwt_token):
        async with websockets.connect(WS_URL) as ws:
            await ws.send(json.dumps(jwt_token))
            # Wait for promotion to active
            while True:
                msg = await ws.recv()
                msg_data = json.loads(msg)
                print(msg_data)
                if "access_token" in msg_data:
                    return msg_data

    
    tokens = []
    async with httpx.AsyncClient() as client:
        # 1. 토큰 발급
        for _ in range(NUM_CLIENT):
            resp = await client.post(TOKEN_URL)
            assert resp.status_code == 200
            tokens.append(resp.json())

        # 2. 대기열에서 active 될 때까지 기다림
        active_tokens = await asyncio.gather(*[connect_and_listen(tk) for tk in tokens])

        # 3. active 된 토큰으로 /limited 호출 (rate limit 3회 허용)
        for token in active_tokens:
            print(f"\n\ntoken: {token} {type(token)}")
            header = {"Authorization" : f"Bearer {token['access_token']}"}
            for _ in range(config.RATE_LIMIT):
                
                resp = await client.get(LIMITED_URL, headers=header)
                print(f"{resp}")
                assert resp.status_code == 200
                assert resp.json()["msg"] == "ok"
                
            # 최대 리밋 후 한번 더 콜하면 out
            resp = await client.get(LIMITED_URL, headers=header)
            print(f"should be limited {resp}")
            assert resp.status_code == 429
            print(f"sleeping for window length {config.RATE_WINDOW}")
            await asyncio.sleep(config.RATE_WINDOW+1)
            
            # 윈도우만큼 기다렸다 다시 콜.
            print(f"after window")
            resp = await client.get(LIMITED_URL, headers=header)
            print(f"{resp}")