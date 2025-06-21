import google.generativeai as genai
import os
from typing import Dict, Any, Optional

class RadiologyTextSimplifier:
    """
    A class to simplify radiology report text using Google's Gemini API.
    """

    def __init__(self, api_key: str):
        """
        Initialize the RadiologyTextSimplifier with the Gemini API key.
        
        Args:
            api_key: The API key for Google's Gemini API
        """
        self.api_key = api_key
        genai.configure(api_key=api_key)
        # Use Gemini 1.5 Flash for faster processing and lower cost
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
    def simplify_text(self, 
                      text: str, 
                      target_audience: str = "general", 
                      grade_level: int = 6,
                      language: str = "English") -> Dict[str, Any]:
        """
        Simplify radiology report text using Gemini API.
        
        Args:
            text: The radiology report text to simplify
            target_audience: The target audience for the simplified text
            grade_level: Target reading grade level (e.g., 6 for 6th grade)
            language: The language for the simplified text
            
        Returns:
            A dictionary containing the simplified text and metadata
        """
        # Create the prompt with specific instructions for radiology report simplification
        prompt = f"""
        You are a medical translator assistant specialized in converting complex radiology reports into 
        easy-to-understand language. I will provide you with a radiology report, and your task is to:

        1. Simplify the medical terminology while preserving the important clinical information
        2. Target a {grade_level}th grade reading level
        3. Organize the information in a clear, structured way
        4. Explain key medical terms when they first appear
        5. Focus on what would be most important for a {target_audience} audience to understand
        6. Respond in {language}

        Here is the radiology report to simplify:
        ```
        {text}
        ```

        Please provide ONLY the simplified version, without any introduction or explanatory notes.
        """
        
        try:
            # Generate the simplified text
            response = self.model.generate_content(prompt)
            simplified_text = response.text.strip()
            
            return {
                "original_text": text,
                "simplified_text": simplified_text,
                "target_audience": target_audience,
                "grade_level": grade_level,
                "language": language,
                "success": True
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "original_text": text
            }
    
    def identify_key_findings(self, text: str) -> Dict[str, Any]:
        """
        Identify and extract key findings from a radiology report.
        
        Args:
            text: The radiology report text
            
        Returns:
            A dictionary containing the key findings
        """
        prompt = f"""
        You are a medical assistant specialized in analyzing radiology reports. 
        Extract the most important clinical findings from this radiology report, 
        listing them in order of medical significance. Include both normal and abnormal findings.
        
        Here is the radiology report:
        ```
        {text}
        ```
        
        Format your response as a simple bulleted list without any additional commentary.
        """
        
        try:
            response = self.model.generate_content(prompt)
            findings = response.text.strip()
            
            return {
                "key_findings": findings,
                "success": True
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
