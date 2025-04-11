from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime

class Startup(BaseModel):
    id: Optional[str] = None
    name: str
    website: Optional[str] = None
    description: Optional[str] = None
    founded_year: Optional[Union[int, str]] = None
    headquarters: Optional[str] = None
    industry: Optional[List[str]] = None
    funding: Optional[Dict[str, Any]] = None
    founders: Optional[List[str]] = None
    employees_count: Optional[int] = None
    products: Optional[List[str]] = None
    social_media: Optional[Dict[str, str]] = None
    news: Optional[List[Dict[str, Any]]] = None
    last_updated: datetime = Field(default_factory=datetime.now)