from msgspec import Struct
from typing import List, Union
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Union

class TextInput(BaseModel):
    input: str = Field(..., description="The input text to embed")
    model: str = Field(..., description="The model to use for embedding")

class EmbeddingResponse(BaseModel):
    embedding: List[float] = Field(..., description="The embedding vector")
    model: str = Field(..., description="The model used")
    usage: Dict[str, int] = Field(..., description="Token usage information")
    