from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class CVEBase(BaseModel):
    id: str
    date_published: Optional[datetime] = None
    date_updated: Optional[datetime] = None
    title: Optional[str] = None
    description: Optional[str] = None
    problem_types: Optional[List[dict]] = None


class CVECreate(CVEBase):
    pass


class CVEOut(CVEBase):
    date_published: Optional[datetime]
    date_updated: Optional[datetime]
    title: Optional[str] = None
    description: Optional[str] = None
    problem_types: Optional[List[dict]] = None
