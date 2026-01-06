from backend.data_service import data_service
from backend.db import DbClient
from backend.models import PREDICTION_COLLECTION, SCHEDULE_COLLECTION


def populate_schedule_collection():
    db_client = DbClient()
    db_connection = db_client.get_connection()
    db = db_connection.cluster0

    my_collection = db[SCHEDULE_COLLECTION]
    my_collection.drop()

    schedule = data_service.get_latest_schedule()

    for game in schedule.matches:
        my_collection.insert_one(game.todict())


def populate_fake_user_prediction():
    db_client = DbClient()
    db_connection = db_client.get_connection()
    db = db_connection.cluster0

    prediction_collection = db[PREDICTION_COLLECTION]
    prediction_collection.drop()

    prediction_doc = {
        "user_id": "123",
        "predictions": [
            {"id": 400021455, "home": 0, "away": 0},
            {"id": 400021444, "home": 1, "away": 1},
            {"id": 400021511, "home": 2, "away": 2},
            {"id": 400021529, "home": 3, "away": 3},
        ],
    }

    prediction_collection.insert_one(prediction_doc)


populate_schedule_collection()
populate_fake_user_prediction()
