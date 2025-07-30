from Fields.seismicdesign import SeismicDesignCategorySearcher  # For searching seismic design categories
from Fields.seismicresistance import SeismicResistanceSearcher  # For searching seismic resistance systems
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

# === FIELD SEARCHING ===
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
    seismicR_searcher = SeismicResistanceSearcher()

    design_codes = code_searcher.search_codes(text)
    standardized_codes = code_searcher.standardize_design_codes(design_codes)

    risk_category = risk_searcher.search(text)
    standardized_risk = risk_searcher.standardize(risk_category)

    site_class = site_searcher.search(text)
    standardized_site = site_searcher.standardize(site_class)

    seismic_design_category = seismic_searcher.search(text)
    seismic_resistance_system = seismicR_searcher.search(text)
    wind_speed = wind_searcher.search(text)
    project_name = project_searcher.search(text)
    job_number = jobnumber_searcher.search(text)
    materials = materials_searcher.search(text)
    location_name = location_searcher.search(text)

    print("--------------------------------")
    print("🎯 Raw job number:", job_number)
    print("🎯 Raw project name:", project_name)
    print("🎯 Raw location name:", location_name)
    print("🎯 Raw design codes:", design_codes)
    print("🎯 Raw materials:", materials)
    print("🎯 Raw seismic resistance system:", seismic_resistance_system)
    print("🎯 Raw risk category:", risk_category)
    print("🎯 Raw site class:", site_class)
    print("🎯 Raw seismic design category:", seismic_design_category)
    print("🎯 Raw wind speed:", wind_speed)
    print("🎯 Raw all data:", "See Excel file in results folder")

    return {
        "job_number": job_number,
        "project_name": project_name,
        "location": location_name,
        "design_code": standardized_codes,
        "materials": materials,
        "seismic_resistance_system": seismic_resistance_system,
        "risk_category": standardized_risk,
        "site_class": standardized_site,
        "seismic_design_category": seismic_design_category,
        "wind_speed": wind_speed,
    }

# === SMART TEXT EXTRACTION ===
def extract_text_smart(pdf_path, return_raw=False):
    text_parts = []

    extractors = [
        TextExtractor.extract_with_pdfplumber,
        TextExtractor.extract_with_pymupdf,
        TextExtractor.extract_with_pdfminer,
        lambda p: TextExtractor.extract_with_ocr_fast(p)  
    ]

    for extractor in extractors:
        try:
            text = extractor(pdf_path)
            char_count = len(text.strip())
            print(f"✅ {extractor.__name__} extracted {char_count} characters.")
            if char_count > 0:
                text_parts.append(text)
            else:
                print(f"⚠️ {extractor.__name__} found no text.")
        except Exception as e:
            print(f"❌ Extractor {extractor.__name__} failed: {e}")

    combined_text = "\n".join(text_parts)

    # === Optional: Save raw extracted text to file for review ===
    debug_txt_output_path = os.path.join("results", f"{os.path.basename(pdf_path)}_textdump.txt")
    with open(debug_txt_output_path, "w", encoding="utf-8") as f:
        f.write(combined_text)

    # === Structured field search and return ===
    fields = search_engineering_fields(combined_text)
    raw_text_container = AllDataExtractor(combined_text)

    return (fields, raw_text_container) if return_raw else fields

# === PARALLEL WORKER ===
def process_pdf_file(pdf_path):
    try:
        filename = os.path.basename(pdf_path)
        print(f"\n📄 Processing: {filename}\n")

        start = time()
        fields, raw_text_obj = extract_text_smart(pdf_path, return_raw=True)
        duration = time() - start
        print(f"⏱️ Processing time for {filename}: {duration:.2f} seconds")
        print("--------------------------------")

        complete_data = {**fields, **raw_text_obj.to_dict()}
        return (filename, complete_data)

    except Exception as e:
        print(f"❌ Error processing {pdf_path}: {e}")
        return (os.path.basename(pdf_path), None)

# === MAIN ===
if __name__ == "__main__":
    input_folder = r"C:\\Users\\leben\\Downloads\\BOK_PDFs"
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
            CSVHandler.write_to_csv(fields, output_csv, filename)

    CSVHandler.write_raw_text_to_excel(all_results, output_xlsx)

    total_duration = time() - total_start
    print(f"\n⏳ Total processing time for all PDFs: {total_duration:.2f} seconds")
    print("✅ Structured data saved to:", output_csv)
    print("📝 Raw text saved to Excel:", output_xlsx)