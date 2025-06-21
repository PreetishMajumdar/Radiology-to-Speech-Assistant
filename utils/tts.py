import os
from gtts import gTTS
from typing import Dict, Any, Optional
import uuid

class TextToSpeechConverter:
    """
    A class to convert text to speech using gTTS.
    """
    
    def __init__(self, output_dir: str = "static/audio"):
        """
        Initialize the TextToSpeechConverter.
        
        Args:
            output_dir: Directory to save the generated audio files
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def convert_to_speech(self, 
                         text: str, 
                         language: str = "en",
                         slow: bool = False) -> Dict[str, Any]:
        """
        Convert text to speech using gTTS and save to an audio file.
        
        Args:
            text: The text to convert to speech
            language: The language code for the speech (e.g., 'en' for English)
            slow: Whether to speak slowly
            
        Returns:
            A dictionary with information about the generated audio
        """
        try:
            # Generate a unique filename
            filename = f"{uuid.uuid4()}.mp3"
            filepath = os.path.join(self.output_dir, filename)
            
            # Create gTTS object
            tts = gTTS(text=text, lang=language, slow=slow)
            
            # Save to file
            tts.save(filepath)
            
            return {
                "success": True,
                "filename": filename,
                "filepath": filepath,
                "text": text,
                "language": language
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "text": text
            }
