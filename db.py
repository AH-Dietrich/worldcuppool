import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv


class DbClient:
    def __init__(self):
        self.connection = None

    async def get_connection(self):
        if self.connection:
            return self.connection
        return await self.connect()

    async def connect(self) -> MongoClient:
        load_dotenv()

        uri = f"mongodb+srv://{os.getenv('MONGO_DB_USER')}:{os.getenv('MONGO_DB_PASS')}@cluster0.nersjol.mongodb.net/?appName=Cluster0"
        client = MongoClient(uri, server_api=ServerApi("1"))
        self.connection = client
        return client
