from msgspec import Struct
from typing import List, Union


class TextInput(Struct):
    input: Union[str, List[str]]


class EmbeddingResponse(Struct):
    embedding: List[float]
