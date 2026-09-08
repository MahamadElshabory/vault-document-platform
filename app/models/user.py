from sqlmodel import SQLModel, Field
from datetime import datetime
from uuid import uuid4


class User(SQLModel , table = True) :
    __tablename__ = "users"
    id: str = Field(default_factory=lambda: str(uuid4()),primary_key=True)
    name : str
    email : str = Field(unique=True, index=True)
    hashed_password : str
    org_id : int = Field(foreign_key="organizations.id")
    created_at : datetime = Field(default_factory=datetime.now)