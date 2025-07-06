from fastapi import Request, HTTPException
import time
from utils import config
from redis.asyncio import Redis


"""
rate limiting (fixed window)
고정 시간 윈도우 동안 요청 수 제한
1. 모든 api 콜은 redis 의 유저키에 카운트됨.
2. 첫 api 콜이라면 만료시간이 설정됨.
3. 만료 되기 전 유저키에 카운트 된 횟수가 제한을 넘긴다면 exception 

구현 간단.
"""
def fixed_rate_limiter(redis_client:Redis, 
                 uuid: str, 
                 limit:int=config.RATE_LIMIT,
                 window:int=config.RATE_WINDOW):
    key = config.RATE_PREFIX + uuid
    current = redis_client.incr(key)
    if current == 1: # 첫 api 콜이면 만료 설정
        redis_client.expire(key, window)
    if current > limit: # api 콜이 일정 횟수 넘어가면 exception
        raise HTTPException(status_code=429, detail="Too many requests")



"""
rate limiting (sliding window)
해당 시간 윈도우 동안 요청 수 제한. 
1. 키 값에 현재 시간 추가 (zadd)
2. zremrangebyscore 을 사용해 현재 윈도우에서 벗어난 값들 제거
3. 키 값에 남아있는 값 카운트 (zcard)
4. 만료 시간 재설정 (여유시간 + 10초) 
    -> TTL 만료를 윈도우와 딱 맞게 설정하면 엣지케이스에서 오류 발생 가능
    
"""
def sliding_window_rate_limiter(redis_client:Redis, 
                                uuid: str, 
                                limit: int = config.RATE_LIMIT, 
                                window_sec: int = config.RATE_WINDOW):
    now = int(time.time() * 1000)
    key = config.RATE_PREFIX + uuid
    window_start = now - (window_sec * 1000)

    pipe = redis_client.pipeline()  # 여러 쿼리 파이프라인 실행
    pipe.zadd(key, {str(now): now})  # score 값을 현재 시간으로 (밀리초)
    pipe.zremrangebyscore(key, 0, window_start) 
    pipe.zcard(key)  
    pipe.expire(key, window_sec + 10) # 여유
    _, _, count, _ = pipe.execute()  # 파이프라인 결과값 (zadd, zrem~, zcard, expire)

    if count > limit:
        raise HTTPException(status_code=429, detail="Too Many Requests")
    

"""
토큰 버킷 방식
1. 현재 시각(now)과 마지막 충전 시각(last_ts)의 차이 계산
2. 경과 시간에 비례해서 토큰 보충
3. 버킷이 비었는지 확인
4. 토큰이 있다면 1개 소비하고 요청 처리
5. Redis에 상태 갱신

"""

def token_bucket_rate_limiter(
    redis_client:Redis,
    uuid: str,
    refill_rate: float,   # 초당 몇 개 충전
    capacity: int         # 버킷 최대 토큰 수
):
    key_tokens = f"{config.RATE_PREFIX}{uuid}:tokens"
    key_last_ts = f"{config.RATE_PREFIX}{uuid}:last"

    now = time.time()

    # Redis 파이프라인으로 원자적 처리
    pipe = redis_client.pipeline()
    pipe.get(key_tokens)
    pipe.get(key_last_ts)
    tokens_str, last_ts_str = pipe.execute()

    # 현재 상태 로딩
    tokens = float(tokens_str) if tokens_str else capacity
    last_ts = float(last_ts_str) if last_ts_str else now

    # 경과 시간만큼 토큰 충전
    elapsed = now - last_ts
    refill = elapsed * refill_rate
    tokens = min(capacity, tokens + refill)

    if tokens < 1:
        raise HTTPException(status_code=429, detail="Too Many Requests")

    # 요청 처리: 토큰 1개 소비
    tokens -= 1

    # Redis에 상태 저장
    pipe = redis_client.pipeline()
    pipe.set(key_tokens, tokens)
    pipe.set(key_last_ts, now)
    pipe.expire(key_tokens, int(capacity / refill_rate) + 10)
    pipe.expire(key_last_ts, int(capacity / refill_rate) + 10)
    pipe.execute()