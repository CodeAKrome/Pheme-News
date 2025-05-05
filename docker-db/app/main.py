from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import json
from .db import db_manager
from .models import Record, VectorSearchQuery

app = FastAPI()

@app.post("/records/", response_model=List[Record])
async def create_records(jsonl_data: str):
    """
    Upload a JSONL feed (one JSON object per line), store in MongoDB, and add embeddings to Chroma.
    """
    try:
        # Split input by lines and parse each as JSON
        records = []
        for line in jsonl_data.splitlines():
            if line.strip():  # Skip empty lines
                record = json.loads(line)
                records.append(record)
        
        # Insert records into MongoDB and Chroma
        result = await db_manager.create_records(records)
        return result
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSONL format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/records/search/", response_model=List[Record])
async def search_records(**query: Any):
    """
    Search records by any field using query parameters.
    Example: /records/search/?name=John&age=30
    """
    try:
        # Build MongoDB query from query parameters
        mongo_query = {k: v for k, v in query.items() if v is not None}
        records = await db_manager.search_records(mongo_query)
        return records
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/records/vector-search/", response_model=List[Record])
async def vector_search(query: VectorSearchQuery):
    """
    Search Chroma vector DB with a query text and return corresponding MongoDB records.
    """
    try:
        # Search Chroma for similar records
        record_ids = await db_manager.vector_search(query.query_text, query.top_k)
        # Fetch records from MongoDB by IDs
        records = await db_manager.get_records_by_ids(record_ids)
        return records
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
