import datetime

import pymongo
from bson import ObjectId

from product.backend.models.config import Config
from product.backend.models.exceptions import ResourceNotFound
from product.backend.models.models import InferResponse, TrainResult
from product.backend.models.singelton import Singleton


class MongoManager(metaclass=Singleton):
    INFERENCES = "inferences"
    MODELS = "models"

    def __init__(self):
        self.client = self._get_dataset()

    @staticmethod
    def _get_dataset():
        config = Config()
        client = pymongo.MongoClient(config.mongo_connection_string)
        return client[config.mongo_db_name]

    def add_inference(self, data: dict):
        self.client.get_collection("inferences").insert_one(data)

    def add_model(self, retrain_result: TrainResult) -> str:
        data = retrain_result.dict(exclude_none=True)
        data["created_at"] = datetime.datetime.now()
        result = self.client.get_collection("models").insert_one(data)
        return str(result.inserted_id)

    @staticmethod
    def parse_result(mongo_result: list) -> list:
        result = []
        for elem in mongo_result:
            curr_id = elem.pop("_id")
            result.append(dict(id=str(curr_id), **elem))
        return result

    def get_models(self):
        return self.parse_result(
            list(self.client.get_collection("models").find())
        )

    def get_inferences(self):
        return self.parse_result(
            list(self.client.get_collection("inferences").find())
        )

    def get_model_by_id(self, model_id: str) -> str:
        model_res = self.client.get_collection("models").find_one(
            {"_id": ObjectId(model_id)}
        )
        if not model_res:
            raise ResourceNotFound(f"model with id {model_id} not found")
        return model_res["model_name"]
