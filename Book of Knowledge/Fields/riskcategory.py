import re

class RiskCategorySearcher:
    def __init__(self):
        self.pattern = re.compile(
            r'\b(?:SEISMIC\s+)?RISK\s+(?:CATEGORY|CAT\.?)\s*[:=\\-]?\s*(I{1,3}|IV|1|2|3|4)\b'
        )

    def search(self, text):
        matches = self.pattern.findall(text)
        valid_roman = {'I', 'II', 'III', 'IV'}
        valid_numeric = {'1', '2', '3', '4'}
        filtered = [m for m in matches if m in valid_roman or m in valid_numeric]

        return ', '.join(sorted(set(filtered))) if filtered else None

    def standardize(self, category):
        if not category:
            return None
        replacements = {'1': 'I', '2': 'II', '3': 'III', '4': 'IV'}
        parts = [p.strip() for p in category.split(',')]
        standardized = [replacements.get(p, p) for p in parts if p in replacements or p in replacements.values()]

        return ', '.join(sorted(set(standardized)))