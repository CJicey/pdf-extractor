from pdfminer.high_level import extract_text as pdfminer_extract_text
from pdf2image import convert_from_path
import numpy as np
import pytesseract
import pdfplumber
import fitz
import cv2
import re

class TextExtractor:
    #pdf extractor
    @staticmethod #This method doesn’t use or depend on any instance (self)
    def extract_with_pdfplumber(pdf_path, max_pages=5):
        try:
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    if i >= max_pages:
                        break
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return re.sub(r'\s+', ' ', text.strip())
        except Exception:
            return ""

    #pymupdf extractor
    @staticmethod
    def extract_with_pymupdf(pdf_path, max_pages=5):
        try:
            doc = fitz.open(pdf_path)
            text = ""
            for i, page in enumerate(doc):
                if i >= max_pages:
                    break
                text += page.get_text()
            return re.sub(r'\s+', ' ', text.strip())
        except Exception:
            return ""
        
    # PDFMiner extractor
    @staticmethod
    def extract_with_pdfminer(pdf_path, max_pages=5):
        try:
            full_text = pdfminer_extract_text(pdf_path)
            # Optionally limit to `max_pages` manually (PDFMiner doesn't offer a direct page limiter)
            pages = full_text.split('\f')  # PDFMiner separates pages with form-feed
            limited_text = "\n".join(pages[:max_pages])
            return re.sub(r'\s+', ' ', limited_text.strip())
        except Exception as e:
            print(f"⚠️ PDFMiner failed for {pdf_path}: {e}")
            return ""

    #ocr extractor
    @staticmethod
    def extract_with_ocr_fast(pdf_path, dpi=150):
        try:
            images = convert_from_path(pdf_path, dpi=dpi)
            text = ""
            for img in images:
                img_np = np.array(img)
                gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
                _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
                ocr_text = pytesseract.image_to_string(thresh)
                text += ocr_text + "\n"
            return re.sub(r'\s+', ' ', text.strip())
        except Exception as e:
            print(f"⚠️ OCR failed for {pdf_path}: {e}")
            return ""