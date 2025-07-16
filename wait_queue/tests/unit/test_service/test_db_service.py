import pytest
from service.db_service import DbService
from model.models import TokenResponse
import pytest_asyncio
from utils import config, util


@pytest.mark.asyncio
async def test_create_token_adds_to_queue(fake_redis):
    db = DbService(redis=fake_redis)

    # jwt 토큰 생성
    token = await db.create_token()
    assert isinstance(token, str)
    decoded = TokenResponse(**util.decode_token(token))

    # 대기열에 들어갔는지 확인
    queue = await fake_redis.lrange(config.WAIT_QUEUE_KEY, 0, -1)
    assert decoded.uuid in queue

    # Redis key로 저장됐는지도 확인
    token_key = config.TOKEN_PREFIX + decoded.uuid
    val = await fake_redis.get(token_key)
    assert val == config.TOKEN_WAIT


@pytest.mark.asyncio
async def test_promote_to_active_moves_token(fake_redis):
    db = DbService(redis=fake_redis)

    # 1. 생성
    token = await db.create_token()
    decoded = TokenResponse(**util.decode_token(token))
    # 2. promote
    promoted_token = await db.promote_to_active()

    assert promoted_token.uuid == decoded.uuid
    assert promoted_token.status == config.TOKEN_ACTIVE

    # 3. active_list에 있는지 확인
    in_set = await fake_redis.sismember(config.ACTIVE_SET_KEY, decoded.uuid)
    assert in_set == 1
