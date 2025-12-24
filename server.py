import json
from os import environ as env

from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from flask import Flask, redirect, request, session, url_for
from pymongo import UpdateOne

from data_service import data_service
from db import DbClient
from models import (
    PREDICTION_COLLECTION,
    SCHEDULE_COLLECTION,
    USER_COLLECTION,
    MatchInfo,
    ScheduleInfo,
)
from utils import as_match_info

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)


app = Flask(__name__)
app.secret_key = env.get("APP_SECRET_KEY")

oauth = OAuth(app)

oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration',
)

db_client = DbClient()
db = db_client.get_cluster_connection()


@app.route("/login")
def login():
    if not oauth.auth0:
        return json.dumps(500)
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )


@app.route("/callback", methods=["GET", "POST"])
def callback():
    if not oauth.auth0:
        return json.dumps(500)
    token = oauth.auth0.authorize_access_token()

    save_user_info(token)
    session["user"] = token

    return redirect("/")


@app.post("/addPrediction")
def add_user_prediction():
    token = session.get("user")

    if not token:
        return json.dumps(403)

    request_json = request.json

    if not request_json:
        return json.dumps(400)

    predictions = request_json["predictions"]
    user_id = token.get("userinfo", {}).get("sub", "")

    if not user_id:
        return json.dumps(500)

    prediction_collection = db[PREDICTION_COLLECTION]

    write_requests = []

    for prediction in predictions:
        write_requests.append(
            UpdateOne(
                {"user_id": user_id},
                {"$push": {"predictions": prediction}},
            )
        )
    prediction_collection.bulk_write(write_requests)
    return json.dumps(200)


def get_match_schedule() -> ScheduleInfo:
    schedule_collection = db[SCHEDULE_COLLECTION]

    schedule = schedule_collection.find({}, {"_id": False})
    matches: list[MatchInfo] = []

    for match in schedule:
        matches.append(as_match_info(match))

    return ScheduleInfo(matches)


async def update_match_schedule():
    schedule = data_service.get_latest_schedule()

    if not schedule:
        return

    schedule_collection = db[SCHEDULE_COLLECTION]

    for match in schedule.matches:
        schedule_collection.update_one(
            {"id": match.id, "is_completed": False}, {"$set": match.todict()}
        )


def get_missing_predictions(user_id: str):
    prediction_collection = db[PREDICTION_COLLECTION]

    user_doc = prediction_collection.find_one({"user_id": user_id})

    if not user_doc:
        return

    prediction_ids = set(m["id"] for m in user_doc["predictions"])

    schedule_collection = db[SCHEDULE_COLLECTION]
    schedule_cursor = schedule_collection.find(
        {
            "is_completed": False,
            "home.is_placeholder": False,
            "away.is_placeholder": False,
        },
        {"id": True, "_id": False},
    )
    match_ids = schedule_cursor.to_list()
    match_ids = set(m["id"] for m in match_ids)

    return match_ids - prediction_ids


def save_user_info(token: dict):
    user_id = token.get("userinfo", {}).get("sub", "")

    if not user_id:
        return

    user_info = token.get("userinfo", {})

    user_collection = db[USER_COLLECTION]
    prediction_collection = db[PREDICTION_COLLECTION]

    user_collection.update_one({"user_id": user_id}, {"$set": user_info}, upsert=True)
    prediction_collection.insert_one({"user_id": user_id})


if __name__ == "__main__":
    app.run(port=5001)
