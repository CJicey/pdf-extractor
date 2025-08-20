# Book of Knowledge/Dumpers/page_dump_writer.py
from __future__ import annotations
import os
from typing import List, Optional

class PageDumpWriter:
    """
    Writes a page-segmented text dump for a PDF to the SAME path/filename you pass in.
    Tries: pdfplumber → PyMuPDF; if both fail, uses form-feed splits in combined_text,
    then finally falls back to treating combined_text as a single page.
    """

    def write_by_page(
        self,
        pdf_path: str,
        out_txt_path: str,
        combined_text: Optional[str] = None
    ) -> str:
        pages: List[str] = []

        # 1) Try pdfplumber (page-native)
        try:
            import pdfplumber
            with pdfplumber.open(pdf_path) as pdf:
                pages = [(page.extract_text() or "") for page in pdf.pages]
        except Exception:
            pages = []

        # 2) Fallback to PyMuPDF (page-native)
        if not pages or not any(p.strip() for p in pages):
            try:
                import fitz  # PyMuPDF
                with fitz.open(pdf_path) as doc:
                    pages = [(pg.get_text("text") or "") for pg in doc]
            except Exception:
                pages = []

        # 3) If the combined text has form-feed separators, use them
        if (not pages or not any(p.strip() for p in pages)) and isinstance(combined_text, str) and "\f" in combined_text:
            pages = combined_text.split("\f")

        # 4) As a last resort, use the combined text as PAGE 1
        if not pages:
            pages = [combined_text or ""]

        # Ensure output folder exists
        out_dir = os.path.dirname(out_txt_path)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)

        # Write the page-segmented file (SAME path/filename you pass in)
        with open(out_txt_path, "w", encoding="utf-8") as f:
            f.write(f"FILE: {os.path.basename(pdf_path)}\nPAGES: {len(pages)}\n\n")
            for i, text in enumerate(pages, start=1):
                f.write(f"{'='*20} PAGE {i} {'='*20}\n")
                f.write((text or "").strip() or "[EMPTY]")
                f.write("\n\n")

        return out_txt_path