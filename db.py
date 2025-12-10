import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv

class DbClient:
    async def get_connection(self):
      return await self.connect()
            
    async def connect(self) -> MongoClient:
        load_dotenv()

        uri = f"mongodb+srv://dietrichanaya_db_user:{os.getenv('MONGO_DB_PASS')}@cluster0.nersjol.mongodb.net/?appName=Cluster0"
        client = MongoClient(uri, server_api=ServerApi('1'))
        return client