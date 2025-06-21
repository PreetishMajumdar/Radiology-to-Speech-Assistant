# Enhanced PDF text extraction with OCR support
# Add this to your app.py or create a separate utils/pdf_processor.py

import os
import fitz  # PyMuPDF
from PIL import Image
import io
import tempfile

def extract_text_from_file_enhanced(file_path):
    """
    Enhanced text extraction with OCR support for image-based PDFs.
    """
    extension = file_path.rsplit('.', 1)[1].lower()
    
    try:
        if extension == 'txt':
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read().strip()
                if not text:
                    raise ValueError("Text file appears to be empty")
                return text
                
        elif extension == 'pdf':
            return extract_pdf_text_with_ocr(file_path)
            
        elif extension in ['doc', 'docx']:
            import docx
            doc = docx.Document(file_path)
            text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
            if not text.strip():
                raise ValueError("Document appears to be empty")
            return text.strip()
        else:
            raise ValueError(f"Unsupported file format: {extension}")
            
    except Exception as e:
        raise ValueError(f"Failed to extract text from {extension.upper()} file: {str(e)}")

def extract_pdf_text_with_ocr(file_path):
    """
    Extract text from PDF with OCR fallback for image-based PDFs.
    """
    text = ""
    
    # Method 1: Try standard text extraction first
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(file_path)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        
        if text.strip():
            print("✓ Successfully extracted text using PyPDF2")
            return text.strip()
    except Exception as e:
        print(f"PyPDF2 extraction failed: {e}")
    
    # Method 2: Try pdfplumber
    try:
        import pdfplumber
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        
        if text.strip():
            print("✓ Successfully extracted text using pdfplumber")
            return text.strip()
    except ImportError:
        print("pdfplumber not installed")
    except Exception as e:
        print(f"pdfplumber extraction failed: {e}")
    
    # Method 3: OCR fallback using PyMuPDF + Tesseract
    print("Standard PDF extraction failed, attempting OCR...")
    return extract_pdf_with_ocr(file_path)

def extract_pdf_with_ocr(file_path):
    """
    Extract text from PDF using OCR (Optical Character Recognition).
    Requires: pip install PyMuPDF pytesseract pillow
    And Tesseract OCR installed on system.
    """
    try:
        import pytesseract
        
        # For Windows, you might need to specify tesseract path
        # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        
        # Open PDF with PyMuPDF
        doc = fitz.open(file_path)
        text = ""
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            
            # Convert page to image
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better OCR
            img_data = pix.tobytes("png")
            
            # Convert to PIL Image
            img = Image.open(io.BytesIO(img_data))
            
            # Perform OCR
            page_text = pytesseract.image_to_string(img, lang='eng')
            text += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
            
            print(f"✓ OCR completed for page {page_num + 1}")
        
        doc.close()
        
        if text.strip():
            print("✓ Successfully extracted text using OCR")
            return text.strip()
        else:
            raise ValueError("OCR completed but no text was found")
            
    except ImportError as e:
        missing_lib = str(e).split("'")[1] if "'" in str(e) else "required library"
        raise ValueError(f"OCR libraries not installed. Please install: pip install PyMuPDF pytesseract pillow")
    except Exception as e:
        raise ValueError(f"OCR extraction failed: {str(e)}")

def check_ocr_dependencies():
    """
    Check if OCR dependencies are available.
    """
    missing = []
    
    try:
        import fitz
    except ImportError:
        missing.append("PyMuPDF")
    
    try:
        import pytesseract
    except ImportError:
        missing.append("pytesseract")
    
    try:
        from PIL import Image
    except ImportError:
        missing.append("pillow")
    
    if missing:
        return False, missing
    
    # Check if Tesseract executable is available
    try:
        import pytesseract
        pytesseract.get_tesseract_version()
        return True, []
    except Exception:
        return False, ["Tesseract OCR executable"]

# Alternative: Cloud-based OCR using Google Vision API
def extract_pdf_with_google_vision(file_path, credentials_path=None):
    """
    Extract text using Google Cloud Vision API OCR.
    Requires: pip install google-cloud-vision
    """
    try:
        from google.cloud import vision
        import os
        
        if credentials_path:
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
        
        client = vision.ImageAnnotatorClient()
        
        # Open PDF with PyMuPDF
        doc = fitz.open(file_path)
        text = ""
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            img_data = pix.tobytes("png")
            
            image = vision.Image(content=img_data)
            response = client.text_detection(image=image)
            
            if response.text_annotations:
                page_text = response.text_annotations[0].description
                text += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
            
            if response.error.message:
                raise Exception(f'Google Vision API error: {response.error.message}')
        
        doc.close()
        return text.strip() if text.strip() else "No text found"
        
    except ImportError:
        raise ValueError("Google Cloud Vision not installed: pip install google-cloud-vision")
    except Exception as e:
        raise ValueError(f"Google Vision OCR failed: {str(e)}")