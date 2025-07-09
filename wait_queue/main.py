from fastapi import FastAPI, Request, Depends
import asyncio 
from contextlib import asynccontextmanager

from service.observer import get_observer
from service.monitor import get_monitor
from api import routers
from repository.redis_repo import get_redis, Redis
from api.limiter import rate_limiter_fixed

#서버 시작시 실행
@asynccontextmanager
async def lifespan(app: FastAPI):
    wait_observer = await get_observer()
    active_monitor = await get_monitor()
    asyncio.create_task(active_monitor.validate_active_count())
    asyncio.create_task(active_monitor.watch_key_expiration())
    asyncio.create_task(wait_observer.notify_loop())
    
    yield

## fastapi 실행
app = FastAPI(lifespan=lifespan)
for r in routers:
    app.include_router(r)



@app.get("/")
def main():
    return "main_page"



## rate limiting 테스트
@app.get("/limited/")
async def limited_endpoint(token:str, redis:Redis =Depends(get_redis)                           ):
    await rate_limiter_fixed(redis_client=redis,
                             uuid=token)

    return {"msg": "ok"}


## rate limiting 데코레이터 테스트.
## 미구현
# @app.get("/limited/")
# @rate_limiter_fixed(redis_client= Depends(get_redis), 
#                     limit=3, 
#                     window=10,
#                     key_func= lambda token: token  # Use token(uuid) as limiter key
#                     )
# async def limited_endpoint(token:str):


#     return {"msg": "ok"}




if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", reload=True, log_level="info")