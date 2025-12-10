from schedule_fetcher import data_service
from db import DbClient
import asyncio

def test1():
  schedule = data_service.get_latest_schedule()

  print(schedule.matches[0].__dict__)

async def test():
  db_client = DbClient()
  db_connection = await db_client.get_connection()
  db = db_connection.cluster0
  my_collection = db['schedule2026_test']
  my_collection.drop()

  schedule = data_service.get_latest_schedule()
  
  for game in schedule.matches:
    my_collection.insert_one(game.todict())



if __name__ == '__main__':
  # test1()
  asyncio.run(test())