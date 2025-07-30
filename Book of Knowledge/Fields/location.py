import re

class LocationSearcher:
    def __init__(self):
        # Keywords that typically appear in address blocks
        self.location_keywords = [
            r"\b(?:SUITE|STE|BUILDING|BLDG|ROOM|RM)\b",
            r"\b(?:STREET|ST|AVENUE|AVE|ROAD|RD|BOULEVARD|BLVD|LANE|LN|PARKWAY|PKWY|DRIVE|DR|COURT|CT|WAY)\b",
            r"\b(?:GEORGIA|TEXAS|FLORIDA|ALABAMA|NORTH CAROLINA|SOUTH CAROLINA|TENNESSEE|GA|TX|FL|AL|NC|SC|TN)\b",
            r"\b\d{5}(?:-\d{4})?\b"  # ZIP code
        ]

    def search(self, text: str) -> str:
        lines = text.split('\n')
        candidates = []

        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue

            if any(re.search(kw, line, re.IGNORECASE) for kw in self.location_keywords):
                # Capture surrounding context if multiple-line address
                full_context = "\n".join(lines[max(0, i - 1): i + 2])
                candidates.append(full_context.strip())

        # Return the first valid-looking match or fallback
        for cand in candidates:
            if 10 <= len(cand) <= 150:
                return cand

        return "Unknown"