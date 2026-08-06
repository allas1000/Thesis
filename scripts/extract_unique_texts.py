"""Write the unique resumes and job descriptions out as plain text.

Reads data/processed/final_with_text_cleaned.csv and writes one entry per
unique Resume_index and per unique Job_index, each headed by its full SHA-256
index and followed by the cleaned text. No other metadata is included.

    data/processed/resumes_unique.txt   30 resumes
    data/processed/jobs_unique.txt      15 job descriptions

Plain text is the format the manual demographic cleaning was carried out in.
The hand-neutralised results are in data/processed/neutralised/.

The resume output contains names, contact details, and profile links belonging
to real job seekers, so .gitignore excludes it. Do not commit it. The job
output carries no personal data and is tracked.

Run from the repository root:

    python scripts/extract_unique_texts.py
"""

from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
INPUT_CSV = REPO_ROOT / "data" / "processed" / "final_with_text_cleaned.csv"
OUTPUT_RESUMES = REPO_ROOT / "data" / "processed" / "resumes_unique.txt"
OUTPUT_JOBS = REPO_ROOT / "data" / "processed" / "jobs_unique.txt"

SEPARATOR = "=" * 80


def write_unique(df, id_col, text_col, path):
    """Write one entry per unique value of id_col, carrying id and text only."""
    unique = df.drop_duplicates(subset=id_col).reset_index(drop=True)
    with open(path, "w", encoding="utf-8") as f:
        for _, row in unique.iterrows():
            text = row[text_col] if isinstance(row[text_col], str) else ""
            f.write(SEPARATOR + "\n")
            f.write(f"{id_col}: {row[id_col]}\n")
            f.write(SEPARATOR + "\n\n")
            f.write(text)
            f.write("\n\n")
    print(f"Wrote {path.relative_to(REPO_ROOT)}: {len(unique)} entries")


def main():
    if not INPUT_CSV.exists():
        print(f"ERROR: cannot find {INPUT_CSV}.")
        print("Run scripts/clean_text_columns.py first.")
        return

    df = pd.read_csv(INPUT_CSV)
    print(f"Loaded {INPUT_CSV.name}: {df.shape[0]:,} rows")

    OUTPUT_RESUMES.parent.mkdir(parents=True, exist_ok=True)
    write_unique(df, "Resume_index", "Resume_text", OUTPUT_RESUMES)
    write_unique(df, "Job_index", "Job_text", OUTPUT_JOBS)


if __name__ == "__main__":
    main()