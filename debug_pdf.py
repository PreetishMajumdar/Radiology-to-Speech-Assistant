#!/usr/bin/env python3
"""
PDF Debug Utility for Radiology-to-Speech Assistant

This script helps diagnose issues with PDF text extraction.
Usage: python debug_pdf.py <path_to_pdf>
"""

import sys
import os
from pathlib import Path

def test_pypdf2(file_path):
    """Test PyPDF2 extraction method."""
    print("🔍 Testing PyPDF2...")
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(file_path)
        
        print(f"   📄 Number of pages: {len(reader.pages)}")
        print(f"   📋 Document info: {reader.metadata}")
        
        total_text = ""
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text()
            print(f"   📃 Page {i+1}: {len(page_text)} characters")
            if page_text:
                total_text += page_text + "\n"
        
        if total_text.strip():
            print(f"   ✅ PyPDF2 SUCCESS: Extracted {len(total_text)} total characters")
            print(f"   📝 First 200 chars: {total_text[:200]}...")
            return total_text.strip()
        else:
            print(f"   ❌ PyPDF2 FAILED: No text extracted")
            return None
            
    except ImportError:
        print("   ⚠️  PyPDF2 not installed")
        return None
    except Exception as e:
        print(f"   ❌ PyPDF2 ERROR: {e}")
        return None

def test_pdfplumber(file_path):
    """Test pdfplumber extraction method."""
    print("\n🔍 Testing pdfplumber...")
    try:
        import pdfplumber
        
        total_text = ""
        with pdfplumber.open(file_path) as pdf:
            print(f"   📄 Number of pages: {len(pdf.pages)}")
            
            for i, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                print(f"   📃 Page {i+1}: {len(page_text) if page_text else 0} characters")
                if page_text:
                    total_text += page_text + "\n"
        
        if total_text.strip():
            print(f"   ✅ pdfplumber SUCCESS: Extracted {len(total_text)} total characters")
            print(f"   📝 First 200 chars: {total_text[:200]}...")
            return total_text.strip()
        else:
            print(f"   ❌ pdfplumber FAILED: No text extracted")
            return None
            
    except ImportError:
        print("   ⚠️  pdfplumber not installed - run: pip install pdfplumber")
        return None
    except Exception as e:
        print(f"   ❌ pdfplumber ERROR: {e}")
        return None

def test_pymupdf(file_path):
    """Test PyMuPDF extraction method."""
    print("\n🔍 Testing PyMuPDF...")
    try:
        import fitz  # PyMuPDF
        
        doc = fitz.open(file_path)
        print(f"   📄 Number of pages: {doc.page_count}")
        print(f"   📋 Document metadata: {doc.metadata}")
        
        total_text = ""
        for page_num in range(doc.page_count):
            page = doc[page_num]
            page_text = page.get_text()
            print(f"   📃 Page {page_num+1}: {len(page_text)} characters")
            if page_text:
                total_text += page_text + "\n"
        
        doc.close()
        
        if total_text.strip():
            print(f"   ✅ PyMuPDF SUCCESS: Extracted {len(total_text)} total characters")
            print(f"   📝 First 200 chars: {total_text[:200]}...")
            return total_text.strip()
        else:
            print(f"   ❌ PyMuPDF FAILED: No text extracted")
            return None
            
    except ImportError:
        print("   ⚠️  PyMuPDF not installed - run: pip install PyMuPDF")
        return None
    except Exception as e:
        print(f"   ❌ PyMuPDF ERROR: {e}")
        return None

def analyze_pdf_structure(file_path):
    """Analyze PDF structure for diagnostic purposes."""
    print("\n🔍 Analyzing PDF structure...")
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(file_path)
        
        print(f"   📊 File size: {os.path.getsize(file_path)} bytes")
        print(f"   🔐 Encrypted: {reader.is_encrypted}")
        
        if reader.metadata:
            metadata = reader.metadata
            print(f"   📅 Creation date: {metadata.get('/CreationDate', 'Unknown')}")
            print(f"   🏭 Producer: {metadata.get('/Producer', 'Unknown')}")
            print(f"   📝 Creator: {metadata.get('/Creator', 'Unknown')}")
            print(f"   📖 Title: {metadata.get('/Title', 'Unknown')}")
        
        # Check first page for fonts and content streams
        if len(reader.pages) > 0:
            page = reader.pages[0]
            if '/Font' in page:
                fonts = page['/Font']
                print(f"   🔤 Fonts found: {len(fonts)} font(s)")
                for font_name, font_obj in fonts.items():
                    if isinstance(font_obj, dict) and '/BaseFont' in font_obj:
                        print(f"     - {font_name}: {font_obj['/BaseFont']}")
            else:
                print(f"   ⚠️  No fonts found in first page - might be image-based")
        
    except Exception as e:
        print(f"   ❌ Analysis ERROR: {e}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python debug_pdf.py <path_to_pdf>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        sys.exit(1)
    
    if not file_path.lower().endswith('.pdf'):
        print(f"❌ Not a PDF file: {file_path}")
        sys.exit(1)
    
    print(f"🔧 PDF Debug Utility")
    print(f"📁 File: {file_path}")
    print("=" * 60)
    
    # Analyze PDF structure
    analyze_pdf_structure(file_path)
    
    # Test different extraction methods
    results = []
    
    pypdf2_result = test_pypdf2(file_path)
    if pypdf2_result:
        results.append(("PyPDF2", pypdf2_result))
    
    pdfplumber_result = test_pdfplumber(file_path)
    if pdfplumber_result:
        results.append(("pdfplumber", pdfplumber_result))
    
    pymupdf_result = test_pymupdf(file_path)
    if pymupdf_result:
        results.append(("PyMuPDF", pymupdf_result))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    
    if results:
        print(f"✅ {len(results)} method(s) successfully extracted text:")
        for method, text in results:
            print(f"   • {method}: {len(text)} characters")
        
        # Show comparison if multiple methods worked
        if len(results) > 1:
            print(f"\n🔍 Comparing results:")
            lengths = [len(text) for _, text in results]
            if max(lengths) - min(lengths) > 100:
                print(f"   ⚠️ Significant difference in extracted text lengths")
                print(f"   📏 Range: {min(lengths)} - {max(lengths)} characters")
            else:
                print(f"   ✅ Similar text lengths across methods")
        
        print(f"\n📝 Recommended: Use the method that extracted the most text")
        best_method, best_text = max(results, key=lambda x: len(x[1]))
        print(f"   🏆 Best: {best_method} ({len(best_text)} characters)")
        
    else:
        print("❌ NO TEXT EXTRACTED BY ANY METHOD")
        print("\n🔍 Possible reasons:")
        print("   • PDF contains only images (scanned document)")
        print("   • PDF uses unsupported font encoding")
        print("   • PDF is password-protected")
        print("   • PDF is corrupted")
        print("\n💡 Suggestions:")
        print("   • Try OCR software (e.g., Tesseract) for image-based PDFs")
        print("   • Check if PDF can be opened and text can be selected/copied")
        print("   • Convert to a different format using online tools")

if __name__ == "__main__":
    main()
