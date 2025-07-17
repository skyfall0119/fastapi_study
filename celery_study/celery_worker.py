import time
from celery import Celery
import config

celery_app = Celery(
    "worker",
    broker=f"redis://{config.REDIS_HOST}:{config.REDIS_PORT}",
    backend=f"redis://{config.REDIS_HOST}:{config.REDIS_PORT}",
    # broker=f"redis://localhose:6379",
    # backend=f"redis://localhose:6379",
)



@celery_app.task
def task_1(x,y):
    time.sleep(10)
    return x+y