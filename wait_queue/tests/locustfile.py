from locust import HttpUser, task, between
import json
import websocket
import threading
import time

class WaitQueueUser(HttpUser):
    wait_time = between(1, 2)

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
            while True:
                try:
                    msg = ws.recv()
                    # print(f"[Locust] Received: {msg}")
                except websocket.WebSocketConnectionClosedException:
                    print("[Locust] WebSocket closed by server (TTL 만료 등)")
                    break
                except Exception as e:
                    print(f"[Locust] WebSocket error: {e}")
                    break
        finally:
            ws.close()
