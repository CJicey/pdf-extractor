import re

class SeismicResistanceSearcher:
    def __init__(self):
        self.patterns = [
            # ✅ NEW: Exact match for detailed variant
            r"STRUCTURAL\s+STEEL\s+SYSTEMS?\s+NOT\s+SPECIFICALLY\s+DETAILED\s+FOR\s+SEISMIC\s+RESISTANCE",

            # 🔹 Non-capturing + DESIGNED variant
            r"(?:STRUCTURAL\s+)?STEEL\s+SYSTEMS?\s+NOT\s+SPECIFICALLY\s+DESIGNED\s+FOR\s+SEISMIC\s+RESISTANCE",

            # 🔹 Non-capturing + DETAILED variant
            r"(?:STRUCTURAL\s+)?STEEL\s+SYSTEM\s+NOT\s+SPECIFICALLY\s+DETAILED\s+FOR\s+SEISMIC(?:\s+RESISTANCE)?",

            # 🔸 Steel Systems
            r"(?:SPECIAL|ORDINARY|INTERMEDIATE)?\s*STEEL\s+MOMENT\s+FRAMES?",
            r"(?:SPECIAL|ORDINARY|INTERMEDIATE)?\s*STEEL\s+CONCENTRICALLY\s+BRACED\s+FRAMES?",
            r"(?:SPECIAL|ORDINARY)?\s*STEEL\s+ECCENTRICALLY\s+BRACED\s+FRAMES?",
            r"BUCKLING[-\s]*RESTRAINED\s+BRACED\s+FRAMES?",
            r"SPECIAL\s+TRUSS\s+MOMENT\s+FRAMES?",
            r"(?:ORDINARY|SPECIAL)?\s*STEEL\s+PLATE\s+SHEAR\s+WALLS?",

            # 🔸 Concrete Systems
            r"(?:SPECIAL|ORDINARY|INTERMEDIATE)?\s*REINFORCED\s+CONCRETE\s+MOMENT\s+FRAMES?",
            r"(?:SPECIAL|ORDINARY)?\s*CONCRETE\s+SHEAR\s+WALLS?",
            r"CONCRETE\s+DUAL\s+SYSTEMS?",
            r"WALL[-\s]*FRAME\s+SYSTEMS?",

            # 🔸 Masonry Systems
            r"(?:SPECIAL|ORDINARY|INTERMEDIATE)?\s*(?:REINFORCED|PLAIN)?\s*MASONRY\s+SHEAR\s+WALLS?",
            r"UNREINFORCED\s+MASONRY\s+(?:SHEAR\s+)?WALLS?",

            # 🔸 Wood Systems
            r"(?:BRACED\s+)?WOOD\s+(?:SHEAR\s+WALLS?|PANELS?|DIAPHRAGMS?)",
            r"CROSS[-\s]*LAMINATED\s+TIMBER\s+(?:CLT\s+)?SHEAR\s+WALLS?",
            r"TIMBER\s+SHEAR\s+WALLS?",

            # 🔸 Cold-Formed Steel Systems
            r"COLD[-\s]*FORMED\s+(?:STEEL\s+)?(?:SHEAR\s+WALLS?|BRACED\s+FRAMES?)",
            r"LIGHT[-\s]*GAUGE\s+STEEL\s+(?:SHEAR\s+WALLS?|FRAMES?)",

            # 🔸 Precast Concrete Systems
            r"(?:ORDINARY|SPECIAL)?\s*PRECAST\s+(?:CONCRETE\s+)?SHEAR\s+WALLS?",
            r"PRECAST\s+SHEAR\s+WALLS?",

            # 🔸 Hybrid / Special Systems
            r"DUAL\s+SYSTEMS?\s+(?:WITH\s+)?(?:SPECIAL|ORDINARY|INTERMEDIATE)?\s*(?:MOMENT\s+FRAMES?|SHEAR\s+WALLS?)",
            r"WALL[-\s]*FRAME\s+COMBINATIONS?",
            r"INVERTED\s+PENDULUM\s+FRAMES?",

            # 🔸 Isolation & Energy Dissipation
            r"BASE\s+ISOLATION\s+(?:SYSTEMS?|BEARINGS?)",
            r"SEISMIC\s+ISOLATION\s+(?:SYSTEMS?|DEVICES?)",
            r"(?:ENERGY|SEISMIC)\s+DISSIPATION\s+DEVICES?",
            r"DAMPERS?|VISCOUS\s+BRACES?",
            r"PODIUM\s+STRUCTURES?\s+(?:WITH\s+)?TRANSFER\s+SLABS?",
        ]

        self.compiled = [re.compile(p, re.IGNORECASE) for p in self.patterns]

    def search(self, text):
        # Normalize and flatten text
        cleaned = re.sub(r"\s+", " ", text.upper())
        matches = []

        # Apply regex patterns
        for pattern in self.compiled:
            found = pattern.findall(cleaned)
            for match in found:
                if isinstance(match, tuple):
                    flat = " ".join(m for m in match if m).strip()
                    if flat:
                        matches.append(flat)
                elif isinstance(match, str):
                    matches.append(match.strip())

        # Deduplicate
        unique_matches = list(dict.fromkeys(matches))

        # Suppress substrings if a longer match contains them
        filtered = []
        for m in unique_matches:
            if not any((m != other and m in other) for other in unique_matches):
                filtered.append(m)

        return filtered
