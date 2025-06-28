# tests/test_service/test_monitor.py
import pytest
import asyncio
from service.monitor import TokenMonitor
from service.db_service import ActiveList
from unittest.mock import AsyncMock, patch
from redis.asyncio import Redis
from utils import config

@pytest.mark.asyncio
async def test_active_count_get_set(fake_redis:Redis):
    monitor = TokenMonitor(redis=fake_redis)

    # 기본값은 0
    count = await monitor.get_active_count()
    assert count == 0

    # 값을 저장하고 다시 불러오기
    await monitor.set_active_count(5)
    count = await monitor.get_active_count()
    assert int(count) == 5


@pytest.mark.asyncio
async def test_update_active_count(fake_redis:Redis):
    monitor = TokenMonitor(fake_redis)
    fake_user_num = 5
    
    ## 사용자 리스트 5명 모킹
    monitor.active_list.count = AsyncMock(return_value=fake_user_num) 
   
    # 1. set_active_count 함수를 모킹.
    # 2. _update_active_count 에서 set_active_count 를 호출 (asyncMock 으로 대체됨)
    # 3. await 한번 호출됨.  
    monitor.set_active_count = AsyncMock()
    await monitor._update_active_count()
    monitor.set_active_count.assert_awaited_once_with(count=fake_user_num)



@pytest.mark.asyncio
async def test_cleanup_removes_nonexistent_tokens(fake_redis):
    monitor = TokenMonitor(fake_redis)
    # ActiveList.get_members() 반환값 세팅
    monitor.active_list.get_members = AsyncMock(return_value=["token1", "token2", "token3"])

    # token1, token3 존재, token2 없음 설정
    async def exists_side_effect(token_uuid):
        return token_uuid != "token2"
    monitor.active_list.exists = AsyncMock(side_effect=exists_side_effect)
    monitor.active_list.remove = AsyncMock()

    await monitor._cleanup()

    # token2 만 remove 호출되어야 함
    monitor.active_list.remove.assert_awaited_once_with("token2")

@pytest.mark.asyncio
async def test_watch_key_expiration_removes_on_expired_key(fake_redis):
    monitor = TokenMonitor(fake_redis)
    monitor.active_list.remove = AsyncMock()

    # fake pubsub를 모킹 (비동기 제너레이터 함수로 메시지 생성)
    class FakePubSub:
        def __init__(self):
            self.subscribed = False
        async def psubscribe(self, channel):
            self.subscribed = True
        async def listen(self):
            # 정상 메시지 1개, 종료 위해 반복문 탈출
            yield {
                "type": "pmessage",
                "data": f"{config.TOKEN_PREFIX}uuid123".encode()
            }
            yield {
                "type": "pmessage",
                "data": f"otherkey".encode()
            }
            return

    monitor.redis.pubsub = lambda: FakePubSub()

    # run watch_key_expiration but exit after first message
    # 비동기 태스크로 실행하고, 타임아웃 후 취소 시도
    async def run_watch():
        try:
            await asyncio.wait_for(monitor.watch_key_expiration(), timeout=0.2)
        except asyncio.TimeoutError:
            pass

    await run_watch()

    monitor.active_list.remove.assert_awaited_once_with("uuid123")