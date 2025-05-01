import asyncpg
from fastapi import Depends
from typing import Annotated
from app.database.db import get_db

AsyncDB = Annotated[asyncpg.Pool | asyncpg.Connection, Depends(get_db)]