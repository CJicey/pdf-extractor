import pandas as pd
import csv
import os

class CSVHandler:
    headers = [
        "Source_File", "Project_Name", "Location_Name", "Job_Number", "Design_Codes", "Materials",
        "Risk_Category", "Seismic_Design_Category",
        "Site_Class", "Wind_Speed", "All_Data"
    ]

    @staticmethod
    def prompt_clear_csv(csv_file):
        if os.path.exists(csv_file):
            user_input = input(f"\n⚠️ File '{csv_file}' already exists. Clear it? (y/n): ").lower()
            if user_input == 'y':
                with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(CSVHandler.headers)
                print("🧹 CSV cleared.")
            else:
                print("➡️ Appending to existing CSV.")

    @staticmethod
    def prompt_clear_excel(excel_file):
        if os.path.exists(excel_file):
            user_input = input(f"\n⚠️ Excel file '{excel_file}' already exists. Do you want to overwrite it? (y/n): ").lower()
            if user_input == 'y':
                os.remove(excel_file)
                print("🧹 Excel file cleared and will be recreated.")
            else:
                print("➡️ Raw text will be appended (if supported).")

    @staticmethod
    def write_to_csv(data_dict, csv_file, source_file):
        complete_data = {
            "Source_File": source_file,
            "Project_Name": data_dict.get("project_name") or "Null",
            "Location_Name": data_dict.get("location_name") or "Null",
            "Job_Number": data_dict.get("job_number") or "Null",
            "Design_Codes": data_dict.get("design_code") or "Null",
            "Materials": data_dict.get("materials") or "Null",
            "Risk_Category": data_dict.get("risk_category") or "Null",
            "Seismic_Design_Category": data_dict.get("seismic_design_category") or "Null",
            "Site_Class": data_dict.get("site_class") or "Null",
            "Wind_Speed": data_dict.get("wind_speed") or "Null",
            "All_Data": "See Excel file in results folder"  # Tell user where to find raw text
        }

        file_exists = os.path.isfile(csv_file)
        with open(csv_file, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=CSVHandler.headers)
            if not file_exists:
                writer.writeheader()
            writer.writerow(complete_data)

    @staticmethod
    def write_raw_text_to_excel(rows, excel_file):
        raw_texts = []

        for row in rows:
            raw_texts.append({
                "Source_File": row.get("Source_File"),
                "All_Data": row.get("raw_text") or "Null"
            })

        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            pd.DataFrame(raw_texts).to_excel(writer, sheet_name="Raw_Text", index=False)