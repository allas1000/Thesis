"""Remove scraping noise from the recovered resume and job text.

Reads data/processed/final_with_text.csv and writes
data/processed/final_with_text_cleaned.csv, leaving the original untouched.
This pass removes artefacts of how the corpora were scraped. It does not touch
demographic markers, which were removed by hand afterwards.

The six steps run in order.

    1. Strip HTML tags. The dataset carries only <span class="hl"> tags left by
       keyword highlighting, but the pattern is general.
    2. Repair mojibake byte sequences. Defensive only, since pandas reads the
       current file correctly. It guards against a future re-export through a
       tool that mis-encodes.
    3. Replace the non-breaking space U+00A0 with a normal space.
    4. Remove the zero-width space U+200B.
    5. Replace U+00C6 with a curly apostrophe. The dataset has 15 garbled
       apostrophes of this form, where "accountantAEs" should read
       "accountant's".
    6. Collapse the whitespace runs the steps above leave behind, and trim.

Smart punctuation is kept as proper Unicode, so the text stays faithful to the
original.

Cleaned text will not re-hash to the original Resume_index or Job_index values,
by design. Those columns remain the identifiers. The cleaned text is the input
to scoring and not a re-derivable artefact.

The output contains names, contact details, and profile links belonging to real
job seekers, so .gitignore excludes it. Do not commit it.

Run from the repository root:

    python scripts/clean_text_columns.py
"""

import re
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
INPUT_CSV = REPO_ROOT / "data" / "processed" / "final_with_text.csv"
OUTPUT_CSV = REPO_ROOT / "data" / "processed" / "final_with_text_cleaned.csv"

TEXT_COLS = ["Resume_text", "Job_text"]

HTML_TAG_RE = re.compile(r"<[^>]+>")
WHITESPACE_RUN_RE = re.compile(r"\s+")

# Ordered longest first, so str.replace cannot partly consume a longer pattern.
MOJIBAKE_FIXES = [
    ("â€¦", "…"),       # ellipsis (U+2026)
    ("â€¢", "•"),       # bullet (U+2022)
    ("â€™", "’"),       # right single quote (U+2019)
    ("â€˜", "‘"),       # left single quote (U+2018)
    ("â€\x9d", "”"),    # right double quote (U+201D)
    ("â€\x9c", "“"),    # left double quote (U+201C)
    ("â€\x94", "—"),    # em dash (U+2014)
    ("â€\x93", "–"),    # en dash (U+2013)
]


def clean_text(text):
    """Clean one text value. Non-strings such as NaN pass through unchanged."""
    if not isinstance(text, str):
        return text

    # 1. HTML tags.
    out = HTML_TAG_RE.sub("", text)

    # 2. Mojibake. Defensive, and normally a no-op on this dataset.
    for bad, good in MOJIBAKE_FIXES:
        if bad in out:
            out = out.replace(bad, good)

    # 3 to 5. Single-character fixes.
    out = (
        out
        .replace("\u00a0", " ")   # non-breaking space becomes a normal space
        .replace("\u200b", "")    # zero-width space, removed
        .replace("\u00c6", "’")   # garbled curly apostrophe
    )

    # 6. Whitespace runs.
    out = WHITESPACE_RUN_RE.sub(" ", out).strip()
    return out


def main():
    if not INPUT_CSV.exists():
        print(f"ERROR: cannot find {INPUT_CSV}.")
        print("Run scripts/match_hashes.py first.")
        return

    df = pd.read_csv(INPUT_CSV)
    print(f"Loaded {INPUT_CSV.name}: {df.shape[0]:,} rows × {df.shape[1]} cols")

    # Count the noise items before cleaning, for the summary below.
    counts = {
        "<span> open/close tags":           0,
        "Other HTML tags":                  0,
        "Non-breaking spaces (U+00A0)":     0,
        "Zero-width spaces (U+200B)":       0,
        "Garbled apostrophes (Æ → ’)":      0,
        "Mojibake sequences (defensive)":   0,
    }
    span_re = re.compile(r"<span[^>]*>|</span>")
    other_html_re = re.compile(r"<(?!/?span\b)[^>]+>", re.IGNORECASE)

    for col in TEXT_COLS:
        if col not in df.columns:
            print(f"WARNING: column {col!r} not found, skipping")
            continue
        joined = "\n".join(df[col].fillna("").tolist())
        counts["<span> open/close tags"]       += len(span_re.findall(joined))
        counts["Other HTML tags"]              += len(other_html_re.findall(joined))
        counts["Non-breaking spaces (U+00A0)"] += joined.count("\u00a0")
        counts["Zero-width spaces (U+200B)"]   += joined.count("\u200b")
        counts["Garbled apostrophes (Æ → ’)"]  += joined.count("\u00c6")
        for bad, _ in MOJIBAKE_FIXES:
            counts["Mojibake sequences (defensive)"] += joined.count(bad)

    before_chars = sum(
        df[col].fillna("").str.len().sum()
        for col in TEXT_COLS if col in df.columns
    )

    # Clean each text column.
    for col in TEXT_COLS:
        if col in df.columns:
            df[col] = df[col].apply(clean_text)

    after_chars = sum(
        df[col].fillna("").str.len().sum()
        for col in TEXT_COLS if col in df.columns
    )

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")

    print()
    print("Cleanup summary (across both text columns):")
    for label, n in counts.items():
        print(f"  {n:7,d}  {label}")

    print()
    saved = before_chars - after_chars
    pct = 100 * saved / before_chars if before_chars else 0
    print(
        f"Total characters in {' + '.join(TEXT_COLS)}: "
        f"{before_chars:,} → {after_chars:,}  "
        f"(removed {saved:,}, {pct:.2f}%)"
    )
    print(f"Wrote {OUTPUT_CSV.relative_to(REPO_ROOT)}")
    print("Original final_with_text.csv left untouched.")


if __name__ == "__main__":
    main()
