import re

class JobNumberSearcher:
    def __init__(self):
        # Step 1: dotted format (22.00.062.02, 19150.000)
        self.pattern_dotted = re.compile(
            r"(?i)\b(?:B\s*&\s*P\s*Job\s*Number|Project\s*Number|Project\s*No\.?)"
            r"[\s:=\-]{0,10}"
            r"(\d{2,6}(?:\.\d{2,6}){1,3})"
        )

        # Step 2: pure digits (70205085)
        self.pattern_fallback_digits = re.compile(
            r"(?i)\b(?:B\s*&\s*P\s*Job\s*Number|Project\s*Number|Project\s*No\.?)"
            r"[\s:=\-]{0,10}"
            r"(\d{8,10})"
        )

        # Step 3: final fallback (capture anything word-like after the label)
        self.pattern_final_anything = re.compile(
            r"(?i)\b(?:B\s*&\s*P\s*Job\s*Number|Project\s*Number|Project\s*No\.?)"
            r"[\s:=\-]{0,10}"
            r"([A-Z0-9.\-_/]{3,20})"  # match alphanumeric-like code
        )

    def search(self, text):
        # Clean and normalize
        cleaned_text = re.sub(r"[^\S\r\n]+", " ", text)
        cleaned_text = cleaned_text.replace("\n", " ").replace("\r", " ")
        cleaned_text = re.sub(r"(\d)\s*\.\s*(\d)", r"\1.\2", cleaned_text)

        # Debug: snippet near PROJECT
        snippet = re.search(r"(PROJECT.{0,100})", cleaned_text, re.IGNORECASE)
        if snippet:
            print("📝 OCR Snippet Near 'PROJECT':", snippet.group(1))
        else:
            print("🚫 No 'PROJECT' snippet found.")

        # Step 1: Dotted
        matches = self.pattern_dotted.findall(cleaned_text)
        if matches:
            print("✅ Dotted Job Numbers Found:", matches)
            return list(dict.fromkeys(matches))

        # Step 2: Pure Digits
        matches = self.pattern_fallback_digits.findall(cleaned_text)
        if matches:
            print("⚠️ Fallback Pure-Digit Job Numbers Found:", matches)
            return list(dict.fromkeys(matches))

        # Step 3: Final fallback (alphanumeric code like SLR.019)
        matches = self.pattern_final_anything.findall(cleaned_text)
        if matches:
            print("🧪 Final Fallback: Alphanumeric Job Reference Found:", matches)
            return list(dict.fromkeys(matches))

        print("🚫 No job number found.")
        return []