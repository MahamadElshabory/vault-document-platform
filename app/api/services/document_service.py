from sqlmodel import Session, select, text, text
from app.core.metrics import (ingestion_duration,ingestion_failures,)
from time import perf_counter
from app.api.services.embedding_service import EmbeddingService
from app.api.services.vector_service import VectorService
from app.core.security import hash_password
from app.db import session
from app.models import document
from app.models import document
from app.models.organization import Organization
from app.models.user import User
from app.models.document import Document
from pypdf import PdfReader
import fitz
import pytesseract
from PIL import Image
import io


embedding_service = EmbeddingService()
vector_service = VectorService()

class DocumentService :
    
    def create_document( self, org_id : int , filename : str , storage_ref : str , session : Session):
        
        document = Document(
            
            org_id = org_id,
            filename = filename,
            storage_ref = storage_ref
        )
        
        session.add(document)
        session.commit()
        session.refresh(document)
        
        return document
    
    
    def extract_pdf_text(self, storage_ref: str):

        try :
            reader = PdfReader(storage_ref)

        except Exception :
            raise ValueError("Invalid PDF file")

        pdf_for_ocr = fitz.open(storage_ref)

        text = ""

        for page_number, page in enumerate(reader.pages):

            page_text = page.extract_text()

            if page_text and page_text.strip():

                text += page_text + "\n"

            else:

                pdf_page = pdf_for_ocr[page_number]

                pix = pdf_page.get_pixmap()

                image = Image.open(
                    io.BytesIO(pix.tobytes("png"))
                )

                ocr_text = pytesseract.image_to_string(image)

                text += ocr_text + "\n"

        pdf_for_ocr.close()

        if not text.strip():
            raise ValueError(
                "No extractable text found in PDF"
        )

        return text
    
    
    
    
    def chunk_text(self, text: str, chunk_size: int = 200, overlap: int = 40):

        words = text.split()

        chunks = []

        if overlap >= chunk_size:
          raise ValueError()
      
        step = chunk_size - overlap

        for start in range(0, len(words), step):

            end = start + chunk_size

            chunk_words = words[start:end]

            if not chunk_words:
                break

            chunk = " ".join(chunk_words)

            chunks.append(chunk)

        return chunks 
        
        
    def document_process(self, document: Document, session: Session):

        start_time = perf_counter()
        
        try:
            document.status = "processing"
            session.add(document)
            session.commit()


            text = self.extract_pdf_text(
                storage_ref=document.storage_ref
            )

            chunks = self.chunk_text(
                text=text,
                chunk_size=1000,
                overlap=200
            )


            for index, chunk in enumerate(chunks):

                vector = embedding_service.create_embedding(
                    text=chunk
                )

                vector_service.store_vector(
                    vector=vector,
                    document_id=document.id,
                    org_id=document.org_id,
                    chunk_index=index,
                    text=chunk
                )


            document.status = "completed"
            session.add(document)
            session.commit()
            session.refresh(document)


        except Exception as e:
            
            ingestion_failures.inc()

            document.status = "failed"
            document.error = str(e)

            session.add(document)
            session.commit()

            raise e
    
        finally:
            duration = perf_counter() - start_time

            ingestion_duration.observe(duration)