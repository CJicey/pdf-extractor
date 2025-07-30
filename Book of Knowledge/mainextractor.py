from Fields.seismicdesign import SeismicDesignCategorySearcher  # For searching seismic design categories
from Fields.riskcategory import RiskCategorySearcher            # For searching risk categories
from Fields.designcode import BuildingCodeSearcher              # For searching engineering codes
from Fields.projectname import ProjectNameSearcher              # For searching project names
from Fields.siteclass import SiteClassSearcher                  # For searching site classes
from Fields.windspeed import WindSpeedSearcher                  # For searching wind speeds
from Fields.jobnumber import JobNumberSearcher                  # For searching job numbers
from Fields.materials import MaterialsSearcher                  # For searching materials
from Fields.location import LocationSearcher                    # For searching location
from Fields.alldata import AllDataExtractor                     # For extracting all raw data 
from Extractor.extractor import TextExtractor                   # For extracting text from PDF files
from CSVhandler.csvwriter import CSVHandler                     # For writing to CSV
from multiprocessing import Pool, cpu_count                     # For Multi Processing
from datetime import datetime                                   # For timestamping the output file 
from time import time                                           # For timing the execution
import pytesseract                                              # For OCR
import os                                                       # For file operations

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

    fields = search_engineering_fields(combined_text)
    raw_text_container = AllDataExtractor(combined_text)

    return (fields, raw_text_container) if return_raw else fields

# === FIELDS ===
def search_engineering_fields(text):
    code_searcher = BuildingCodeSearcher()
    risk_searcher = RiskCategorySearcher()
    site_searcher = SiteClassSearcher()
    wind_searcher = WindSpeedSearcher()
    seismic_searcher = SeismicDesignCategorySearcher()
    project_searcher = ProjectNameSearcher()
    jobnumber_searcher = JobNumberSearcher()
    materials_searcher = MaterialsSearcher()
    location_searcher = LocationSearcher()

    design_codes = code_searcher.search_codes(text)
    standardized_codes = code_searcher.standardize_design_codes(design_codes)

    risk_category = risk_searcher.search(text)
    standardized_risk = risk_searcher.standardize(risk_category)

    site_class = site_searcher.search(text)
    standardized_site = site_searcher.standardize(site_class)

    seismic_design_category = seismic_searcher.search(text)
    wind_speed = wind_searcher.search(text)
    project_name = project_searcher.search(text)
    job_number = jobnumber_searcher.search(text)
    materials = materials_searcher.search(text)
    location_name = location_searcher.search(text)

    # Print debug info for each field
    print("--------------------------------")
    print("🎯 Raw project name:", project_name)
    print("🎯 Raw job number:", job_number)
    print("🎯 Raw location name:", location_name)
    print("🎯 Raw design codes:", design_codes)
    print("🎯 Raw materials:", materials)
    print("🎯 Raw risk category:", risk_category)
    print("🎯 Raw site class:", site_class)
    print("🎯 Raw seismic design category:", seismic_design_category)
    print("🎯 Raw wind speed:", wind_speed)
    print("🎯 Raw all data:", "See Excel file in results folder")

    return {
        "project_name": project_name,
        "job_number": job_number,
        "design_code": standardized_codes,
        "materials": materials,
        "risk_category": standardized_risk,
        "site_class": standardized_site,
        "seismic_design_category": seismic_design_category,
        "wind_speed": wind_speed,
        "location": location_name,
    }

# === PARALLEL WORKER FUNCTION ===
def process_pdf_file(pdf_path):
    try:
        filename = os.path.basename(pdf_path)
        print(f"\n📄 Processing: {filename}")
        print()

        start = time()
        fields, raw_text_obj = extract_text_smart(pdf_path, return_raw=True)

        duration = time() - start
        print(f"⏱️ Processing time for {filename}: {duration:.2f} seconds")
        print("--------------------------------")

        # Merge raw text into the extracted field dictionary
        complete_data = {**fields, **raw_text_obj.to_dict()}
        return (filename, complete_data)

    except Exception as e:
        print(f"❌ Error processing {pdf_path}: {e}")
        return (os.path.basename(pdf_path), None)

# === MAIN EXECUTION ===
if __name__ == "__main__":
    input_folder = r"C:\\Users\\CalebJohnson\\Downloads\\BOK_PDFs"
    timestamp = datetime.now().strftime("%Y-%m-%d")
    output_dir = "results"
    os.makedirs(output_dir, exist_ok=True)
    output_csv = os.path.join(output_dir, f"extracted_meeting_notes_{timestamp}.csv")
    output_xlsx = os.path.join(output_dir, f"extracted_meeting_notes_{timestamp}_raw_text.xlsx")

    CSVHandler.prompt_clear_csv(output_csv)
    CSVHandler.prompt_clear_excel(output_xlsx)

    total_start = time()

    pdf_files = [
        os.path.join(input_folder, f)
        for f in os.listdir(input_folder)
        if f.lower().endswith(".pdf")
    ]

    with Pool(processes=min(8, cpu_count())) as pool:
        results = pool.map(process_pdf_file, pdf_files)

    all_results = []

    for filename, fields in results:
        if fields:
            fields["Source_File"] = filename
            all_results.append(fields)

            # Write structured data to CSV
            CSVHandler.write_to_csv(fields, output_csv, filename)

    # Write all raw text to a separate Excel file
    CSVHandler.write_raw_text_to_excel(all_results, output_xlsx)

    total_duration = time() - total_start
    print(f"\n⏳ Total processing time for all PDFs: {total_duration:.2f} seconds")
    print("✅ Structured data saved to:", output_csv)
    print("📝 Raw text saved to Excel:", output_xlsx)