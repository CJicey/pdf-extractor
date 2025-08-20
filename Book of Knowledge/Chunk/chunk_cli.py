
import argparse, json, sys
from pathlib import Path
from Extractor.chunker import chunk_from_page_dump_file

def main():
    ap = argparse.ArgumentParser(description="Chunk a page-dump txt into JSONL chunks")
    ap.add_argument("dump_file", help="Path to page-dump .txt")
    ap.add_argument("--out", help="Output JSONL path (default: <dump_file>.chunks.jsonl)")
    ap.add_argument("--max", type=int, default=1200, help="Max chunk chars (default: 1200)")
    ap.add_argument("--overlap", type=int, default=150, help="Overlap chars (default: 150)")
    args = ap.parse_args()

    out_path = args.out or (str(args.dump_file) + ".chunks.jsonl")
    chunks = chunk_from_page_dump_file(args.dump_file, max_chunk_chars=args.max, overlap=args.overlap)

    with open(out_path, "w", encoding="utf-8") as f:
        for ch in chunks:
            f.write(json.dumps(ch, ensure_ascii=False) + "\n")

    print(f"Wrote {len(chunks)} chunks → {out_path}")

if __name__ == "__main__":
    main()
