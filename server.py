from data_service import data_service
from db import DbClient
from pymongo import UpdateOne
from models import (
    ScheduleInfo,
    MatchPrediction,
    MatchInfo,
    MatchPredictionVariant,
    SCHEDULE_COLLECTION,
    PREDICTION_COLLECTION,
)
from utils import as_match_info
from flask import Flask, request
import json


app = Flask(__name__)


@app.post("/addPrediction")
def add_user_prediction():
    schedule = data_service.get_latest_schedule()

    if not schedule:
        return json.dumps(500)

    request_json = request.json

    if not request_json:
        return json.dumps(400)

    predictions = request_json["predictions"]
    user_id = request_json["user_id"]

    db_client = DbClient()
    db_connection = db_client.get_connection()
    db = db_connection.cluster0
    prediction_collection = db[PREDICTION_COLLECTION]

    write_requests = []

    for prediction in predictions:
        print(type(prediction))
        print(prediction)
        write_requests.append(
            UpdateOne(
                {"user_id": user_id},
                {"$set": {prediction.match_id: prediction.to_dict()}},
                upsert=True,
            )
        )
    prediction_collection.bulk_write(write_requests)
    return json.dumps(200)


def get_match_schedule() -> ScheduleInfo:
    db_client = DbClient()
    db_connection = db_client.get_connection()
    db = db_connection.cluster0
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

    db_client = DbClient()
    db_connection = db_client.get_connection()
    db = db_connection.cluster0
    schedule_collection = db[SCHEDULE_COLLECTION]

    for match in schedule.matches:
        result = schedule_collection.update_one(
            {"id": match.id, "is_completed": False}, {"$set": match.todict()}
        )


def get_missing_predictions(user_id: str):
    db_client = DbClient()
    db_connection = db_client.get_connection()
    db = db_connection.cluster0
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


if __name__ == "__main__":
    # app.run()
    get_missing_predictions("123")
