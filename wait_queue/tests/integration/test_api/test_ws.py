from fastapi.testclient import TestClient
from main import app


def test_websocket_attach_and_receive():
    client = TestClient(app)

    # 먼저 토큰을 생성
    token_response = client.post("/token")
    assert token_response.status_code == 200
    token_data = token_response.json()

    with client.websocket_connect("/ws") as websocket:
        # 토큰 전송
        websocket.send_json({
            "uuid": token_data["uuid"],
            "status": token_data["status"]
        })

        # 서버가 연결 유지할 경우, 클라이언트가 대기 메시지를 수신할 수 있음
        msg = websocket.receive_json()
        assert msg["status"] == "wait"
        assert isinstance(msg["position"], int)