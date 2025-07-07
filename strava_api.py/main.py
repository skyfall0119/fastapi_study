from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, JSONResponse
from strava import get_authorize_url, exchange_code_for_token, get_activities, get_activity_streams

app = FastAPI()

access_token_store = {}

@app.get("/")
def root():
    return {"message": "Strava OAuth Test. Visit /auth/strava to begin."}

@app.get("/auth/strava")
def auth_strava():
    url = get_authorize_url()
    return RedirectResponse(url)

@app.get("/auth/strava/callback")
def auth_callback(code: str):
    token_data = exchange_code_for_token(code)
    access_token = token_data.get("access_token")
    access_token_store["access_token"] = access_token
    activities = get_activities(access_token)

    return JSONResponse(content={"token": token_data, "activities": activities})


@app.get("/activity/{activity_id}/stream")
def get_activity_stream(activity_id: int):
    res = get_activity_streams(access_token_store['access_token'],
                               activity_id)

    return JSONResponse(content={"result": res})

