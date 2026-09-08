from fastapi import APIRouter, Depends, HTTPException, UploadFile, status, File
from sqlmodel import Session
from app.models.document import Document
from app.tasks.document_tasks import process_document
from app.api.services.document_service import DocumentService 
from app.db.session import get_db
from app.models import user
from app.schemas.auth import UserSignUp , UserLogin , TokenResponse
from app.models.organization import Organization 
from app.models.user import User
from app.api.services.user_service import UserService
from app.core.security import create_access_token, verify_password 
from app.api.dependencies import get_current_user, require_org_scope
from pathlib import Path
from uuid import uuid4
import shutil

router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)

document_service = DocumentService()


UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload")
def upload_document(current_user : User = Depends(get_current_user) , file : UploadFile = File(...) , session: Session = Depends(get_db)):
    
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed"
        )
    
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only PDF files are allowed."
        )
        
    original_filename = Path(file.filename).name

    stored_filename = f"{uuid4().hex}_{original_filename}"

    file_path = UPLOAD_DIR / stored_filename

    with file_path.open("wb") as saved_file:
      shutil.copyfileobj(file.file, saved_file)       
      
      
    document = document_service.create_document(org_id=current_user.org_id, filename=file.filename, storage_ref=str(file_path), session=session)
    
    process_document.delay(document.id)
    return {
        "document_id": document.id,
        "filename": document.filename,
        "status": document.status
    }
    
    
    
@router.get("/{document_id}/text")
def get_document_text(document_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(get_db)):
    
    document = session.get(Document, document_id)
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    if document.org_id != current_user.org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access to this document is forbidden"
        )
            
    storage_ref = document.storage_ref
    text = document_service.extract_pdf_text(storage_ref=storage_ref)
    
    chunks = document_service.chunk_text(text=text, chunk_size=1000, overlap=200)
    
    return{
        "document_id": document.id,
        "chunks_count" : len(chunks),
        "chunks" : chunks
    }