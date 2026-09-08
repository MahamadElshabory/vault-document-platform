from sqlmodel import Session, select, text, text

from app.core.security import hash_password
from app.db import session
from app.models.organization import Organization
from app.models.user import User
from app.models.document import Document
from pypdf import PdfReader
import fitz
import pytesseract
from PIL import Image
import io



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
        
