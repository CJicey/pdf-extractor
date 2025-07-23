import re

class JobNumberSearcher:
    def __init__(self):
        # Match job numbers after specific phrases with optional spacing
        self.pattern = re.compile(
            r"(?i)\b(?:B\s*&\s*P\s*Job\s*Number|Project\s*Number|Project\s*No\.?)[:\s]*"
            r"(\d{2,5}\.\d{2,5}(?:\.\d{2,5}){1,2})"
        )

    def search(self, text):
        # Normalize all whitespace (spaces, tabs, non-breaking) to regular space
        cleaned_text = re.sub(r"[^\S\r\n]+", " ", text)

        # Fix line breaks inside job numbers like 21.02.095\n.001 or with spaces between dots
        cleaned_text = re.sub(r"(\d)\s*\.\s*(\d)", r"\1.\2", cleaned_text)

        # Extract matches
        matches = self.pattern.findall(cleaned_text)

        # Deduplicate by keeping only the most complete version per base
        job_map = {}
        for job in matches:
            segments = job.split(".")
            base = ".".join(segments[:3])  # First 3 segments as unique identifier

            if base not in job_map or len(segments) > len(job_map[base].split(".")):
                job_map[base] = job

        # Preserve order of appearance
        return list(dict.fromkeys(job_map.values()))