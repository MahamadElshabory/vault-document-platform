from sqlmodel import Enum, SQLModel, Field
from datetime import datetime



class DocumentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


class Document(SQLModel , table = True):
    
    __tablename__ = "documents"
    id : int | None = Field(default=None , primary_key=True)
    org_id : int = Field(foreign_key="organizations.id")
    filename : str
    storage_ref : str
    status : str = Field(default="pending")
    error : str | None = Field(default=None)