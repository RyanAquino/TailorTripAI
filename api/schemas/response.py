from typing import Any, Optional

from pydantic import BaseModel


class ResponseSchema(BaseModel):
    data: Optional[Any]
