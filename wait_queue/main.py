from fastapi import FastAPI, Request
import asyncio 
from contextlib import asynccontextmanager

from service.observer import get_observer
from service.monitor import get_monitor
from repository.redis_repo import init_redis
from api import routers

#서버 시작시 실행
@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_redis()
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





if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", reload=True, log_level="info")