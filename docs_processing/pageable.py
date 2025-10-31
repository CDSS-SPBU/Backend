from pydantic import BaseModel
from typing import List, Any


class Pageable(BaseModel):
    page: int = 0
    size: int = 10


class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    pageable: Pageable
    total_pages: int
