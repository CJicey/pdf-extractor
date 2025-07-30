import re

class ProjectNameSearcher:
    def __init__(self):
        self.patterns = [
            r"PROJECT\s*NAME\s*[:\-–]?\s*(.+)",                     
            r"(?:PROJECT\s*TITLE|TITLE)\s*[:\-–]?\s*(.+)",              
            r"FOR\s+(.+?)(?:\s{2,}|$)",                                 
        ]
        self.blacklist = {
            "ISSUED FOR CONSTRUCTION", "GENERAL NOTES", "SHEET LIST",
            "COPYRIGHT", "PROJECT NO", "DATE", "REVISIONS", "COVER SHEET",
        }

    def search(self, text: str) -> str:
        lines = text.split('\n')
        cleaned_lines = [line.strip() for line in lines if line.strip()]

        for line in cleaned_lines:
            for pattern in self.patterns:
                match = re.search(pattern, line, flags=re.IGNORECASE)
                if match:
                    name = match.group(1).strip()
                    if self._valid_name(name):
                        return name

        for line in cleaned_lines:
            if line.isupper() and len(line.split()) >= 3 and self._valid_name(line):
                return line.strip()

        return "Unknown"

    def _valid_name(self, name: str) -> bool:
        if not name:
            return False
        name_upper = name.upper()
        if any(phrase in name_upper for phrase in self.blacklist):
            return False
        return 5 <= len(name) <= 100