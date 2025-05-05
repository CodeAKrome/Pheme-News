from motor.motor_asyncio import AsyncIOMotorClient
from .models import Record
from typing import List, Dict, Any
import chromadb
from chromadb.utils import embedding_functions
from bson import ObjectId
import json

class DBManager:
    def __init__(self, mongo_uri: str, database_name: str, chroma_host: str, chroma_port: int):
        # MongoDB setup
        self.mongo_client = AsyncIOMotorClient(mongo_uri)
        self.db = self.mongo_client[database_name]
        self.collection = self.db["records"]
        
        # Chroma setup
        self.chroma_client = chromadb.HttpClient(host=chroma_host, port=chroma_port)
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        self.chroma_collection = self.chroma_client.get_or_create_collection(
            name="records",
            embedding_function=self.embedding_function
        )

    def _json_to_text(self, record: Dict) -> str:
        """
        Convert a JSON record to a text string for embedding.
        """
        return " ".join([f"{k}:{v}" for k, v in record.items()])

    async def create_records(self, records: List[Dict]) -> List[Record]:
        """
        Insert records into MongoDB and add embeddings to Chroma.
        """
        # Insert into MongoDB
        mongo_result = await self.collection.insert_many(records)
        inserted_ids = mongo_result.inserted_ids

        # Prepare data for Chroma
        documents = [self._json_to_text(record) for record in records]
        chroma_ids = [str(obj_id) for obj_id in inserted_ids]
        metadatas = [{"mongo_id": str(obj_id)} for obj_id in inserted_ids]

        # Add to Chroma
        self.chroma_collection.add(
            documents=documents,
            ids=chroma_ids,
            metadatas=metadatas
        )

        # Fetch inserted records from MongoDB to return
        inserted_records = []
        for obj_id in inserted_ids:
            record = await self.collection.find_one({"_id": obj_id})
            record["id"] = str(record["_id"])
            del record["_id"]
            inserted_records.append(Record(**record))
        return inserted_records

    async def search_records(self, query: Dict) -> List[Record]:
        """
        Search records in MongoDB based on query parameters.
        """
        records = []
        cursor = self.collection.find(query)
        async for record in cursor:
            record["id"] = str(record["_id"])
            del record["_id"]
            records.append(Record(**record))
        return records

    async def vector_search(self, query_text: str, top_k: int = 5) -> List[str]:
        """
        Search Chroma for similar records and return their MongoDB IDs.
        """
        results = self.chroma_collection.query(
            query_texts=[query_text],
            n_results=top_k
        )
        return results["ids"][0]  # List of Chroma IDs (MongoDB _id strings)

    async def get_records_by_ids(self, record_ids: List[str]) -> List[Record]:
        """
        Fetch MongoDB records by their IDs.
        """
        records = []
        for id_str in record_ids:
            record = await self.collection.find_one({"_id": ObjectId(id_str)})
            if record:
                record["id"] = str(record["_id"])
                del record["_id"]
                records.append(Record(**record))
        return records

# Initialize DBManager with MongoDB and Chroma connections
db_manager = DBManager(
    mongo_uri="mongodb://mongodb:27017",
    database_name="json_db",
    chroma_host="chroma",
    chroma_port=8000
)
