import re

class SiteClassSearcher:
    def __init__(self):
        self.pattern = re.compile(
            r'\bSITE\s+CLASS\b[\s:=.\-]*([A-F])\b',  # Matches "SITE CLASS .... D"
            re.IGNORECASE
        )

    def search(self, text):
        matches = self.pattern.findall(text)
        valid_classes = {'A', 'B', 'C', 'D', 'E', 'F'}
        filtered = [m.upper() for m in matches if m.upper() in valid_classes]
        return ', '.join(sorted(set(filtered))) if filtered else None

    def standardize(self, site_class):
        if not site_class:
            return None
        parts = [p.strip().upper() for p in site_class.split(',')]
        valid = {'A', 'B', 'C', 'D', 'E', 'F'}
        standardized = [p for p in parts if p in valid]
        return ', '.join(sorted(set(standardized)))