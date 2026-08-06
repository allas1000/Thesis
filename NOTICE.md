# Third-party content

This repository includes data and code derived from the sources listed below. Each retains its original licence, so consult the source for terms before any redistribution. The MIT licence in `LICENSE` covers only the code and figures written for this thesis.

## Kim et al. (2025), *Correlated Errors in Large Language Models*

- **Repository:** https://github.com/nikhgarg/llm_correlated_errors_public
- **Files reproduced here, in `data/kim_garg/`:**
  - `final.csv`, the 1,800-row scored dataset of 60 resumes and 30 jobs, of which the 450 hand-labelled rows are the primary ground truth for this thesis.
  - `utilities.py`, which contains the `hash_id` SHA-256 helper defining the format of `Resume_index` and `Job_index`.
  - `setup_data.py`, which defines `load_raw_data` and so specifies how the raw datasets are length-filtered and concatenated before hashing.
  - `5_Data.ipynb`, the notebook that built `final.csv`.
- **Use here:** the hashing logic in `scripts/match_hashes.py` mirrors `utilities.hash_id` and the preprocessing in `setup_data.load_raw_data` exactly, so that hashes recomputed from the raw data match `final.csv` bit for bit. The upstream files themselves are unmodified.

## Asaniczka (2024), *Upwork Job Postings Dataset, 50K records*

- **Source:** https://www.kaggle.com/datasets/asaniczka/upwork-job-postings-dataset-2024-50k-records
- **Used as:** `data/raw/upwork-jobs.csv`, not redistributed here.
- **Role:** the pool of 53,058 Upwork postings from which Kim et al. sampled 30 jobs.

## Bhawal (2022), *Resume Dataset*

- **Source:** https://www.kaggle.com/datasets/snehaanbhawal/resume-dataset
- **Used as:** `data/raw/Resume.csv`, not redistributed here.
- **Role:** one of the two resume pools Kim et al. sampled from, the LiveCareer-derived corpus of 2,484 resumes before the length filter.

## Jiechieu and Tsopze (2021), resume corpus

- **Source:** https://github.com/florex/resume_corpus
- **Used as:** `data/raw/resume_samples.txt`, not redistributed here.
- **Role:** the second resume pool, roughly 29,780 resumes before the length filter.

## Derived text

Two categories of derived text need distinguishing.

The recovered resume text is **not** published in this repository. It reproduces documents from the two resume corpora in full, including names, contact details, and profile links belonging to identifiable individuals. Kim et al. published hashes instead of text for the same reason. Anyone who obtains the raw datasets from their sources can regenerate the recovered text locally with `scripts/match_hashes.py`.

The neutralised resumes and job descriptions in `data/processed/neutralised/` **are** published. They are the study's own inputs rather than a copy of the source corpora, having been rewritten by hand to remove every personal, geographic, institutional, and temporal identifier. Publishing them lets the cleaning decisions be inspected, which the thesis relies on, and they carry no identifiers. They remain derived works of the corpora above, so their reuse is still governed by the source terms.
