# Raw data

The three datasets below are *not* tracked in this repository (see `.gitignore`). Download each from its source and place it in this folder with the exact filename shown.

| Filename | Approx. size | Source |
|---|---|---|
| `upwork-jobs.csv` | 70 MB | https://www.kaggle.com/datasets/asaniczka/upwork-job-postings-dataset-2024-50k-records |
| `Resume.csv` | 55 MB | https://www.kaggle.com/datasets/snehaanbhawal/resume-dataset |
| `resume_samples.txt` | 210 MB | https://github.com/florex/resume_corpus |

## Notes

- **Encoding for `resume_samples.txt`:** the file is windows-1252. If `match_hashes.py` raises a `UnicodeDecodeError`, you most likely have a UTF-8 copy, so re-download from GitHub by right-clicking the *Raw* link and choosing *Save link as*, rather than copy-pasting from the rendered page in the browser.
- **Kaggle dataset versions can drift.** Kaggle keeps version history, so if `match_hashes.py` reports fewer than 30/30 resume hashes or 15/15 job hashes matched, fetch the historical version from the dataset's *Version* tab. The Asaniczka dataset is currently consistent with the 53,058 rows reported in Kim et al. (2025), and the Bhawal dataset is the standard one with `Resume_str` and `Category` columns.
- **Once the three files are here**, run `python scripts/match_hashes.py` from the repository root to regenerate `data/processed/final_with_text.csv`. Expected output:
  ```
  MATCH: 30/30 resumes, 15/15 jobs
  ```
- **Keep these files out of Git.** They are large, they carry their own licences, and the two resume corpora contain personal data. `.gitignore` already excludes all three, along with the recovered text they produce.