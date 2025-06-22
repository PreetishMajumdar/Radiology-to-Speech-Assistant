import os
import traceback
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
app.secret_key = 'radiology_to_speech_secret_key'

# Create directories if they don't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('static/audio', exist_ok=True)

# Import utility classes
try:
    from utils.nlp import RadiologyTextSimplifier
    from utils.tts import TextToSpeechConverter
except ImportError:
    RadiologyTextSimplifier = None
    TextToSpeechConverter = None

# OCR setup
ocr_available = False
missing_deps = []
try:
    import fitz
    import pytesseract
    from PIL import Image
    import io

    for path in [
        r'D:\Program Files\Tesseract-OCR\tesseract.exe',
        r'C:\Program Files\Tesseract-OCR\tesseract.exe',
        r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe']:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            break
    pytesseract.get_tesseract_version()
    ocr_available = True
except Exception:
    missing_deps = ["PyMuPDF", "pytesseract", "pillow"]

# Services initialization
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
text_simplifier = RadiologyTextSimplifier(api_key=GEMINI_API_KEY) if RadiologyTextSimplifier else None
tts_converter = TextToSpeechConverter(output_dir='static/audio') if TextToSpeechConverter else None

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'txt', 'pdf', 'doc', 'docx'}

def extract_pdf_with_ocr(file_path):
    doc = fitz.open(file_path)
    text = ""
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        text += pytesseract.image_to_string(img, lang='eng') + "\n"
    doc.close()
    return text.strip()

def extract_text_from_file(file_path):
    extension = file_path.rsplit('.', 1)[1].lower()
    if extension == 'pdf':
        return extract_pdf_with_ocr(file_path)
    elif extension == 'txt':
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    elif extension in ['doc', 'docx']:
        import docx
        doc = docx.Document(file_path)
        return '\n'.join([p.text for p in doc.paragraphs]).strip()
    raise ValueError("Unsupported file format")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/simplify', methods=['POST'])
def simplify():
    try:
        if not text_simplifier:
            return jsonify({'error': 'Text simplification not available'}), 500

        text = request.form.get('text', '').strip()
        if not text and 'file' in request.files:
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                text = extract_text_from_file(file_path)
                os.remove(file_path)

        if not text or len(text) < 10:
            return jsonify({'error': 'Text is too short or missing'}), 400

        result = text_simplifier.simplify_text(
            text=text,
            target_audience=request.form.get('target_audience', 'general'),
            grade_level=int(request.form.get('grade_level', 6)),
            language=request.form.get('language', 'English')
        )

        response = {
            'original_text': result.get('original_text', ''),
            'simplified_text': result.get('simplified_text', ''),
            'success': result.get('success', False)
        }

        if tts_converter and result.get('success'):
            speech = tts_converter.convert_to_speech(result['simplified_text'], request.form.get('language_code', 'en'))
            if speech.get('success'):
                response['audio_filename'] = speech['filename']
            else:
                response['audio_error'] = speech.get('error')

        return jsonify(response)
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/check-ocr-status')
def check_ocr_status():
    return jsonify({'ocr_available': ocr_available, 'missing_dependencies': missing_deps})

if __name__ == '__main__':
    app.run(debug=True)
