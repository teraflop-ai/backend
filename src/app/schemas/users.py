from pydantic import BaseModel

class User(BaseModel):
    id: str
    email: str
    credits: int
    google_id: str | None = None