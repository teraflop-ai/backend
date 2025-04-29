import asyncpg
from fastapi import Depends
from typing import Annotated
from app.database.db import create_client

Client = Annotated[asyncpg.Pool | asyncpg.Connection, Depends(create_client)]