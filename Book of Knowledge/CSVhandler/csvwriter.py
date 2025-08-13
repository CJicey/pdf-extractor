import csv
import os

class CSVHandler:
    headers = [
        "Source_File", "Job_Number", "Design_Codes", "Materials", "Seismic_Resistance_System",
        "Risk_Category", "Seismic_Design_Category",
        "Site_Class", "Wind_Speed", "All_Data"
    ]

    @staticmethod
    def prompt_clear_all(csv_file, results_folder, general_notes_folder=None):
        # === Clear CSV if it exists ===
        if os.path.exists(csv_file):
            user_input = input(f"\n⚠️  File '{csv_file}' already exists. Clear it? (y/n): ").lower()
            if user_input == 'y':
                with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(CSVHandler.headers)
                print("🧹 CSV cleared.")
            else:
                print("➡️ Appending to existing CSV.")

        # === Clear raw text dump files ===
        if os.path.exists(results_folder):
            text_dumps = [
                f for f in os.listdir(results_folder)
                if f.lower().endswith("_textdump.txt")
            ]
            if text_dumps:
                user_input = input(f"\n⚠️  {len(text_dumps)} raw text dump(s) found. Clear them? (y/n): ").lower()
                if user_input == 'y':
                    for f in text_dumps:
                        os.remove(os.path.join(results_folder, f))
                    print("🧹 Raw text dumps cleared.")
                else:
                    print("➡️ Keeping existing raw text dumps.")

        # === Clear general notes files ===
        if general_notes_folder and os.path.exists(general_notes_folder):
            general_notes = [
                f for f in os.listdir(general_notes_folder)
                if f.lower().endswith(" - general notes.txt") or f.lower().startswith("general_notes_")
            ]
            if general_notes:
                user_input = input(f"\n⚠️  {len(general_notes)} general notes file(s) found. Clear them? (y/n): ").lower()
                if user_input == 'y':
                    for f in general_notes:
                        os.remove(os.path.join(general_notes_folder, f))
                    print("🧹 General Notes files cleared.")
                else:
                    print("➡️ Keeping existing General Notes files.")
        elif general_notes_folder:
            print(f"📁 General Notes folder '{general_notes_folder}' does not exist. Skipping.")

    @staticmethod
    def write_to_csv(data_dict, csv_file, source_file):
        # Ensure the parent directory for the CSV exists
        csv_dir = os.path.dirname(csv_file)
        if csv_dir:  # only mkdir if a directory is actually present in the path
            os.makedirs(csv_dir, exist_ok=True)

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
