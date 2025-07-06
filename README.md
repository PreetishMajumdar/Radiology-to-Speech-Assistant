# Radiology-to-Speech Assistant

Transforming radiology accessibility with AI-powered speech and multi-modal diagnostics

## Overview

Radiology-to-Speech Assistant is an open-source project that bridges medical imaging and assistive technology. The system converts radiology reports and images into natural language audio summaries, aiming to democratize diagnostic access, reduce interpretation time, and support visually impaired practitioners.

- Current Version: OCR-based report-to-speech conversion

- Next-Gen Pipeline: Direct image analysis, multi-stage ML predictions, and automated speech output

## Features

- OCR Integration: Extracts text from radiology reports for audio conversion

- Direct Image Analysis (Planned): Processes radiology images without text dependency

- Multi-Stage ML Pipeline (Planned):

  - Scan type classification (X-ray, MRI, CT, etc.)

  - Organ identification

  - Tumor and abnormality detection

- Gemini API Integration: Generates diagnostic narratives from structured data

- Text-to-Speech Output: Delivers real-time audio summaries

- Clinical Collaboration: Developed in partnership with a senior radiologist in Nagpur for real-world validation

## Project Goals

- Democratize diagnostic access for all, including visually impaired practitioners

- Accelerate interpretation of radiology findings

- Enable research and clinical validation in real-world settings

## Tech Stack

| Component         | Technology                |

|-------------------|--------------------------|

| Frontend          | HTML, CSS, JavaScript    |

| Backend           | Python (Flask)           |

| OCR               | Tesseract, EasyOCR       |

| ML Models         | PyTorch, TensorFlow      |

| Image Processing  | OpenCV, pydicom          |

| Speech Synthesis  | Gemini API, gTTS         |

## Directory Structure

```

├── app/                # Flask application

│   ├── static/         # CSS, JS, images

│   ├── templates/      # HTML templates

│   └── utils/          # Helper functions, OCR, ML

├── models/             # ML models (planned)

├── data/               # Sample reports/images

├── requirements.txt    # Python dependencies

└── README.md           # Project documentation

```

## Getting Started

### Prerequisites

- Python 3.8+

- pip

- Tesseract OCR

- (Optional) GPU for ML model training

### Installation

1. Clone the repository:

   ```bash

   git clone https://github.com/PreetishMajumdar/Radiology-to-Speech-Assistant.git

   cd Radiology-to-Speech-Assistant

   ```

2. Install dependencies:

   ```bash

   pip install -r requirements.txt

   ```

3. Set up Tesseract OCR:

   - Install Tesseract for your OS

   - Ensure the binary is in your system PATH

4. Run the application:

   ```bash

   python app/main.py

   ```

5. Access the web app:

   - Open your browser and go to http://localhost:5000

## Usage

- Upload a radiology report (PDF or image)

- OCR extracts text and generates an audio summary

- (Planned) Upload a radiology image for direct ML-based analysis and speech output

## Roadmap

- [x] OCR-based report-to-speech

- [ ] Direct image analysis (scan type, organ, tumor/abnormality detection)

- [ ] Enhanced ML pipeline (U-Net, YOLO, Transformers)

- [ ] Gemini API integration for narrative generation

- [ ] Clinical validation and feedback loop

- [ ] Research paper publication

## Research & Collaboration

This project is being developed in collaboration with a senior radiologist in Nagpur to ensure clinical accuracy and real-world relevance. We are preparing for research publication and welcome contributions from those passionate about:

- Medical computer vision

- Multi-modal AI systems

- Clinical deployment in healthcare

If you are interested in collaborating or co-authoring research, please open an issue or contact the maintainer.

## Contributing

Contributions are welcome! Please:

1. Fork the repository

2. Create a new branch (`git checkout -b feature/your-feature`)

3. Commit your changes

4. Open a pull request

## Ethical Considerations

- For assistive use only: Not a substitute for professional medical advice

- Clinical review required: All outputs should be validated by qualified clinicians

- Data privacy: Ensure compliance with patient data protection regulations

## License

This project is licensed under the MIT License.

## Acknowledgments

- Senior radiologist collaborator (Nagpur)

- Open-source contributors and the medical AI community

## Contact

For questions, suggestions, or collaboration inquiries, please open an issue or reach out via LinkedIn.

Let’s make radiology more accessible, together!