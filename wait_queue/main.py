from fastapi import FastAPI
from api import routers



app = FastAPI()
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