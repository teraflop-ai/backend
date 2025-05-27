from fastapi import Depends
from typing import Annotated
from app.core.users import get_current_user
from app.schemas.users import User

CurrentUser = Annotated[User, Depends(get_current_user)]