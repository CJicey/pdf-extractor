from pdfminer.high_level import extract_text as pdfminer_extract_text
from pdf2image import convert_from_path
import numpy as np
import pytesseract
import pdfplumber
import fitz
import cv2
import re

class TextExtractor:
    # --- internal helpers ---
    @staticmethod
    def _normalize_space(s: str) -> str:
        return re.sub(r"\s+", " ", (s or "").strip())

    # PDFPlumber extractor (full-document text)
    @staticmethod
    def extract_with_pdfplumber(pdf_path):
        try:
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return TextExtractor._normalize_space(text)
        except Exception:
            return ""

    # PyMuPDF extractor (full-document text)
    @staticmethod
    def extract_with_pymupdf(pdf_path):
        try:
            doc = fitz.open(pdf_path)
            text = ""
            for page in doc:
                text += page.get_text() or ""
            return TextExtractor._normalize_space(text)
        except Exception:
            return ""

    # PDFMiner extractor (full-document text)
    @staticmethod
    def extract_with_pdfminer(pdf_path):
        try:
            full_text = pdfminer_extract_text(pdf_path)
            return TextExtractor._normalize_space(full_text)
        except Exception as e:
            print(f"⚠️ PDFMiner failed for {pdf_path}: {e}")
            return ""

    # OCR extractor (full-document text)
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
            return TextExtractor._normalize_space(text)
        except Exception as e:
            print(f"⚠️ OCR failed for {pdf_path}: {e}")
            return ""