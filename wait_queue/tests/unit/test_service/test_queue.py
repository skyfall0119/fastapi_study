import pytest
import asyncio
from service.db_service import FIFOQueue, PriorityQueue
from model.models import TokenResponse
from utils import config
import uuid

@pytest.mark.asyncio
async def test_fifo_insert_and_pop(fake_redis):
    queue = FIFOQueue(fake_redis)

    ## insert 확인
    token = TokenResponse(uuid=str(uuid.uuid4()), status="wait")
    await queue.insert(token.uuid)

    # Redis 리스트 확인
    items = await fake_redis.lrange(config.WAIT_QUEUE_KEY, 0, -1)
    assert token.uuid in items

    # 토큰 키 확인
    value = await fake_redis.get(config.TOKEN_PREFIX + token.uuid)
    assert value == "wait"

    # pop 후 반환 확인
    popped = await queue.pop()
    assert popped.uuid == token.uuid
    assert popped.status == "active"

@pytest.mark.asyncio
async def test_fifo_validate(fake_redis):
    queue = FIFOQueue(fake_redis)

    token = TokenResponse(uuid=str(uuid.uuid4()), status="wait")
    await queue.insert(token.uuid)

    is_valid = await queue.validate(token)
    assert is_valid is True

    # 잘못된 상태
    wrong_token = TokenResponse(uuid=token.uuid, status="active")
    is_valid_wrong = await queue.validate(wrong_token)
    assert is_valid_wrong is False


#### priority queue

@pytest.mark.asyncio
async def test_priority_insert_and_pop(fake_redis):
    queue = PriorityQueue(fake_redis)

    token1 = TokenResponse(uuid=str(uuid.uuid4()), status="wait")
    token2 = TokenResponse(uuid=str(uuid.uuid4()), status="wait")

    await queue.insert(token1)
    await asyncio.sleep(0.01)
    await queue.insert(token2)

    # zset에 들어갔는지 확인
    items = await fake_redis.zrange(config.WAIT_QUEUE_KEY, 0, -1)
    items = [item.decode() if isinstance(item, bytes) else item for item in items]
    assert token1.uuid in items
    assert token2.uuid in items

    # pop 수행 → 우선순위 가장 오래된(먼저 삽입한) token1
    popped = await queue.pop()
    assert isinstance(popped, TokenResponse)
    assert popped.uuid == token1.uuid

    # zset에서 제거됐는지 확인
    remaining = await fake_redis.zrange(config.WAIT_QUEUE_KEY, 0, -1)
    remaining = [item.decode() if isinstance(item, bytes) else item for item in remaining]
    assert token1.uuid not in remaining

@pytest.mark.asyncio
async def test_priority_validate(fake_redis):
    queue = PriorityQueue(fake_redis)

    token = TokenResponse(uuid=str(uuid.uuid4()), status="wait")
    await queue.insert(token)

    is_valid = await queue.validate(token)
    assert is_valid is True

    # 상태가 다르면 False
    wrong_token = TokenResponse(uuid=token.uuid, status="active")
    assert await queue.validate(wrong_token) is False