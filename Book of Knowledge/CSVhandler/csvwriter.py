import csv
import os

class CSVHandler:
    headers = [
        "Source_File", "Job_Number", "Design_Codes", "Materials", "Seismic_Resistance_System",
        "Risk_Category", "Seismic_Design_Category",
        "Site_Class", "Wind_Speed", "All_Data"
    ]

    @staticmethod
    def prompt_clear_all(csv_file, results_folder):
        # === Clear CSV if it exists ===
        if os.path.exists(csv_file):
            user_input = input(f"\n⚠️ File '{csv_file}' already exists. Clear it? (y/n): ").lower()
            if user_input == 'y':
                with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(CSVHandler.headers)
                print("🧹 CSV cleared.")
            else:
                print("➡️ Appending to existing CSV.")

        # === Clear .txt files in results folder ===
        txt_files = [f for f in os.listdir(results_folder) if f.lower().endswith(".txt")]
        if txt_files:
            user_input = input(f"\n⚠️ {len(txt_files)} text dump(s) found in '{results_folder}'. Clear them? (y/n): ").lower()
            if user_input == 'y':
                for txt_file in txt_files:
                    os.remove(os.path.join(results_folder, txt_file))
                print("🧹 Text dumps cleared.")
            else:
                print("➡️ Keeping existing text dumps.")

    @staticmethod
    def write_to_csv(data_dict, csv_file, source_file):
        complete_data = {
            "Source_File": source_file,
            "Job_Number": data_dict.get("job_number") or "Null",
            "Design_Codes": data_dict.get("design_code") or "Null",
            "Materials": data_dict.get("materials") or "Null",
            "Seismic_Resistance_System": data_dict.get("seismic_resistance_system") or "Null",
            "Risk_Category": data_dict.get("risk_category") or "Null",
            "Seismic_Design_Category": data_dict.get("seismic_design_category") or "Null",
            "Site_Class": data_dict.get("site_class") or "Null",
            "Wind_Speed": data_dict.get("wind_speed") or "Null",
            "All_Data": "See txt files in results folder"
        }

        file_exists = os.path.isfile(csv_file)
        with open(csv_file, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=CSVHandler.headers)
            if not file_exists:
                writer.writeheader()
            writer.writerow(complete_data)