import json
from os import environ as env
import jwt

from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from flask import Flask, redirect, request, session, url_for
from pymongo import UpdateOne

from authlib.integrations.flask_oauth2 import ResourceProtector
from validator import Auth0JWTBearerTokenValidator


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


require_auth = ResourceProtector()
validator = Auth0JWTBearerTokenValidator(
    env.get("AUTH0_DOMAIN"), env.get("API_IDENTIFIER")
)
require_auth.register_token_validator(validator)

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


@app.route("/")
def home():
    return json.dumps(200)


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
    request_json = request.json

    if not request_json:
        return json.dumps(400)

    token = session.get("user")

    if not token:
        return json.dumps(403)

    predictions = request_json["predictions"]
    user_id = token.get("userinfo", {}).get("sub", "")

    if not user_id:
        return json.dumps(500)

    prediction_collection = db[PREDICTION_COLLECTION]

    write_requests = []

    for prediction in predictions:
        # ToDo check if prediction id is a valid one in the schedule
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


def update_match_schedule():
    schedule = data_service.get_latest_schedule()

    if not schedule:
        return

    schedule_collection = db[SCHEDULE_COLLECTION]

    for match in schedule.matches:
        schedule_collection.update_one(
            {"id": match.id, "is_completed": False},
            {"$set": match.todict()},
            upsert=True,
        )


@app.get("/api/getPredictions")
@require_auth(None)
def get_missing_predictions():
    token = require_auth.acquire_token()
    prediction_collection = db[PREDICTION_COLLECTION]

    user_doc = prediction_collection.find_one({"user_id": token["sub"]})

    if not user_doc:
        return json.dumps(404)

    prediction_ids = set(m["id"] for m in user_doc.get("predictions", []))

    schedule_collection = db[SCHEDULE_COLLECTION]
    schedule_cursor = schedule_collection.find(
        {
            "is_completed": False,
            "home.is_placeholder": False,
            "away.is_placeholder": False,
        },
        {
            "_id": False,
            "is_completed": False,
            "home.is_placeholder": False,
            "home.score": False,
            "away.is_placeholder": False,
            "away.score": False,
            "data.match_length": False,
            "data.stage": False,
        },
    )
    matches = schedule_cursor.to_list()
    match_ids = set(m["id"] for m in matches)

    needed_ids = match_ids - prediction_ids

    match_info = []
    for match in matches:
        if match["id"] in needed_ids:
            match_info.append(match)

    return json.dumps(match_info, default=str)


def save_user_info(token: dict) -> bool:
    user_id = token.get("userinfo", {}).get("sub", "")

    if not user_id:
        return False

    user_collection = db[USER_COLLECTION]
    prediction_collection = db[PREDICTION_COLLECTION]

    user_info = token.get("userinfo", {})
    user_doc = user_collection.find_one({"user_id": user_id})

    if user_doc:
        return False

    user_collection.update_one({"user_id": user_id}, {"$set": user_info}, upsert=True)
    prediction_collection.insert_one({"user_id": user_id})

    return True


if __name__ == "__main__":
    update_match_schedule()
    app.run(port=5001)
