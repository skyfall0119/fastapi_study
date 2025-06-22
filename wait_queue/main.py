from fastapi import FastAPI
import asyncio 
from contextlib import asynccontextmanager

from service.observer import get_observer
from service.monitor import get_monitor
from api import routers


#서버 시작시 실행
@asynccontextmanager
async def lifespan(app: FastAPI):
    wait_observer = await get_observer()
    active_monitor = await get_monitor()
    asyncio.create_task(active_monitor.validate_active_count())
    asyncio.create_task(wait_observer.notify_loop())
    
    yield

## fastapi 실행
app = FastAPI(lifespan=lifespan)
app.include_router(routers)



@app.get("/")
def main():
    return "main_page"

@app.get("/func1")
def main():
    return "test page for token"
@app.get("/func1")
def main():
    return "test page for token"




if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app")