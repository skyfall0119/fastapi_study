import time
import pytest
import asyncio
import websockets
import httpx
import json
from utils import config

TOKEN_URL = "http://localhost:8000/token/"
WS_URL = "ws://localhost:8000/ws/"
LIMITED_URL = "http://localhost:8000/limited/"
NUM_CLIENT = 3  # match the rate limit for easier test

@pytest.mark.asyncio
async def test_rate_limiter_fixed():
    async def connect_and_listen(uuid):
        async with websockets.connect(WS_URL) as ws:
            await ws.send(json.dumps({
                "uuid": uuid,
                "status": config.TOKEN_WAIT
            }))
            # Wait for promotion to active
            while True:
                msg = await ws.recv()
                msg_data = json.loads(msg)
                if msg_data.get("status") == config.TOKEN_ACTIVE:
                    return msg_data  ## active token!!
    
    tokens = []
    async with httpx.AsyncClient() as client:
        # 1. 토큰 발급
        for _ in range(NUM_CLIENT):
            resp = await client.post(TOKEN_URL)
            assert resp.status_code == 200
            tokens.append(resp.json())

        # 2. 대기열에서 active 될 때까지 기다림
        active_tokens = await asyncio.gather(*[connect_and_listen(tk['uuid']) for tk in tokens])

        # 3. active 된 토큰으로 /limited 호출 (rate limit 3회 허용)
        # 이 예제에서는 간단하게 uuid 만 보내서 검증
        # 추후 프로젝트에서는 jwt 로
        for token in active_tokens:
            print(f"\n\n{token['uuid']}")
            for _ in range(config.RATE_LIMIT):
                resp = await client.get(LIMITED_URL, params={"token": token['uuid']})
                print(f"{resp}")
                assert resp.status_code == 200
                assert resp.json()["msg"] == "ok"
            # 리밋 후 한번 더 콜하면 out
            resp = await client.get(LIMITED_URL, params={"token": token['uuid']})
            print(f"{resp}")
            assert resp.status_code == 429
            print(f"sleeping for window length {config.RATE_WINDOW}")
            await asyncio.sleep(config.RATE_WINDOW+1)
            # 윈도우만큼 기다렸다 다시 콜.
            print(f"after window")
            resp = await client.get(LIMITED_URL, params={"token": token['uuid']})
            print(f"{resp}")