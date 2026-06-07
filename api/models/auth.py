from pydantic import BaseModel
from typing import List, Optional


class ApiKey(BaseModel):
    key_id: str
    name: str
    created_at: str
    expires_at: Optional[str] = None
    rate_limit: int
    scopes: List[str]
    last_used: Optional[str] = None
    is_active: bool = True
