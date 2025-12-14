from schedule_fetcher import data_service
from db import DbClient
from models import User, ScheduleInfo, MatchPrediction, MatchPredictionVariant
import asyncio

SCHEDULE_COLLECTION = "schedule2026_test"
PREDICTION_COLLECTION = "2026_predictions"


async def populate_schedule_collection():
    db_client = DbClient()
    db_connection = await db_client.get_connection()
    db = db_connection.cluster0

    my_collection = db[SCHEDULE_COLLECTION]
    my_collection.drop()

    schedule = data_service.get_latest_schedule()

    for game in schedule.matches:
        my_collection.insert_one(game.todict())


# add user prediction
# update schedule data
# populate schedule data
async def add_user_prediction(user_id: str, prediction: MatchPrediction):
    schedule = data_service.get_latest_schedule()

    if not schedule:
        return

    db_client = DbClient()
    db_connection = await db_client.get_connection()
    db = db_connection.cluster0
    prediction_collection = db[PREDICTION_COLLECTION]

    result = prediction_collection.update_one(
        {"user_id": user_id},
        {"$set": {prediction.match_id: prediction.to_dict()}},
        upsert=True,
    )


async def get_match_schedule() -> ScheduleInfo:
    db_client = DbClient()
    db_connection = await db_client.get_connection()
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
    db_connection = await db_client.get_connection()
    db = db_connection.cluster0
    schedule_collection = db[SCHEDULE_COLLECTION]

    # ToDo add some field to know we don't need to update a field anymore
    for match in schedule.matches:
        result = schedule_collection.update_one(
            {"id": match.id, "is_completed": False}, {"$set": match.todict()}
        )


if __name__ == "__main__":
    # test1()
    asyncio.run(
        add_user_prediction(
            "232", MatchPrediction(1, 2, "test", MatchPredictionVariant.GENERAL)
        )
    )
