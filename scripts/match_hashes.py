"""Recover the resume and job text behind Kim et al.'s (2025) published hashes.

SHA-256 cannot be inverted, but it is deterministic. Re-running Kim et al.'s
preprocessing on the same raw datasets reproduces their hashes, and this time
the source text is kept alongside each one. Intersecting the target hashes from
final.csv with the recomputed hashes identifies the matches, and a dictionary
lookup recovers the text. The hash function and the loading logic below are
copied from Kim et al.'s utilities.py and setup_data.py so that the recomputed
hashes match theirs exactly.

Inputs, relative to the repository root:
    data/kim_garg/final.csv         (tracked)
    data/raw/upwork-jobs.csv        (download, see data/raw/README.md)
    data/raw/resume_samples.txt     (download, see data/raw/README.md)
    data/raw/Resume.csv             (download, see data/raw/README.md)

Writes data/processed/final_with_text.csv, the 450 hand-labelled rows with
resume and job text and metadata attached.

The output contains names, contact details, and profile links belonging to real
job seekers, so .gitignore excludes it. Do not commit it.

Run from the repository root:

    python scripts/match_hashes.py
"""

import hashlib
from pathlib import Path

import pandas as pd

# Paths resolve relative to this script, so the repository stays portable.
HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
RAW_DIR = REPO_ROOT / "data" / "raw"        # external datasets, not tracked
KG_DIR = REPO_ROOT / "data" / "kim_garg"    # Kim et al.'s final.csv
OUTPUT_DIR = REPO_ROOT / "data" / "processed"

# Columns kept in the enriched CSV.
KEEP_COLS = [
    "index",
    "job_cluster",
    "job_title",
    "resume_cluster",
    "resume_category",
    "resume_source",
    "Resume_index",
    "Job_index",
    "Resume_text",
    "Job_text",
    "Hand_firm_rate_comb",
    # "Hand_app_rate_comb" is identical to Hand_firm_rate_comb. Uncomment if needed.
]


def hash_id(x):
    """Verbatim from Kim et al.'s utilities.py. Do not alter."""
    return hashlib.sha256(str(x).encode()).hexdigest()


def split_and_validate(row):
    parts = row.split(":::")
    if len(parts) == 3:
        return {"id": parts[0], "occupation": parts[1], "resume": parts[2]}
    return None


def load_raw_data(data_dir):
    """Replicate Kim et al.'s setup_data.load_raw_data.

    Builds the job Content column, concatenates the two resume sources, and
    applies their 5,000 to 10,000 character length filter. The steps must stay
    identical to theirs or the recomputed hashes will not match. Two metadata
    columns, category and source, are retained beyond what they keep, since
    neither enters the hash.

    Returns (resume_df, jobs_df).
    """
    jobs_df = pd.read_csv(data_dir / "upwork-jobs.csv")
    jobs_df["Content"] = (
        "Job Title: " + jobs_df["title"] + "\nDescription: " + jobs_df["description"]
    )

    # Resume source 1, resume_samples.txt from florex/resume_corpus. Its
    # occupation string holds several roles, so the first field is the category.
    with open(data_dir / "resume_samples.txt", "r", encoding="windows-1252") as f:
        txt = f.read()
    rows = [split_and_validate(r) for r in txt.split("\n") if split_and_validate(r)]
    b = pd.DataFrame(rows).drop_duplicates(subset="resume")
    b["category"] = b["occupation"].str.split(";").str[0].str.strip()
    b["source"] = "resume_samples.txt"
    b = b.rename(columns={"resume": "Resume"})[["Resume", "category", "source"]]

    # Resume source 2, Resume.csv from Bhawal on Kaggle, which has a Category column.
    a = pd.read_csv(data_dir / "Resume.csv")
    a = a.rename(columns={"Resume_str": "Resume", "Category": "category"})
    a["source"] = "Resume.csv"
    a = a[["Resume", "category", "source"]]

    resume_df = pd.concat([b, a], ignore_index=True)
    resume_df = resume_df[
        (resume_df["Resume"].str.len() > 5000)
        & (resume_df["Resume"].str.len() < 10000)
    ].reset_index(drop=True)

    return resume_df, jobs_df


def main():
    print(f"Repo root:      {REPO_ROOT}")
    print(f"Raw data:       {RAW_DIR}")
    print(f"Kim & Garg:     {KG_DIR}")
    print(f"Output:         {OUTPUT_DIR}")

    required = {
        KG_DIR / "final.csv": "tracked in git under data/kim_garg/",
        RAW_DIR / "upwork-jobs.csv": "see data/raw/README.md",
        RAW_DIR / "resume_samples.txt": "see data/raw/README.md",
        RAW_DIR / "Resume.csv": "see data/raw/README.md",
    }
    missing = [(p, hint) for p, hint in required.items() if not p.exists()]
    if missing:
        print("\nERROR: missing input files:")
        for p, hint in missing:
            print(f"  {p}  ({hint})")
        return

    print("\nLoading final.csv ...")
    final = pd.read_csv(KG_DIR / "final.csv", encoding="latin1")
    print(f"  {len(final)} total rows")

    # Only hand-labelled rows serve as ground truth, 30 resumes by 15 jobs.
    final = final[final["Hand_firm_rate_comb"].notna()].reset_index(drop=True)
    print(f"  {len(final)} hand-labeled rows retained")

    target_resume_hashes = set(final["Resume_index"].unique())
    target_job_hashes = set(final["Job_index"].unique())
    print(f"  {len(target_resume_hashes)} unique resume hashes, "
          f"{len(target_job_hashes)} unique job hashes")

    print("\nLoading raw data (resume_samples.txt is ~200 MB, takes a moment) ...")
    resume_df, jobs_df = load_raw_data(RAW_DIR)
    print(f"  {len(resume_df):,} resumes after length filter")
    print(f"  {len(jobs_df):,} job rows")

    print("\nHashing every raw resume and job ...")
    resume_df["hash"] = resume_df["Resume"].apply(hash_id)
    jobs_df["hash"] = jobs_df["Content"].apply(hash_id)

    # Lookups from hash back to text and metadata.
    resume_text_lookup = dict(zip(resume_df["hash"], resume_df["Resume"]))
    resume_cat_lookup = dict(zip(resume_df["hash"], resume_df["category"]))
    resume_src_lookup = dict(zip(resume_df["hash"], resume_df["source"]))
    job_text_lookup = dict(zip(jobs_df["hash"], jobs_df["Content"]))
    job_title_lookup = dict(zip(jobs_df["hash"], jobs_df["title"]))

    # Intersection gives the matches, difference the misses.
    matched_r = target_resume_hashes & set(resume_text_lookup)
    matched_j = target_job_hashes & set(job_text_lookup)
    print(f"\nMATCH: {len(matched_r)}/{len(target_resume_hashes)} resumes, "
          f"{len(matched_j)}/{len(target_job_hashes)} jobs")
    missing_r = target_resume_hashes - matched_r
    missing_j = target_job_hashes - matched_j
    if missing_r or missing_j:
        print(f"  WARNING: {len(missing_r)} resume and {len(missing_j)} job hashes "
              f"did not match. Usually this means the Kaggle dataset was updated "
              f"since Kim et al. ran their pipeline.")
        return

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("\nBuilding final_with_text.csv ...")
    final["Resume_text"] = final["Resume_index"].map(resume_text_lookup)
    final["Job_text"] = final["Job_index"].map(job_text_lookup)
    final["job_title"] = final["Job_index"].map(job_title_lookup)
    final["resume_category"] = final["Resume_index"].map(resume_cat_lookup)
    final["resume_source"] = final["Resume_index"].map(resume_src_lookup)
    final = final[KEEP_COLS]
    out_csv = OUTPUT_DIR / "final_with_text.csv"
    final.to_csv(out_csv, index=False)
    print(f"  wrote {out_csv}  ({out_csv.stat().st_size / 1e6:.1f} MB)")

    print("\nDone.")


if __name__ == "__main__":
    main()