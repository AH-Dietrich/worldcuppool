import os

from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


class DbClient:
    def __init__(self):
        self.connection = None

    def get_cluster_connection(self):
        return self.get_connection().cluster0

    def get_connection(self):
        if self.connection:
            return self.connection
        return self.connect()

    def connect(self) -> MongoClient:
        load_dotenv()

        uri = f"mongodb+srv://{os.getenv('MONGO_DB_USER')}:{os.getenv('MONGO_DB_PASS')}@cluster0.nersjol.mongodb.net/?appName=Cluster0"
        client = MongoClient(uri, server_api=ServerApi("1"))
        self.connection = client
        return client
