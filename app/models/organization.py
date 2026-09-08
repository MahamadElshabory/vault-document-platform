from sqlmodel import SQLModel, Field
from datetime import datetime


class Organization(SQLModel , table=True):
    __tablename__ = "organizations"
    id : int | None= Field(default=None, primary_key=True)
    name : str 
    created_at: datetime = Field(default_factory=datetime.now)
    