import csv
import os

class CSVHandler:
    headers = [
        "Source_File", "Project_Name", "Job_Number", "Design_Codes",
        "Risk_Category", "Seismic_Design_Category",
        "Site_Class", "Wind_Speed"
    ]

    @staticmethod # This method doesn’t use or depend on any instance (self)
    def prompt_clear_csv(csv_file):
        if os.path.exists(csv_file):
            user_input = input(f"\n⚠️ CSV file '{csv_file}' already exists. Do you want to clear its contents? (y/n): ").lower()
            if user_input == 'y':
                with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(CSVHandler.headers)
                print("🧹 CSV cleared.")
            else:
                print("➡️ Appending to existing CSV.")  

    @staticmethod
    def write_to_csv(data_dict, csv_file, source_file):
        complete_data = {
            "Source_File": source_file,
            "Project_Name": data_dict.get("project_name") or "Null",
            "Job_Number": data_dict.get("job_number") or "Null",
            "Design_Codes": data_dict.get("design_code") or "Null",
            "Risk_Category": data_dict.get("risk_category") or "Null",
            "Seismic_Design_Category": data_dict.get("seismic_design_category") or "Null",
            "Site_Class": data_dict.get("site_class") or "Null",
            "Wind_Speed": data_dict.get("wind_speed") or "Null",
        }

        file_exists = os.path.isfile(csv_file)
        with open(csv_file, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=CSVHandler.headers)
            if not file_exists:
                writer.writeheader()
            writer.writerow(complete_data)