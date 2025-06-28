"""
conftest.py는 pytest가 공식적으로 지원하는 특수한 설정 파일
테스트 전체에서 공통적으로 사용되는 fixture, hook, 설정 등을 
등록할 수 있는 pytest 표준 방식

pytest는 테스트 실행 시 자동으로 디렉토리 내의 conftest.py 파일을 로드함
테스트 파일에 import 하지 않아도 fixture를 사용 가능
"""

import pytest
import pytest_asyncio
import fakeredis.aioredis


@pytest_asyncio.fixture()
async def fake_redis():
    redis = await fakeredis.aioredis.FakeRedis(decode_responses=True)
    yield redis
    await redis.flushall()
    await redis.aclose()