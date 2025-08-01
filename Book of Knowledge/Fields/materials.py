import re

class MaterialsSearcher:
    def __init__(self):
        self.materials = [
            # Concrete-related
            "REINFORCED CONCRETE", "CAST-IN-PLACE", "TILT-UP", "PRECAST", "CONCRETE", "PRECAST CONCRETE",
            "STRUCTURAL PRECAST CONCRETE", "TILT - UP CONCRETE PANELS", "CAST-IN-PLACE CONCRETE",

            # Steel-related
            "STEEL ROOF DECK", "STEEL JOISTS", "STRUCTURAL STEEL", "WELDED STEEL", 
            "HOT-ROLLED", "LIGHT GAUGE", "COLD-FORMED", "METAL DECK", "BAR JOIST",
            "STEEL DECK", "STEEL", "JOIST GIRDERS", " STEEL COMPOSITE FLOOR", "COLD-FORMED STEEL STRUCTURAL FRAMING",

            # Masonry-related
            "CONCRETE MASONRY", "BLOCK WALL", "MASONRY", "STONE", "BRICK", "CMU", 
            "STRUCTURAL MASONRY",

            # Wood-related
            "HEAVY TIMBER", "ENGINEERED WOOD", "PLYWOOD", "GLULAM", "TIMBER",
            "JOISTS", "OSB", "WOOD", "LVL", "PREFABRICATED WOOD TRUSSES", "LUMBER",

            # Aluminum / other metals
            "GALVANIZED STEEL", "ALUMINUM", "COPPER", "BRASS", "ZINC",

            # Composite systems
            "COMPOSITE SLAB", "CARBON FIBER", "FIBERGLASS", "GFRP", "FRP",
            "PLASTIC", "PVC",

            # Structural systems / misc
            "BOLTED CONNECTION", "SHEAR WALL", "FOUNDATION", "FASTENERS",
            "ANCHOR", "REBAR", "TRUSS", "CABLE", "WELD",

            # Deep foundations / additions
            "DRILLED PIERS"
        ]

        # Sort by length descending to prioritize multi-word phrases
        self.materials.sort(key=lambda x: -len(x))
        self.pattern = re.compile(
            r"(?<!\w)(" + "|".join(re.escape(material) for material in self.materials) + r")(?!\w)", 
            re.IGNORECASE
        )

    def search(self, text):
        cleaned_text = re.sub(r"[^\S\r\n]+", " ", text)
        matches = self.pattern.findall(cleaned_text)
        unique = list(dict.fromkeys(match.upper() for match in matches))
        return unique