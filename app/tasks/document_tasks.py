from sqlmodel import Session

from app.core.celery_app import celery_app
from app.db.session import engine
from app.models.organization import Organization
from app.models.document import Document, DocumentStatus


@celery_app.task()
def process_document(document_id: int):
    
    with Session(engine) as session:
        
        document = session.get(Document, document_id)
        
        if document is None:
            return {
                "document_id": document_id,
                "status": "not_found"
            }
            
        document.status = DocumentStatus.PROCESSING
        
        session.add(document)
        session.commit()
        session.refresh(document)
        
        return {
            "document_id": document.id,
            "status": document.status
        }