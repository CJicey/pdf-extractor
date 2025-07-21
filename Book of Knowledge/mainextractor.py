from Fields.seismicdesign import SeismicDesignCategoryExtractor  # For extracting seismic design categories
from Fields.riskcategory import RiskCategoryExtractor  # For extracting risk categories
from Fields.designcode import BuildingCodeExtractor  # For extracting engineering codes
from Fields.projectname import ProjectNameExtractor  # For extracting project names
from Fields.siteclass import SiteClassExtractor      # For extracting site classes
from Fields.windspeed import WindSpeedExtractor      # For extracting wind speeds
from Fields.jobnumber import JobNumberExtractor      # For extracting job numbers
from Extractor.extractor import TextExtractor        # For extracting text from PDF files
from CSVhandler.csvwriter import CSVHandler          # For writing to CSV
from multiprocessing import Pool, cpu_count          # For Multi Processing
from datetime import datetime                        # For timestamping the output file 
from time import time                                # For timing the execution
import pytesseract                                   # For OCR
import os                                            # For file operations

# === CONFIGURATION ===
TESSERACT_PATH = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

# === SMART TEXT EXTRACTION ===
def extract_text_smart(pdf_path, return_raw=False):
    text_parts = []
    for extractor in [TextExtractor.extract_with_pdfplumber, TextExtractor.extract_with_pymupdf]:
        text = extractor(pdf_path)
        if text.strip():
            text_parts.append(text)

    ocr_text = TextExtractor.extract_with_ocr_fast(pdf_path, max_pages=5)
    if ocr_text.strip():
        text_parts.append(ocr_text)

    combined_text = "\n".join(text_parts)
    fields = extract_engineering_fields(combined_text)
    return (fields, combined_text) if return_raw else fields

# === FIELDS ===
def extract_engineering_fields(text):
    code_extractor = BuildingCodeExtractor()
    risk_extractor = RiskCategoryExtractor()
    site_extractor = SiteClassExtractor()
    wind_extractor = WindSpeedExtractor()
    seismic_extractor = SeismicDesignCategoryExtractor()
    project_extractor = ProjectNameExtractor()
    jobnumber_extractor = JobNumberExtractor()

    design_codes = code_extractor.extract_codes(text)
    standardized_codes = code_extractor.standardize_design_codes(design_codes)

    risk_category = risk_extractor.extract(text)
    standardized_risk = risk_extractor.standardize(risk_category)

    site_class = site_extractor.extract(text)
    standardized_site = site_extractor.standardize(site_class)

    seismic_design_category = seismic_extractor.extract(text)
    wind_speed = wind_extractor.extract(text)
    project_name = project_extractor.extract(text)
    job_number = jobnumber_extractor.extract(text)

    # Print debug info for each field
    print("--------------------------------")
    print("🎯 Raw project name:", project_name)
    print("🎯 Raw job number:", job_number)
    print("🎯 Raw design codes:", design_codes)
    print("🎯 Raw risk category:", risk_category)
    print("🎯 Raw site class:", site_class)
    print("🎯 Raw seismic design category:", seismic_design_category)
    print("🎯 Raw wind speed:", wind_speed)

    return {
        "project_name": project_name,
        "job_number": job_number,
        "design_code": standardized_codes,
        "risk_category": standardized_risk,
        "site_class": standardized_site,
        "seismic_design_category": seismic_design_category,
        "wind_speed": wind_speed,
    }

# === PARALLEL WORKER FUNCTION ===
def process_pdf_file(pdf_path):
    try:
        filename = os.path.basename(pdf_path)
        print(f"\n📄 Processing: {filename}")
        print()

        start = time()
        fields, _ = extract_text_smart(pdf_path, return_raw=True)

        duration = time() - start
        print(f"⏱️ Processing time for {filename}: {duration:.2f} seconds")
        print("--------------------------------")
        return (filename, fields)
    except Exception as e:
        print(f"❌ Error processing {pdf_path}: {e}")
        return (os.path.basename(pdf_path), None)

# === MAIN EXECUTION ===
if __name__ == "__main__":
    input_folder = r"C:\\Users\\leben\\Downloads\\BOK_PDFs"
    timestamp = datetime.now().strftime("%Y-%m-%d")
    output_dir = "results"
    os.makedirs(output_dir, exist_ok=True)
    output_csv = os.path.join(output_dir, f"extracted_meeting_notes_{timestamp}.csv")

    CSVHandler.prompt_clear_csv(output_csv)
    total_start = time()

    pdf_files = [
        os.path.join(input_folder, f)
        for f in os.listdir(input_folder)
        if f.lower().endswith(".pdf")
    ]

    with Pool(processes=min(8, cpu_count())) as pool:
        results = pool.map(process_pdf_file, pdf_files)

    for filename, fields in results:
        if fields:
            CSVHandler.write_to_csv(fields, output_csv, filename)

    total_duration = time() - total_start
    print(f"\n⏳ Total processing time for all PDFs: {total_duration:.2f} seconds")
    print("✅ All PDFs processed. Data saved to:", output_csv)