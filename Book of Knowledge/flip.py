# flip.py — run with no arguments; choose the file in a dialog.
from pathlib import Path
import sys

# ---- Paste the lines you want flipped (exactly as they appear) ----
SELECTED_BLOCK = """notgnivoC 
ERA
SNGISED
DNA
SGNIWARD
ESEHT
DRANITS
FO
YTREPORP
EHT
TON
LLAHS
DNA
.CNI
,ERUTCETIHCRA
EHT
TUOHTIW
DECUDORPER
EB
egarotS
fleS
EREW
YEHT
.NOISSIMREP
S'TCETIHCRA
CIFICEPS
SIHT
NO
ESU
ROF
DERAPERP
EUSSI
EHT
HTIW
NOITCNUJNOC
NI
ETIS
ESU
ROF
ELBATIUS
TON
ERA
DNA
ETAD
RETAL
A TA
RO
ETIS
TNEREFFID
A
NO
EB
TSUM
SNOISNEMID
LLA
.EMIT
DNA
ROTCARTNOC
EHT
YB
DEIFIREV
YNA
FO
DEIFITON
TCETIHCRA
EHT
GNIDEECORP
EROFEB
SEICNAPERCSID
ELACS
TON
OD
.NOITCURTSNOC
HTIW
.SGNIWARD
091
yawhgiH
AL
,notgnivoC"""

def flip_selected_lines_text(text: str, targets: set[str]) -> tuple[str, int]:
    """Reverse characters for any line whose stripped text is in `targets`."""
    out = []
    changed = 0
    for line in text.splitlines(keepends=True):
        # Preserve exact newline characters
        if line.endswith("\r\n"):
            core, nl = line[:-2], "\r\n"
        elif line.endswith("\n") or line.endswith("\r"):
            core, nl = line[:-1], line[-1]
        else:
            core, nl = line, ""

        if core.strip() in targets:
            out.append(core[::-1] + nl)
            changed += 1
        else:
            out.append(line)
    return "".join(out), changed

def choose_file_interactively() -> Path | None:
    """Try a GUI file picker; fall back to console input."""
    try:
        # Tk is usually available with Python on Windows
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        path = filedialog.askopenfilename(
            title="Choose the text dump to fix",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        root.update()
        root.destroy()
        return Path(path) if path else None
    except Exception:
        # Fallback: console prompt
        try:
            p = input("Enter path to your text file: ").strip().strip('"')
            return Path(p) if p else None
        except (EOFError, KeyboardInterrupt):
            return None

def main():
    targets = {ln.strip() for ln in SELECTED_BLOCK.splitlines() if ln.strip()}
    in_path = choose_file_interactively()
    if not in_path:
        print("No file selected. Exiting.")
        sys.exit(1)
    if not in_path.exists():
        print(f"File not found:\n  {in_path}")
        sys.exit(1)

    original = in_path.read_text(encoding="utf-8", errors="ignore")
    fixed_text, changed = flip_selected_lines_text(original, targets)

    # Backup original
    backup_path = in_path.with_suffix(in_path.suffix + ".bak")
    backup_path.write_text(original, encoding="utf-8")

    # Write fixed output
    out_path = in_path.with_name(in_path.stem + "_fixed" + in_path.suffix)
    out_path.write_text(fixed_text, encoding="utf-8")

    print(f"✓ Flipped {changed} line(s)")
    print(f"→ Backup saved: {backup_path}")
    print(f"→ Fixed file:   {out_path}")

if __name__ == "__main__":
    main()