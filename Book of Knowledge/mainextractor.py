from Fields.riskcategory import RiskCategoryExtractor  # For extracting risk categories
from Fields.designcode import BuildingCodeExtractor  # For extracting engineering codes
from Fields.siteclass import SiteClassExtractor      # For extracting site classes
from pdf2image import convert_from_path              # For converting PDF to images
from datetime import datetime                        # For timestamping the output file
from time import time                                # For timing the execution
import numpy as np                                   # For image processing
import pytesseract                                   # For OCR
import pdfplumber                                    # For extracting text from PDF files
import fitz                                          # For PyMuPDF
import cv2                                           # OpenCV for OCR preprocessing
import csv                                           # For writing to CSV
import re                                            # For regular expressions
import os                                            # For file operations


# === CONFIGURATION ===
TESSERACT_PATH = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

# === EXTRACTORS ===
# === PDF EXTRACTOR ===
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

# === PDF EXTRACTOR ===
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

# === OCR EXTRACTOR ===
def extract_with_ocr_fast(pdf_path, dpi=150, max_pages=5):
    try:
        images = convert_from_path(pdf_path, dpi=dpi, first_page=1, last_page=max_pages)
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

# === COMBINED EXTRACTOR ===
def extract_text_smart(pdf_path):
    text_parts = []
    for extractor in [extract_with_pdfplumber, extract_with_pymupdf]:
        text = extractor(pdf_path)
        if text.strip():
            text_parts.append(text)

    # Always include OCR to capture missed content
    ocr_text = extract_with_ocr_fast(pdf_path, max_pages=5)
    if ocr_text.strip():
        text_parts.append(ocr_text)
    combined_text = "\n".join(text_parts)

    return extract_enginnering_fields(combined_text)

# === FIELDS ===
def extract_enginnering_fields(text):
    code_extractor = BuildingCodeExtractor()
    risk_extractor = RiskCategoryExtractor()
    site_extractor = SiteClassExtractor()

    design_codes = code_extractor.extract_codes(text)
    standardized_codes = code_extractor.standardize_design_codes(design_codes)

    risk_category = risk_extractor.extract(text)
    standardized_risk = risk_extractor.standardize(risk_category)

    site_class = site_extractor.extract(text)
    standardized_site = site_extractor.standardize(site_class)  
    
    print("--------------------------------")
    print("🎯 Raw design codes:", design_codes)
    print("🎯 Raw risk category:", risk_category)
    print("🎯 Raw site class:", site_class)
    return {
        "design_code": standardized_codes,
        "risk_category": standardized_risk,
        "site_class": standardized_site
    }

# === CSV WRITER ===
def write_to_csv(data_dict, csv_file, source_file):
    headers = ["Source_File", "Design_Codes", "Risk_Category", "Site_Class"]
    complete_data = {
        "Source_File": source_file,
        "Design_Codes": data_dict.get("design_code") or "Null",
        "Risk_Category": data_dict.get("risk_category") or "Null",
        "Site_Class": data_dict.get("site_class") or "Null"
    }

    file_exists = os.path.isfile(csv_file)
    with open(csv_file, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        if not file_exists:
            writer.writeheader()
        writer.writerow(complete_data)

# === CLEAR CSV OPTION ===
def prompt_clear_csv(csv_file):
    if os.path.exists(csv_file):
        user_input = input(f"\n⚠️ CSV file '{csv_file}' already exists. Do you want to clear its contents? (y/n): ").lower()
        if user_input == 'y':
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Source_File", "Design_Codes", "Risk_Category", "Site_Class"])  
            print("🧹 CSV cleared.")
        else:
            print("➡️ Appending to existing CSV.")  

# === MAIN EXECUTION ===
if __name__ == "__main__":
    input_folder = r"C:\\Users\\leben\\Downloads\\BOK_PDFs"
    timestamp = datetime.now().strftime("%Y-%m-%d")
    output_dir = "results"
    os.makedirs(output_dir, exist_ok=True)
    output_csv = os.path.join(output_dir, f"extracted_meeting_notes_{timestamp}.csv")

    prompt_clear_csv(output_csv)
    total_start = time()
    
    for filename in os.listdir(input_folder):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(input_folder, filename)
            print(f"\n📄 Processing: {filename}")

            start = time()
            fields = extract_text_smart(pdf_path)

            write_to_csv(fields, output_csv, filename)
            duration = time() - start
            print(f"⏱️ Processing time for {filename}: {duration:.2f} seconds")
            print("--------------------------------")
    total_duration = time() - total_start
    print(f"\n⏳ Total processing time for all PDFs: {total_duration:.2f} seconds")
    print("✅ All PDFs processed. Data saved to:", output_csv)
