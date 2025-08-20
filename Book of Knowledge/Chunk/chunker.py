
import re
from typing import List, Dict, Tuple, Optional

# ---------- Header patterns (expand as needed) ----------
ENGINEERING_HEADERS = [
    r"(?:STRUCTURAL\s+)?GENERAL\s+NOTES",
    r"DESIGN\s+CRITERIA",
    r"LOADS?",
    r"WIND\s+(?:CRITERIA|LOADS?)",
    r"SEISMIC\s+(?:CRITERIA|DESIGN|LOADS?)",
    r"RISK\s+CATEGORY",
    r"MATERIALS?",
    r"CONCRETE",
    r"STEEL",
    r"MASONRY",
    r"WOOD",
    r"FOUNDATION(?:S)?",
    r"GEOTECH(?:NICAL)?",
    r"DETAIL(?:S)?",
    r"SCHEDULES?",
    r"ABBREVIATIONS",
    r"(?:DRAWING|SHEET)\s+INDEX",
    r"PROJECT\s+INFORMATION",
]

HEADER_REGEX = re.compile(
    r"^\s*(?:"
    + r"|".join(ENGINEERING_HEADERS)
    + r")\b\s*:?$",
    flags=re.IGNORECASE | re.MULTILINE
)

PARA_SPLIT = re.compile(r"\n\s*\n+")  # blank-line separated paragraphs

def _split_by_headers(text: str) -> List[Tuple[str, str]]:
    matches = list(HEADER_REGEX.finditer(text))
    if not matches:
        return []
    blocks: List[Tuple[str, str]] = []
    for i, m in enumerate(matches):
        header_line = m.group(0).strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end].strip()
        if body:
            blocks.append((header_line, body))
    return blocks

def _chunk_paragraphs(text: str, max_len: int = 1200, overlap: int = 150) -> List[str]:
    paras = [p.strip() for p in PARA_SPLIT.split(text) if p.strip()]
    chunks: List[str] = []
    buf = ""

    def _flush():
        nonlocal buf
        if buf.strip():
            chunks.append(buf.strip())
            buf = ""

    for para in paras:
        if len(para) <= max_len:
            if len(buf) + len(para) + 2 <= max_len:
                buf = (buf + "\n\n" + para).strip()
            else:
                _flush()
                buf = para
        else:
            _flush()
            sentences = re.split(r"(?<=[\.\?\!])\s+", para)
            cur = ""
            for s in sentences:
                if len(s) > max_len:
                    start = 0
                    while start < len(s):
                        end = start + max_len
                        chunks.append(s[start:end].strip())
                        start = end - overlap
                    cur = ""
                else:
                    if len(cur) + len(s) + 1 <= max_len:
                        cur = (cur + " " + s).strip()
                    else:
                        if cur:
                            chunks.append(cur.strip())
                        cur = s.strip()
            if cur:
                chunks.append(cur.strip())
            cur = ""

    _flush()

    if overlap > 0 and len(chunks) > 1:
        with_overlap: List[str] = []
        for i, c in enumerate(chunks):
            if i == 0:
                with_overlap.append(c)
            else:
                prev_tail = chunks[i - 1][-overlap:]
                merged = (prev_tail + " " + c).strip()
                with_overlap.append(merged)
        chunks = with_overlap

    return chunks

def chunk_pages(
    pages: List[str],
    max_chunk_chars: int = 1200,
    overlap: int = 150,
) -> List[Dict]:
    results: List[Dict] = []
    for page_idx, page_text in enumerate(pages, start=1):
        text = (page_text or "").strip()
        if not text:
            continue

        header_blocks = _split_by_headers(text)
        if header_blocks:
            for header, body in header_blocks:
                if len(body) <= max_chunk_chars:
                    results.append({
                        "page": page_idx,
                        "header": header,
                        "text": body,
                        "strategy": "header",
                    })
                else:
                    subchunks = _chunk_paragraphs(body, max_len=max_chunk_chars, overlap=overlap)
                    for sc in subchunks:
                        results.append({
                            "page": page_idx,
                            "header": header,
                            "text": sc,
                            "strategy": "header+para",
                        })
        else:
            subchunks = _chunk_paragraphs(text, max_len=max_chunk_chars, overlap=overlap)
            for sc in subchunks:
                results.append({
                    "page": page_idx,
                    "header": None,
                    "text": sc,
                    "strategy": "para",
                })
    return results

# --------- Convenience: read page-dump file and chunk ----------
PAGE_MARKER = re.compile(r"^=+\s*PAGE\s+(\d+)\s*=+$", re.IGNORECASE | re.MULTILINE)

def chunk_from_page_dump_file(dump_path: str, max_chunk_chars: int = 1200, overlap: int = 150) -> List[Dict]:
    """
    Accepts a text file created by your PageDumpWriter using markers like:
    ==================== PAGE 1 ====================
    Returns chunk dicts with page/header/strategy/text.
    """
    with open(dump_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # Split by markers; keep order
    parts = PAGE_MARKER.split(content)
    # split returns: [pre, page1num, page1content, page2num, page2content, ...]
    pages: List[str] = []
    if len(parts) >= 3:
        # skip the 'pre' chunk at index 0
        for i in range(1, len(parts), 2):
            page_text = parts[i+1] if (i+1) < len(parts) else ""
            pages.append(page_text.strip())
    else:
        # no markers → assume whole file is page 1
        pages = [content]

    return chunk_pages(pages, max_chunk_chars=max_chunk_chars, overlap=overlap)
