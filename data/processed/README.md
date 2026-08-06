# Processed data

## Tracked in this repository

| File | Contents |
|---|---|
| `neutralised/resumes_neutral_hand.txt` | The 30 resumes after the manual demographic cleaning described in Section 3 of the thesis. Every personal, geographic, institutional, and temporal identifier has been removed. These are the neutral baseline of the study and the base text every injected variant is built on. |
| `neutralised/jobs_neutral_hand.txt` | The 15 job descriptions after the lighter version of the same treatment, with country tags and incidental country references removed. |
| `jobs_unique.txt` | The 15 job descriptions as recovered, before the manual cleaning. Kept for comparison, and they contain no personal data. |
| `kim_hand_labels.csv` | Kim et al.'s hand labels, keyed by resume and job hash. Hashes only, no text. |

Entries in the text files are keyed by the full `Resume_index` or `Job_index` hash, so they join to `kim_hand_labels.csv` and to Kim et al.'s `final.csv` directly.

## Generated locally, never committed

Running the scripts produces three further files that `.gitignore` excludes.

| File | Written by |
|---|---|
| `final_with_text.csv` | `scripts/match_hashes.py` |
| `final_with_text_cleaned.csv` | `scripts/clean_text_columns.py` |
| `resumes_unique.txt` | `scripts/extract_unique_texts.py` |

All three carry the recovered resume text in full, including names, e-mail addresses, telephone numbers, and profile links belonging to real job seekers. Kim et al. published hashes rather than text for this reason, and this repository follows them. Regenerate the files from the raw datasets when you need them, and do not commit them.
