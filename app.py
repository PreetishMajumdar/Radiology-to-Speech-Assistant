import os
import json
import traceback
from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for
from werkzeug.utils import secure_filename
import uuid
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add this debug section to check what's available
print("=== DEBUG INFO ===")
print(f"GEMINI_API_KEY set: {'Yes' if os.environ.get('GEMINI_API_KEY') else 'No'}")
print(f"Current working directory: {os.getcwd()}")
print(f"Files in current directory: {os.listdir('.')}")

# Try importing utility classes with error handling
try:
    from utils.nlp import RadiologyTextSimplifier
    print("✓ Successfully imported RadiologyTextSimplifier")
except ImportError as e:
    print(f"✗ Failed to import RadiologyTextSimplifier: {e}")
    RadiologyTextSimplifier = None

try:
    from utils.tts import TextToSpeechConverter
    print("✓ Successfully imported TextToSpeechConverter")
except ImportError as e:
    print(f"✗ Failed to import TextToSpeechConverter: {e}")
    TextToSpeechConverter = None

# Check OCR dependencies
def check_ocr_dependencies():
    """Check if OCR dependencies are available."""
    missing = []
    
    try:
        import fitz
    except ImportError:
        missing.append("PyMuPDF")
    
    try:
        import pytesseract
        
        # Set Tesseract path for Windows
        tesseract_paths = [
            r'D:\Program Files\Tesseract-OCR\tesseract.exe',
            r'C:\Program Files\Tesseract-OCR\tesseract.exe',
            r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'
        ]
        
        for path in tesseract_paths:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                print(f"✓ Found Tesseract at: {path}")
                break
        else:
            print("⚠ Tesseract not found in common locations")
            
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
        version = pytesseract.get_tesseract_version()
        print(f"✓ Tesseract OCR version: {version}")
        return True, []
    except Exception as e:
        print(f"✗ Tesseract OCR error: {e}")
        return False, ["Tesseract OCR executable"]

# Check OCR availability
ocr_available, missing_deps = check_ocr_dependencies()
if ocr_available:
    print("✓ OCR dependencies available")
else:
    print(f"✗ OCR dependencies missing: {missing_deps}")

print("==================")

# Configuration
UPLOAD_FOLDER = 'uploads'
AUDIO_FOLDER = 'static/audio'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload size

# Create directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(AUDIO_FOLDER, exist_ok=True)

# Initialize Flask app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
app.secret_key = 'radiology_to_speech_secret_key'

# Initialize our services with error handling
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')

try:
    if RadiologyTextSimplifier:
        text_simplifier = RadiologyTextSimplifier(api_key=GEMINI_API_KEY)
        print("✓ RadiologyTextSimplifier initialized")
    else:
        text_simplifier = None
        print("✗ RadiologyTextSimplifier not available")
except Exception as e:
    print(f"✗ Error initializing RadiologyTextSimplifier: {e}")
    text_simplifier = None

try:
    if TextToSpeechConverter:
        tts_converter = TextToSpeechConverter(output_dir=AUDIO_FOLDER)
        print("✓ TextToSpeechConverter initialized")
    else:
        tts_converter = None
        print("✗ TextToSpeechConverter not available")
except Exception as e:
    print(f"✗ Error initializing TextToSpeechConverter: {e}")
    tts_converter = None

def allowed_file(filename):
    """Check if a file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_pdf_with_ocr(file_path):
    """Extract text from PDF using OCR."""
    try:
        import fitz  # PyMuPDF
        import pytesseract
        from PIL import Image
        import io
        
        # Set Tesseract path for Windows if not already set
        if not hasattr(pytesseract.pytesseract, 'tesseract_cmd') or not pytesseract.pytesseract.tesseract_cmd:
            tesseract_paths = [
                r'D:\Program Files\Tesseract-OCR\tesseract.exe',
                r'C:\Program Files\Tesseract-OCR\tesseract.exe',
                r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'
            ]
            
            for path in tesseract_paths:
                if os.path.exists(path):
                    pytesseract.pytesseract.tesseract_cmd = path
                    print(f"✓ Using Tesseract at: {path}")
                    break
        
        doc = fitz.open(file_path)
        text = ""
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            
            # Convert page to image with higher resolution for better OCR
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom
            img_data = pix.tobytes("png")
            
            # Convert to PIL Image
            img = Image.open(io.BytesIO(img_data))
            
            # Perform OCR
            page_text = pytesseract.image_to_string(img, lang='eng')
            if page_text.strip():
                text += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
            
            print(f"✓ OCR completed for page {page_num + 1}")
        
        doc.close()
        
        if text.strip():
            print("✓ Successfully extracted text using OCR")
            return text.strip()
        else:
            raise ValueError("OCR completed but no readable text was found")
            
    except ImportError as e:
        missing_lib = "OCR libraries (PyMuPDF, pytesseract, pillow)"
        raise ValueError(f"OCR libraries not installed. Please run: pip install PyMuPDF pytesseract pillow")
    except Exception as e:
        raise ValueError(f"OCR extraction failed: {str(e)}")

def extract_text_from_file(file_path):
    """Extract text from a file with OCR support for image-based PDFs."""
    extension = file_path.rsplit('.', 1)[1].lower()
    
    try:
        if extension == 'txt':
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read().strip()
                if not text:
                    raise ValueError("Text file appears to be empty")
                return text
                
        elif extension == 'pdf':
            text = ""
            
            # Method 1: Try PyPDF2
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
            
            # Method 2: Try pdfplumber as fallback
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
            
            # Method 3: OCR fallback for image-based PDFs
            if not text.strip():
                if ocr_available:
                    print("Standard PDF extraction failed, attempting OCR...")
                    return extract_pdf_with_ocr(file_path)
                else:
                    raise ValueError(
                        "PDF appears to be image-based or scanned. "
                        "Standard text extraction failed and OCR is not available. "
                        f"To enable OCR, install: pip install PyMuPDF pytesseract pillow "
                        "and install Tesseract OCR on your system."
                    )
            
            return text.strip()
            
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

@app.route('/')
def index():
    """Render the home page."""
    try:
        return render_template('index.html')
    except Exception as e:
        print(f"Error rendering index.html: {e}")
        return f"<h1>Radiology Text Simplifier</h1><p>Error: {e}</p><p>Please create templates/index.html</p>"

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors with detailed logging."""
    print("=== 500 ERROR DETAILS ===")
    print(f"Error: {error}")
    print("Traceback:")
    traceback.print_exc()
    print("=========================")
    return jsonify({
        'error': 'Internal server error',
        'details': str(error),
        'help': 'Check the console/logs for detailed error information'
    }), 500

@app.route('/simplify', methods=['POST'])
def simplify():
    """
    Simplify radiology text and convert to speech with OCR support.
    """
    try:
        print("=== SIMPLIFY REQUEST DEBUG ===")
        print(f"Form data keys: {list(request.form.keys())}")
        print(f"Files: {list(request.files.keys())}")
        
        # Check if required services are available
        if not text_simplifier:
            return jsonify({
                'error': 'Text simplification service not available',
                'help': 'Check that utils/nlp.py exists and RadiologyTextSimplifier class is properly defined'
            }), 500
        
        # Get form data
        target_audience = request.form.get('target_audience', 'general')
        grade_level = int(request.form.get('grade_level', 6))
        language = request.form.get('language', 'English')
        language_code = request.form.get('language_code', 'en')
        
        print(f"Parameters: audience={target_audience}, grade={grade_level}, lang={language}")
        
        text = None
        source_info = ""
        extraction_method = ""
        
        # Check for text input
        if 'text' in request.form:
            text_input = request.form['text'].strip()
            if text_input:
                text = text_input
                source_info = "direct text input"
                print(f"Using direct text input: {len(text)} characters")
        
        # Check for file upload if no text
        if not text and 'file' in request.files:
            file = request.files['file']
            if file and file.filename and file.filename != '':
                if allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    unique_filename = f"{time.time()}_{filename}"
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                    file.save(file_path)
                    
                    print(f"Processing file: {filename}")
                    
                    try:
                        text = extract_text_from_file(file_path)
                        source_info = f"file upload ({filename})"
                        print(f"Extracted text: {len(text)} characters")
                        
                        # Clean up
                        try:
                            os.remove(file_path)
                        except:
                            pass
                            
                    except Exception as e:
                        print(f"File extraction error: {e}")
                        
                        # Provide helpful error message based on the error
                        error_msg = str(e)
                        suggestions = []
                        
                        if "OCR" in error_msg or "image-based" in error_msg:
                            suggestions.append("This appears to be a scanned/image-based PDF.")
                            if not ocr_available:
                                suggestions.append("To process image-based PDFs, install OCR support:")
                                suggestions.append("1. pip install PyMuPDF pytesseract pillow")
                                suggestions.append("2. Install Tesseract OCR from: https://github.com/tesseract-ocr/tesseract")
                            suggestions.append("Alternatively, try converting the PDF to text using online tools.")
                        
                        return jsonify({
                            'error': f'Failed to extract text from file: {error_msg}',
                            'suggestions': suggestions,
                            'ocr_available': ocr_available
                        }), 500
                else:
                    return jsonify({'error': 'File type not allowed. Please upload .txt, .pdf, .doc, or .docx files.'}), 400
        
        # Validate text
        if not text:
            return jsonify({
                'error': 'No report provided. Please either enter text directly or upload a file.',
            }), 400
        
        if len(text.strip()) < 10:
            return jsonify({
                'error': 'The text appears to be too short or empty.',
                'extracted_text': text
            }), 400
        
        print("Calling text_simplifier.simplify_text...")
        
        # Simplify the text
        result = text_simplifier.simplify_text(
            text=text,
            target_audience=target_audience,
            grade_level=grade_level,
            language=language
        )
        
        print(f"Simplification result: success={result.get('success', False)}")
        
        if not result['success']:
            return jsonify({
                'error': f"Failed to simplify text: {result.get('error', 'Unknown error')}",
                'original_text_preview': text[:200] + '...' if len(text) > 200 else text
            }), 500
        
        # Convert to speech if TTS is available
        speech_result = None
        if tts_converter:
            print("Converting to speech...")
            speech_result = tts_converter.convert_to_speech(
                text=result['simplified_text'],
                language=language_code
            )
            print(f"TTS result: success={speech_result.get('success', False)}")
        
        # Prepare response
        response_data = {
            'original_text': result['original_text'],
            'simplified_text': result['simplified_text'],
            'source': source_info,
            'language': language,
            'success': True,
            'ocr_available': ocr_available
        }
        
        if speech_result and speech_result['success']:
            response_data['audio_filename'] = speech_result['filename']
        elif tts_converter:
            response_data['audio_error'] = speech_result.get('error', 'Failed to convert text to speech') if speech_result else 'TTS service error'
            response_data['warning'] = 'Text was simplified successfully, but audio generation failed.'
        else:
            response_data['warning'] = 'Text to speech service not available.'
        
        print("Returning successful response")
        return jsonify(response_data)
        
    except Exception as e:
        print(f"Unexpected error in simplify(): {e}")
        traceback.print_exc()
        return jsonify({
            'error': f'Unexpected server error: {str(e)}',
            'type': type(e).__name__
        }), 500

@app.route('/api/simplify', methods=['POST'])
def api_simplify():
    """API endpoint for text simplification."""
    data = request.json
    
    if not data or 'text' not in data:
        return jsonify({'error': 'No text provided'}), 400
    
    text = data['text']
    target_audience = data.get('target_audience', 'general')
    grade_level = int(data.get('grade_level', 6))
    language = data.get('language', 'English')
    
    result = text_simplifier.simplify_text(
        text=text,
        target_audience=target_audience,
        grade_level=grade_level,
        language=language
    )
    
    if not result['success']:
        return jsonify({'error': result.get('error', 'Failed to simplify text')}), 500
    
    return jsonify({
        'original_text': result['original_text'],
        'simplified_text': result['simplified_text'],
        'target_audience': target_audience,
        'grade_level': grade_level,
        'language': language
    })

@app.route('/check-ocr-status')
def check_ocr_status():
    """Check OCR dependencies status."""
    return jsonify({
        'ocr_available': ocr_available,
        'missing_dependencies': missing_deps if not ocr_available else []
    })

if __name__ == '__main__':
    print("Starting Flask application...")
    app.run(debug=True)