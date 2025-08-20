import re

class SeismicDesignCategorySearcher:
    def __init__(self):
        self.patterns = [
            # Original pattern (for =, :, is, etc.)
            re.compile(
                r'\bSEISMIC\s+DESIGN\s+CATEGORY\s*(?:=|:|\bis\b)?\s*([A-E])\b',
                re.IGNORECASE
            ),

            # NEW pattern: dot leader spacing (e.g. SEISMIC DESIGN CATEGORY ............ D)
            re.compile(
                r'\bSEISMIC\s+DESIGN\s+CATEGORY\b[\s.:=\-]*([A-E])\b',
                re.IGNORECASE
            ),
        ]

    def search(self, text):
        for pattern in self.patterns:
            match = pattern.search(text)
            if match:
                return match.group(1).upper()
        return None
