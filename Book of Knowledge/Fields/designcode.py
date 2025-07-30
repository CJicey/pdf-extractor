import re

class BuildingCodeSearcher:
    def __init__(self):
        self.pattern = re.compile(
            # Design Codes
            r'\b('

            # National/state building codes
            r'(?:THE\s+)?\d{4}\s+(?:[A-Z]+\s+){1,3}BUILDING\s+CODE\b|'

            # International Building Code
            r'(?:IBC|International\s+Building\s+Code)[\s,]*\d{4}|'
            r'\d{4}[\s\n]*(?:the\s+)?(?:IBC|International\s+Building\s+Code)|'

            # Uniform Building Code
            r'(?:UBC|Uniform\s+Building\s+Code)[\s,]*\d{4}|'
            r'\d{4}[\s\n]*(?:the\s+)?(?:UBC|Uniform\s+Building\s+Code)|'

            # California Building Code
            r'(?:CBC|California\s+Building\s+Code)[\s,]*\d{4}|'
            r'\d{4}[\s\n]*(?:the\s+)?(?:CBC|California\s+Building\s+Code)|'

            # Florida Building Code
            r'(?:FBC|Florida\s+Building\s+Code)[\s,]*\d{4}|'
            r'\d{4}[\s\n]*(?:the\s+)?(?:FBC|Florida\s+Building\s+Code)|'

            # International Residential Code
            r'(?:IRC|International\s+Residential\s+Code)[\s,]*\d{4}|'
            r'\d{4}[\s\n]*(?:the\s+)?(?:IRC|International\s+Residential\s+Code)|'

            # New York City Building Code
            r'(?:NYBC|NYC\s*Building\s*Code)[\s,]*\d{4}|'
            r'\d{4}[\s\n]*(?:the\s+)?(?:NYBC|NYC\s*Building\s*Code)|'

            # North Carolina Building Code
            r'\d{4}[\s\n]*(?:the\s+)?North\s+Carolina\s+Building\s+Code|'
            r'North\s+Carolina\s+Building\s+Code[\s,]*\d{4}|'
            r'\d{4}[\s\n]*(?:the\s+)?[A-Z][a-z]+\s+State\s+Building\s+Code|'
            r'[A-Z][a-z]+\s+State\s+Building\s+Code[\s,]*\d{4}|'

            # Technical standards
            r'ASCE\s*[/\s]?7[-–]?\d{2}|'
            r'American\s+Society\s+of\s+Civil\s+Engineers\s+Standard\s+7[-–]?\d{2}|'

            # American Concrete Institute
            r'ACI\s*318[-–]?\d{2}|'
            r'American\s+Concrete\s+Institute\s+Code\s+318[-–]?\d{2}|'

            # American Institute of Steel Construction
            r'AISC\s*360[-–]?\d{2}|'
            r'AISC\s*341[-–]?\d{2}|'
            r'American\s+Institute\s+of\s+Steel\s+Construction\s+(?:Specification|Standard)\s+3(41|60)[-–]?\d{2}|'

            # American Iron and Steel Institute
            r'AISI\s*S?100[-–]?\d{2}|'

            # Masonry Code
            r'TMS\s*(402|602)[-/–]?\d{2}|'
            r'(?:The\s+)?Masonry\s+Code\s+(402|602)[-/–]?\d{2}|'

            # National Design Specification for Wood Construction
            r'NDS(?:\s*for\s*Wood\s*Construction)?|'
            r'National\s+Design\s+Specification\s+for\s+Wood\s+Construction|'

            # American Welding Society
            r'AWS\s*D1\.1[-–]?\d{2}|'
            r'American\s+Welding\s+Society\s+Code\s+D1\.1[-–]?\d{2}|'

            # AASHTO Load and Resistance Factor Design
            r'AASHTO\s*LRFD|'
            r'AASHTO\s+Load\s+and\s+Resistance\s+Factor\s+Design|'

            # National Fire Protection Association
            r'NFPA\s*5000|'
            r'National\s+Fire\s+Protection\s+Association\s+5000|'

            # British Standard
            r'BS\s*8110|'
            r'British\s+Standard\s+8110'

            r')\b',
            re.IGNORECASE
        )

    def search_codes(self, text):
        matches = [m.group(0) for m in self.pattern.finditer(text)] # find all non-overlapping matches in the input text
        return ', '.join(set(matches)) if matches else None 
    

    def standardize_design_codes(self, code_string):
        if not code_string:
            return None

        # Fix fragmented phrases
        code_string = re.sub(
            r'\b(INTERNATIONAL\s+BUILDING\s+CODE|IBC)[,\s]+(20\d{2})\b',
            r'\2 IBC',
            code_string,
            flags=re.IGNORECASE
        )

        # replacements
        replacements = {
            r'\b2018\s+International\s+Building\s+Code\b': '2018 IBC',
            r'\b2015\s+International\s+Building\s+Code\b': '2015 IBC',
            r'\b2021\s+International\s+Building\s+Code\b': '2021 IBC',
            r'\bNorth\s+Carolina\s+State\s+Building\s+Code\b': '2018 NCBC',
            r'\bNorth\s+Carolina\s+Building\s+Code\b': 'NCBC',
            r'\bNational\s+Design\s+Specification\s+for\s+Wood\s+Construction\b': 'NDS',
            r'\bASCE\s*7[-–]?\d{2}\b': lambda m: m.group(0).replace(" ", "").upper(),
            r'\bACI\s*318[-–]?\d{2}\b': lambda m: m.group(0).replace(" ", "").upper(),
            r'\bAISC\s*360[-–]?\d{2}\b': lambda m: m.group(0).replace(" ", "").upper(),
        }

        for pattern, replacement in replacements.items():
            code_string = re.sub(pattern, replacement, code_string, flags=re.IGNORECASE)

        # Normalize case, split, and deduplicate
        parts = [p.strip().upper() for p in code_string.split(',')]
        unique_cleaned = sorted(set(p for p in parts if p))

        return ', '.join(unique_cleaned)
    