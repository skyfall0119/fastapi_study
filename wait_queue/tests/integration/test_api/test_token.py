# import pytest
# from httpx import AsyncClient
# from main import app 
# from utils import config
# from httpx import ASGITransport

# ASGITransport(app=app) 은 FastAPI 서버를 내부적으로 호출할 수 있게 해줌.
## redis 만 띄웠을 때
# @pytest.mark.asyncio
# async def test_generate_token_async():
#     async with AsyncClient(
#         transport=ASGITransport(app=app),
#         base_url="http://test"
#     ) as client:
#         response = await client.post("/token")
#         assert response.status_code == 200

#         data = response.json()
#         assert "uuid" in data
#         assert data["status"] == config.TOKEN_WAIT





import pytest
from httpx import AsyncClient
from utils.util import verify_access_token

@pytest.mark.asyncio
async def test_generate_token():
    async with AsyncClient(base_url="http://localhost:8000") as client:
        response = await client.post("/token/")
        assert response.status_code == 200

        data = response.json()
        assert "uuid" in data
        assert "status" in data
        assert data["status"] == "wait"
        
        
@pytest.mark.asyncio
async def test_jwt_token():
    async with AsyncClient(base_url="http://localhost:8000") as client:
        response = await client.post("/token/jwt/")
        assert response.status_code == 200
        
        tk = response.json()
        data = verify_access_token(tk)
        print(tk)
        # {'uuid': 'c8cc0ea5-9b53-4f2b-aff3-863385ec9625', 'status': 'wait', 'exp': 1752990343}
        assert "uuid" in data
        assert "exp" in data
        assert "status" in data
        assert data["status"] == "wait"

