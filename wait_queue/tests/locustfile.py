from locust import HttpUser, task, between
import json
import websocket
from utils import config

class WaitQueueUser(HttpUser):
    wait_time = between(1, 2)
    LIMITED_URL = "/limited/"

    @task
    def websocket_queue(self):
        # 1. 토큰 발급
        resp = self.client.post("/token/")
        # token = resp.json()
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
                    if "uuid" in msg:
                        token = msg['uuid']
                except websocket.WebSocketConnectionClosedException:
                    print("[Locust] WebSocket closed by server (TTL 만료 등)")
                    break
                except Exception as e:
                    print(f"[Locust] WebSocket error: {e}")
                    break
            
            if token:
                try:
                    for _ in range(config.RATE_LIMIT+1):
                        resp = self.client.get("/limited/", params={"token":token})
                except Exception as e:
                    print(f"[Locust] error calling limited {e}")
            
        finally:
            ws.close()
