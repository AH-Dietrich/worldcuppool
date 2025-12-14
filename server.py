from data_service import data_service
from db import DbClient
from pymongo import UpdateOne
from models import (
    ScheduleInfo,
    MatchPrediction,
    MatchPredictionVariant,
    SCHEDULE_COLLECTION,
    PREDICTION_COLLECTION,
)
from flask import Flask, request
import json


app = Flask(__name__)


async def populate_schedule_collection():
    db_client = DbClient()
    db_connection = db_client.get_connection()
    db = db_connection.cluster0

    my_collection = db[SCHEDULE_COLLECTION]
    my_collection.drop()

    schedule = data_service.get_latest_schedule()

    for game in schedule.matches:
        my_collection.insert_one(game.todict())


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
    matches = schedule.to_list()
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


if __name__ == "__main__":
    # app.run()
    get_match_schedule()
