from locust import HttpUser, task, between
import json
import websocket
from utils import config
import time
from fastapi import HTTPException

class WaitQueueUser(HttpUser):
    wait_time = between(1, 5)
    LIMITED_URL = "/limited/"

    @task
    def websocket_queue(self):
        # 1. 토큰 발급
        resp = self.client.post("/token/")
        if resp.status_code == 200 and resp.text:
            try:
                token = resp.json()
            except Exception as e:
                print(f"JSON decode error: {e}, resp.text={resp.text}")
                return
        else:
            print(f"Token API error: status={resp.status_code}, text={resp.text}")
            return
        
        
        # 2. 웹소켓 연결
        ws_url = self.host.replace("http", "ws") + "/ws/"
        ws = websocket.WebSocket()
        try:
            ws.connect(ws_url)
            ws.send(json.dumps(token))
            token = None
            while True:
                try:
                    msg = ws.recv()
                    # print(f"[Locust] Received: {msg}")
                    if not msg.strip():  # 빈 문자열 또는 공백 무시
                        continue
                    token = json.loads(msg)
                    # if "access_token" in token:
                    #     token = msg['access_token']
                except websocket.WebSocketConnectionClosedException:
                    # print("[Locust] WebSocket closed by server (TTL 만료 등)")
                    break
                except Exception as e:
                    # print(f"[Locust] WebSocket error: {e}")
                    break
            
            if token:
                try:
                    header = {"Authorization" : f"Bearer {token['access_token']}"}
                    for _ in range(config.RATE_LIMIT+1):
                        resp = self.client.get("/limited/", headers=header)
                        # print(resp)
                        if resp.status_code == 429:
                            print(f"too many request")
                            break
                except HTTPException as e:
                    print("limit exceeded")
                except Exception as e:
                    print(f"[Locust] error calling limited {e}")
                time.sleep(10)
            
        finally:
            ws.close()
