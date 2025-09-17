import re

class WindSpeedSearcher:
    def __init__(self):
        # List of regex patterns to match various wind speed formats
        self.patterns = [
            # Match formats like "VULT = 115 MPH", "Ultimate Wind Speed: 125 mph", etc.
            re.compile(
                r'\b(?:VULT|V\s*ULT|V|ULTIMATE\s+WIND\s+SPEED|BASIC\s+WIND\s+SPEED)'
                r'(?:\s*\([^)]*\))?'                # optional parentheses content
                r'\s*[:=\u2013\-]?\s*'             # optional punctuation or dash
                r'(\d{2,3})\s*(?:mph|m\.?p\.?h\.?)\b',
                re.IGNORECASE
            ),
            # Fallback: any standalone "### mph" match
            re.compile(
                r'\b(\d{2,3})\s*(?:mph|m\.?p\.?h\.?)\b',
                re.IGNORECASE
            )
        ]

    def search(self, text):
        for pattern in self.patterns:
            match = pattern.search(text)
            if match:
                return f"{match.group(1)} mph"
        return None