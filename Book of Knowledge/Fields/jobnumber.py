from collections import Counter
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

        # 🔹 Step 2.5 (NEW): short 4–6 digit label-anchored numbers (e.g., 19145)
        self.pattern_label_shortdigits = re.compile(
            r"(?i)\b(?:B\s*&\s*P\s*Job\s*Number|Project\s*Number|Project\s*No\.?)"
            r"[\s:=\-]{0,10}"
            r"(\d{4,6})(?![.\d])"
        )

        # Step 3: final fallback (capture anything word-like after the label)
        self.pattern_final_anything = re.compile(
            r"(?i)\b(?:B\s*&\s*P\s*Job\s*Number|Project\s*Number|Project\s*No\.?)"
            r"[\s:=\-]{0,10}"
            r"([A-Z0-9.\-_/]{3,20})"  # match alphanumeric-like code
        )

        # 🔹 NEW: helper regex/sets for cleanup
        self.pattern_year_dash = re.compile(r"\b20\d{2}-\d{2,3}\b")  # e.g., 2019-95 / 2020-101
        self.stopwords = {"DATE", "REVISION", "REVISIONS", "SHEET", "SHEETS", "DRAWING", "DRAWINGS"}

    def _prefer_longest_dotted(self, matches):
        # Prefer job numbers with 2+ dots (like 22.00.092)
        dotted = [m for m in matches if m.count('.') >= 2]
        return dotted if dotted else matches

    # 🔹 NEW: pick the most frequent 4–6 digit "core" (e.g., 19145 from 19145.1/.2/.3)
    def _most_frequent_core_short_digits(self, candidates):
        cores = []
        for c in candidates:
            m = re.match(r"^(\d{4,6})", str(c))
            if m:
                cores.append(m.group(1))
        if not cores:
            return None
        counter = Counter(cores)
        # most common by frequency, then numeric tie-breaker
        best_core, _ = max(counter.items(), key=lambda kv: (kv[1], int(kv[0])))
        return best_core

    def search(self, text):
        # Clean and normalize whitespace
        cleaned_text = re.sub(r"[^\S\r\n]+", " ", text)
        cleaned_text = cleaned_text.replace("\n", " ").replace("\r", " ")

        # 🛠️ Fix common formatting errors
        # 1. Turn commas between digits into dots (e.g. 20.00,092 → 20.00.092)
        cleaned_text = re.sub(r"(?<=\d),(?=\d)", ".", cleaned_text)
        # 2. Collapse broken dotted numbers
        cleaned_text = re.sub(r"(\d)\s*\.\s*(\d)", r"\1.\2", cleaned_text)
        for _ in range(2):
            cleaned_text = re.sub(r"(\d+)\s*\.\s*(\d+)", r"\1.\2", cleaned_text)

        # Debug: snippet near PROJECT
        snippet = re.search(r"(PROJECT.{0,100})", cleaned_text, re.IGNORECASE)
        if snippet:
            print("📝 OCR Snippet Near 'PROJECT':", snippet.group(1))
        else:
            print("🚫 No 'PROJECT' snippet found.")

        # Helper to numerically compare job numbers
        def to_number(val):
            try:
                return float(re.sub(r"[^\d.]", "", val).replace(".", ""))
            except:
                return 0

        # Step 1: Dotted (unchanged)
        matches = self.pattern_dotted.findall(cleaned_text)
        if matches:
            matches = self._prefer_longest_dotted(matches)
            print("✅ Dotted Job Numbers Found (filtered):", matches)
            largest = max(matches, key=to_number)
            return [largest]

        # Step 2: Pure Digits (unchanged)
        matches = self.pattern_fallback_digits.findall(cleaned_text)
        if matches:
            print("⚠️ Fallback Pure-Digit Job Numbers Found:", matches)
            largest = max(matches, key=to_number)
            return [largest]

        # 🔹 Step 2.5: Short 4–6 digit label-anchored numbers (new)
        short_digits = self.pattern_label_shortdigits.findall(cleaned_text)
        if short_digits:
            print("🔎 Short 4–6 digit candidates (label-anchored):", short_digits)
            best_core = self._most_frequent_core_short_digits(short_digits)
            if best_core:
                return [best_core]

        # Step 3: Final fallback (alphanumeric) — now with cleanup
        matches = self.pattern_final_anything.findall(cleaned_text)
        if matches:
            # Filter junk tokens and year-dash patterns
            filtered = []
            for m in matches:
                up = str(m).strip().upper()
                if up in self.stopwords:
                    continue
                if self.pattern_year_dash.fullmatch(up):
                    continue
                # toss obvious non-job tokens that are too "wordy"
                if up.isalpha():
                    continue
                filtered.append(m)

            if filtered:
                # Try frequency of 4–6 digit core first (handles 19145 vs 19145.1/.2/.3)
                best_core = self._most_frequent_core_short_digits(filtered)
                if best_core:
                    print("🧪 Final Fallback (filtered): using most-frequent core:", best_core)
                    return [best_core]

                # else keep your original "largest numeric" behavior
                print("🧪 Final Fallback: Alphanumeric Job Reference Found (filtered):", filtered)
                largest = max(filtered, key=to_number)
                return [largest]

        # Step 4: Raw dotted number fallback (standalone like 22.00.092) (unchanged)
        fallback_dotted_raw = re.findall(r"\b(\d{2,6}(?:\.\d{2,6}){2,3})\b", cleaned_text)
        if fallback_dotted_raw:
            fallback_dotted_raw = self._prefer_longest_dotted(fallback_dotted_raw)
            print("🧩 Standalone fallback dotted numbers:", fallback_dotted_raw)
            return [max(fallback_dotted_raw, key=to_number)]

        print("🚫 No job number found.")
        return []
