import re

class MaterialsSearcher:
    def __init__(self):
        # Expanded list of structural materials
        self.materials = [
            # Concrete-related
            "CONCRETE", "PRECAST", "TILT-UP", "CAST-IN-PLACE", "REINFORCED CONCRETE",
            
            # Steel-related
            "STEEL", "STRUCTURAL STEEL", "LIGHT GAUGE", "COLD-FORMED", "HOT-ROLLED", "WELDED STEEL", "METAL DECK", "BAR JOIST",

            # Masonry-related
            "MASONRY", "CMU", "BRICK", "CONCRETE MASONRY", "STONE", "BLOCK WALL",

            # Wood-related
            "WOOD", "TIMBER", "HEAVY TIMBER", "GLULAM", "LVL", "OSB", "PLYWOOD", "ENGINEERED WOOD", "JOISTS",

            # Aluminum / other metals
            "ALUMINUM", "COPPER", "BRASS", "GALVANIZED STEEL", "ZINC",

            # Composite systems
            "COMPOSITE SLAB", "FIBERGLASS", "FRP", "CARBON FIBER", "GFRP", "PLASTIC", "PVC",

            # Structural systems / misc
            "TRUSS", "CABLE", "ANCHOR", "REBAR", "FASTENERS", "WELD", "BOLTED CONNECTION", "SHEAR WALL", "FOUNDATION"
        ]

        self.pattern = re.compile(
            r"\b(" + "|".join(re.escape(material) for material in self.materials) + r")\b",
            re.IGNORECASE
        )

    def search(self, text):
        # Normalize whitespace and extract unique uppercase matches
        cleaned_text = re.sub(r"[^\S\r\n]+", " ", text)
        matches = self.pattern.findall(cleaned_text)

        # Remove duplicates, normalize to uppercase
        unique = list(dict.fromkeys(match.upper() for match in matches))
        return unique
        