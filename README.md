# Many Models, Same Bias?

Data, code, and figures for my master's thesis at LMU Munich, *Many Models, Same Bias? An Analysis of Fairness and Systematic Deviations in Large Language Models and the Implications for Insurance* (supervisor: Leonard Külpp, advisor: Yuanyuan Yi).

The study builds on Kim et al. (2025), *Correlated Errors in Large Language Models*. It recovers their hand-labelled subset of 30 resumes and 15 job descriptions from the published hashes, strips the resumes of demographic markers by hand, injects controlled race, gender, and age signals, and scores every variant with twelve open-weight models. The question is whether demographic bias is correlated across models, and what follows for an insurer writing the resulting exposure.

## Repository structure

```
thesis-repo/
├── README.md                   (this file)
├── NOTICE.md                   (third-party attributions)
├── LICENSE                     (MIT for the code, see NOTICE.md for the data)
├── requirements.txt
├── data/
│   ├── raw/                    (external datasets, not tracked, see data/raw/README.md)
│   ├── kim_garg/               (files from Kim et al.'s public repository)
│   └── processed/              (see data/processed/README.md for what is published)
├── figures/                    (the figures reported in the thesis)
├── notebooks/
│   ├── reinforced_study_v1_all_models.ipynb   (the main study)
│   └── pilot_injection.ipynb                  (the single-name pilot)
└── scripts/
    ├── match_hashes.py                 (recovers text from Kim et al.'s hashes)
    ├── clean_text_columns.py           (removes scraping noise from that text)
    ├── extract_unique_texts.py         (writes the unique resumes and jobs to plain text)
    └── diversification_floor_figure.py (draws the Section 5 diversification figure)
```

## What is published here, and what is not

The neutralised resumes and job descriptions in `data/processed/neutralised/` are the actual inputs to the study, so they are published in full and the cleaning decisions can be inspected line by line.

The recovered resume text is not published. Kim et al. released SHA-256 hashes rather than text, and the recovered documents carry names, e-mail addresses, telephone numbers, and profile links belonging to real job seekers. Republishing them would expose personal data that the upstream authors deliberately withheld. `match_hashes.py` reproduces the recovery locally for anyone who downloads the raw datasets, so the pipeline stays verifiable without the identifiable text leaving the machine it is built on.

Also absent are the raw datasets, which are large and carry their own licences, and the per-model parquet score caches, which sit on Google Drive next to the Colab runtime.

## From raw data to results

The pipeline runs in two stages. The scripts rebuild the dataset, and the notebooks run the study on it.

1. `match_hashes.py` recovers the original resume and job text from Kim et al.'s hashes by re-running their preprocessing on the raw datasets. It takes one to two minutes on a typical laptop, most of which is reading the 200 MB `resume_samples.txt`. Expected output is `MATCH: 30/30 resumes, 15/15 jobs`. Writes `data/processed/final_with_text.csv`, the 450 hand-labelled rows with resume and job text attached.
2. `clean_text_columns.py` removes scraping noise from the `Resume_text` and `Job_text` columns, meaning HTML tags left by keyword highlighting, non-breaking and zero-width spaces, and a small number of garbled apostrophes. It writes `data/processed/final_with_text_cleaned.csv` and leaves the original untouched. Output is UTF-8 with BOM so that Excel renders non-ASCII characters correctly.
3. `extract_unique_texts.py` pulls the 30 unique resumes and 15 unique job descriptions out of the cleaned CSV into plain text, which is the format the manual demographic cleaning was carried out in. The hand-neutralised results of that cleaning are in `data/processed/neutralised/`.
4. `notebooks/reinforced_study_v1_all_models.ipynb` builds the three study arms, meaning neutral, reinforced injection, and observational, scores 87,300 resume-job pairs per model across the twelve models, and produces every figure in `figures/`. Scoring ran on a single NVIDIA L4 on Google Colab and caches results per model as parquet, so an interrupted run resumes where it stopped. The analysis sections read only those caches and run on a CPU runtime.
5. `notebooks/pilot_injection.ipynb` holds the single-name pilot that motivated the reinforced design. It scores ten of the twelve models on a fixed subsample against the 80-name set of Wilson and Caliskan (2024).

## Reproducing the study

1. Install Python 3.10 or newer and the dependencies with `pip install -r requirements.txt`.
2. Download the three raw datasets into `data/raw/`. See `data/raw/README.md` for sources, file names, and a note on encoding.
3. Run the three scripts in order from the repository root. This regenerates the files that `data/processed/README.md` lists as locally generated.
4. Open the notebooks in Colab or a local Jupyter server. Scoring needs a GPU and a Hugging Face token with access to the gated Llama and Gemma weights. The notebook reads that token from Colab secrets, an `HF_TOKEN` environment variable, or a file on Drive, in that order.

Two caveats are worth noting. Kaggle dataset versions drift, so if fewer than 30 resume or 15 job hashes match, fetch the historical version from the dataset's version tab. Model outputs are also sampled, so individual scores will not reproduce exactly, though the aggregate patterns reported in the thesis are stable across runs.

## Acknowledgments

This project builds on the data and code released by Kim et al. (2025) at https://github.com/nikhgarg/llm_correlated_errors_public. The hashing logic in `scripts/match_hashes.py` mirrors theirs so that recomputed hashes match `final.csv` exactly. Full attribution for all third-party files is in `NOTICE.md`.

## Licence

The code in `scripts/` and `notebooks/` and the figures in `figures/` are released under the MIT licence, see `LICENSE`. Third-party material is not covered by it. Files in `data/kim_garg/` retain their upstream licence, and data derived from the external datasets remains subject to the terms of its source. See `NOTICE.md`.
