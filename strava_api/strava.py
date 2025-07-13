import os
import requests
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
REDIRECT_URI = os.getenv("STRAVA_REDIRECT_URI")

AUTH_URL = "https://www.strava.com/oauth/authorize"
TOKEN_URL = "https://www.strava.com/oauth/token"
API_URL = "https://www.strava.com/api/v3/"
ACTIVITIES = "athlete/activities"  # List Athlete Activities (getLoggedInAthleteActivities)
STREAM_URL = "activities/id/streams"

def get_authorize_url():
    return (
        f"{AUTH_URL}?client_id={CLIENT_ID}"
        f"&response_type=code"
        f"&redirect_uri={REDIRECT_URI}"
        f"&approval_prompt=auto"
        f"&scope=read,activity:read_all"
    )

def exchange_code_for_token(code: str):
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code"
    }
    response = requests.post(TOKEN_URL, data=payload)
    response.raise_for_status()
    return response.json()

def get_activities(access_token: str):
    headers = {"Authorization": f"Bearer {access_token}"}
    url = API_URL + ACTIVITIES
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def get_activity_streams(access_token: str, id):
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {
        "keys": "heartrate,watts,cadence,distance,velocity_smooth,time",
        "key_by_type": "true"
    }
    url = API_URL + f"activities/{id}/streams"
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()


# stream set
# time
# TimeStream	An instance of TimeStream.
# distance
# DistanceStream	An instance of DistanceStream.
# latlng
# LatLngStream	An instance of LatLngStream.
# altitude
# AltitudeStream	An instance of AltitudeStream.
# velocity_smooth
# SmoothVelocityStream	An instance of SmoothVelocityStream.
# heartrate
# HeartrateStream	An instance of HeartrateStream.
# cadence
# CadenceStream	An instance of CadenceStream.
# watts
# PowerStream	An instance of PowerStream.
# temp
# TemperatureStream	An instance of TemperatureStream.
# moving
# MovingStream	An instance of MovingStream.
# grade_smooth
# SmoothGradeStream	An instance of SmoothGradeStream.
