from fastapi import Depends
from typing import Annotated
from app.core.users import get_current_user

# CurrentUSER = Annotated[, Depends(get_current_user)]