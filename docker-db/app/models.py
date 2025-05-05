from pydantic import BaseModel
from typing import Any, Optional

class Record(BaseModel):
    id: Optional[str] = None
    data: Any  # Allow any JSON-compatible data

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class VectorSearchQuery(BaseModel):
    query_text: str
    top_k: int = 5
