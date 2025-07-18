from fastapi import FastAPI
from celery_worker import task_1, celery_app

app = FastAPI()



@app.get("/")
def root():
    return {"message": "Hello, Celery"}

## simple celery 
@app.get("/add/{a}/{b}")
def run_add(a: int, b: int):
    task = task_1.delay(a, b)
    return {"task_id": task.id}

@app.get("/result/{task_id}")
def get_result(task_id: str):
    result = celery_app.AsyncResult(task_id)
    if result.ready():
        return {"status": "done", "result": result.result}
    return {"status": "pending"}



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", reload=True, log_level="info")