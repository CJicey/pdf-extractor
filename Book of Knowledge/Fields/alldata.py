class AllDataExtractor:
    def __init__(self, raw_text=""):
        self.raw_text = raw_text

    def to_dict(self):
        return {
            "raw_text": self.raw_text
        }