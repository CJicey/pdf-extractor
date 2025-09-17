from Fields.seismicdesign import SeismicDesignCategorySearcher  # For searching seismic design categories
from Fields.seismicresistance import SeismicResistanceSearcher  # For searching seismic resistance systems
from Fields.riskcategory import RiskCategorySearcher            # For searching risk categories
from Fields.designcode import BuildingCodeSearcher              # For searching engineering codes
from Fields.siteclass import SiteClassSearcher                  # For searching site classes
from Fields.windspeed import WindSpeedSearcher                  # For searching wind speeds
from Fields.jobnumber import JobNumberSearcher                  # For searching job numbers
from Fields.materials import MaterialsSearcher                  # For searching materials
from Fields.alldata import AllDataExtractor                     # For extracting all raw data 

from Datahandler.txtseperator import PageDumpWriter             # Sepreates pages in txt file
from Extractor.extractor import TextExtractor                   # For extracting text from PDF files
from Datahandler.csvwriter import CSVHandler                    # For writing to CSV

from multiprocessing import Pool, cpu_count                     # For Multi Processing
from datetime import datetime                                   # For timestamping the output file 
from time import time                                           # For timing the execution

import pytesseract                                              # For OCR                                 
import os                                                       # For file operations

# === CONFIGURATION ===
TESSERACT_PATH = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

# === FIELD SEARCHING ===
def search_engineering_fields(full_pdf_text):
    def try_search(searcher, method='search', standardize_method='standardize',
                   bad_values=None):
        search_method = getattr(searcher, method)

        # Only use a standardize method if it's a valid string and exists
        if isinstance(standardize_method, str) and hasattr(searcher, standardize_method):
            standardize = getattr(searcher, standardize_method)
        else:
            standardize = lambda x: x  # no-op if no standardize method

        # single-source: full_pdf_text only
        primary_text = full_pdf_text
        secondary_text = None

        def is_bad(val):
            if not bad_values or val is None:
                return False
            def to_upstrings(x):
                if isinstance(x, str):
                    return {x.upper()}
                if isinstance(x, (list, tuple, set)):
                    return {str(y).upper() for y in x}
                return {str(x).upper()}
            return not to_upstrings(val).isdisjoint({b.upper() for b in bad_values})

        raw = search_method(primary_text)
        if is_bad(raw) and secondary_text:
            raw = search_method(secondary_text)

        return standardize(raw)

    # Initialize searchers
    code_searcher = BuildingCodeSearcher()
    risk_searcher = RiskCategorySearcher()
    site_searcher = SiteClassSearcher()
    seismic_searcher = SeismicDesignCategorySearcher()
    seismicR_searcher = SeismicResistanceSearcher()
    wind_searcher = WindSpeedSearcher()
    jobnumber_searcher = JobNumberSearcher()
    materials_searcher = MaterialsSearcher()

    # Perform extraction from full PDF only
    design_codes = code_searcher.search_codes(full_pdf_text)
    standardized_codes = code_searcher.standardize_design_codes(design_codes)

    risk_category = try_search(risk_searcher)
    site_class = try_search(site_searcher)
    seismic_design_category = try_search(seismic_searcher)  # Safe even if no standardize method
    seismic_resistance_system = try_search(seismicR_searcher)
    wind_speed = try_search(wind_searcher)

    # Job Number ignores bogus 'SHEET'
    job_number = try_search(jobnumber_searcher, bad_values={'SHEET'})

    materials = try_search(materials_searcher, standardize_method=None)

    print("--------------------------------")
    print("🎯 Raw job number:", job_number)
    print("🎯 Raw design codes:", design_codes)
    print("🎯 Raw materials:", materials)
    print("🎯 Raw seismic resistance system:", seismic_resistance_system)
    print("🎯 Raw risk category:", risk_category)
    print("🎯 Raw site class:", site_class)
    print("🎯 Raw seismic design category:", seismic_design_category)
    print("🎯 Raw wind speed:", wind_speed)
    print("🎯 Raw all data:", "See txt files in results folder")

    # Build fields dict with standardized codes
    fields = {
        "Job_Number": job_number,
        "Design_Codes": standardized_codes,
        "Materials": materials,
        "Seismic_Resistance_System": seismic_resistance_system,
        "Risk_Category": risk_category,
        "Site_Class": site_class,
        "Seismic_Design_Category": seismic_design_category,
        "Wind_Speed": wind_speed,
    }

    return fields

# === SMART TEXT EXTRACTION ===
def extract_text_smart(pdf_path, return_raw: bool = False):
    text_parts = []

    extractors = [
        TextExtractor.extract_with_pdfplumber,             # list[str] or str depending on impl
        TextExtractor.extract_with_pymupdf,                # str
        TextExtractor.extract_with_pdfminer,               # str
        lambda p: TextExtractor.extract_with_ocr_fast(p),  # str (OCR fallback)
    ]

    for extractor in extractors:
        try:
            text = extractor(pdf_path)
            if isinstance(text, list):
                text = "\n".join([t for t in text if t])
            name = getattr(extractor, "__name__", "extractor")
            char_count = len((text or "").strip())
            print(f"📝 {name} extracted {char_count} characters")
            if text:
                text_parts.append(text)
        except Exception as e:
            name = getattr(extractor, "__name__", "extractor")
            print(f"❌ Extractor {name} failed: {e}")

    # Combine all extractor outputs (no mirrored-text fixing)
    combined_text = "\n".join([t for t in text_parts if t]) if text_parts else ""

    # Write page-segmented dump from the combined text
    debug_txt_output_path = os.path.join(
        "TxT_Results", f"{os.path.basename(pdf_path)}_textdump.txt"
    )
    try:
        PageDumpWriter().write_by_page(pdf_path, debug_txt_output_path, combined_text)
        print(f"💾 Wrote page-segmented dump: {debug_txt_output_path}")
    except Exception as e:
        print(f"⚠️ Page dump failed (continuing): {e}")

    # Downstream uses the raw combined text
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
        print(f"⏱️  Processing time for {filename}: {duration:.2f} seconds")
        print("--------------------------------")

        complete_data = {**fields, **raw_text_obj.to_dict()}
        return (filename, complete_data)

    except Exception as e:
        print(f"❌ Error processing {pdf_path}: {e}")
        return (os.path.basename(pdf_path), None)

# === MAIN EXECUTION ===
if __name__ == "__main__":
    from multiprocessing import Pool, cpu_count
    from datetime import datetime

    input_folder = r"C:\\Users\\leben\\Downloads\\BOK_PDFs"
    timestamp = datetime.now().strftime("%Y-%m-%d")

    output_dir = "CSV_Result"   
    results_dir = "TxT_Results"          # keep for text dumps

    # Only create the Results directory; do NOT create CSV_Txt Results
    os.makedirs(results_dir, exist_ok=True)

    output_csv = os.path.join(output_dir, f"extracted_meeting_notes_{timestamp}.csv")
    output_notes = None

    # Keep your clear call as-is (it should handle missing dirs gracefully in your CSVHandler)
    CSVHandler.prompt_clear_all(output_csv, results_dir, general_notes_folder=None)

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

    total_duration = time() - total_start
    print(f"\n⏳ Total processing time for all PDFs: {total_duration:.2f} seconds")
    print("✅ Structured data saved to:", output_csv)