# How many weeks out do you look? Literature search

[![reproduce](../../actions/workflows/reproduce.yml/badge.svg)](../../actions/workflows/reproduce.yml)

The bibliographic search behind a paper on estimating **"apparent weeks out"**
(how close to contest condition a physique competitor looks) from ordinary
photos, using **pairwise ranking**. Built for *Methodology of Research*,
Assignment 2 (Eduard Kecskemeti, October 2026).

This repository holds the queries, the raw search results, the scripts that
turn them into the two datasets, and checksums. **Anyone can rebuild every
result file from the raw data and get byte-identical output.**

## Results

| | Records | File |
|---|---|---|
| Retrieved by the four final queries | 1,251 | `data/raw/blockmap_v2.txt` |
| Removed by cleaning rules | −84 | `results/removed_records.tsv` |
| Added by snowballing (seed papers the queries missed) | +4 | `scripts/relevant.py` |
| **Dataset 1: broad** (limit 1,500) | **1,171** | `results/dataset1_broad_openalex.csv` / `.bib` / `.ris` |
| **Dataset 2: relevant** (limit about 50) | **50** | `results/dataset2_relevant.csv` / `.bib` / `.ris` |

Dataset 1: 879 articles, 17 reviews, 242 conference papers, 33 book chapters;
English; 2016–2025. Dataset 2 is a screened subset with a theme and a reason
for each paper:

| Theme | Papers |
|---|---|
| A. Body composition from ordinary photos | 15 |
| B. Body shape, weight and BMI from images | 9 |
| C. Body composition during contest preparation | 13 |
| D. Learning order, rank or progression from images | 11 |
| E. AI applied to bodybuilding | 2 |

## Verify it yourself

Requires Python 3.8 or newer and nothing else.

```bash
git clone <this repository>
cd weeks-out-litsearch
python3 scripts/verify.py --rebuild
```

This rebuilds `results/` from `data/raw/`, then checks:

1. **Checksums:** every raw and result file matches `CHECKSUMS.sha256`;
2. **Assignment criteria:** record limits, allowed types (article, review,
   conference paper, book chapter), years 2016–2025, no duplicate IDs or DOIs,
   and that dataset 2 is a subset of dataset 1;
3. **Counts:** retrieved − removed + snowballed = dataset 1.

It ends with `ALL CHECKS PASSED`. GitHub Actions runs the same check on every
push (badge above).

### Re-run the search live

```bash
python3 scripts/fetch_openalex.py
```

This sends the exact final queries to the OpenAlex API and compares the IDs it
gets back with the archived ones, block by block. OpenAlex keeps adding and
re-indexing records, so a later run returns most of the archived records plus
some new ones. It won't match exactly. Set `OPENALEX_API_KEY` and/or
`OPENALEX_MAILTO` if you hit rate limits.

## Search strategy

- **Question:** how has progress toward contest leanness, or body composition
  in general, been estimated from ordinary photographs?
  - Q1 body composition and shape from 2D images
  - Q2 body composition during contest preparation
  - Q3 learning an order or progression from images without absolute labels
- **Term refinement:** Google Scholar Labs, one natural-language prompt per
  sub-question, used only for vocabulary and seed papers.
- **Database:** OpenAlex, `title_and_abstract.search`. Web of Science login
  failed and Scopus access was pending. Google Scholar has no type or language
  filters and no export.
- **Filters:** `publication_year:2016-2025, language:en, type:article|review|conference-paper|book-chapter`

| Block | Question | Hits | |
|---|---|---|---|
| b1v3 | Q1 | 804 | final |
| b2 | Q2 | 294 | final |
| b3v4 | Q3 | 138 | final |
| b4 | AI in bodybuilding | 18 | final |
| b1 | Q1, narrower | 436 | subset of b1v3; used only as a label |
| run 1 | all, no conference papers | 881 | scrapped: conference papers missing |
| b1 without 3rd concept | Q1 | 3,991 | scrapped: too broad |
| b3 original | Q3 | 292 | scrapped: "siamese" matched Thai/Siam studies |
| b3v2 | Q3 | 46 | scrapped: too narrow |
| b3v3 | Q3 | 703 | scrapped: no image term, off-topic |

Full query strings: [`search/queries.json`](search/queries.json) (machine
readable) and [`search/search_queries.pdf`](search/search_queries.pdf).
Reasoning for each change: [`search/search_log.md`](search/search_log.md).

### Cleaning rules (`scripts/clean.py`)

| Rule | Removed |
|---|---|
| R1 commercial spam (supplement adverts on Zenodo, ad pages) | 11 |
| R2 retracted articles and retraction notices | 5 |
| R3 front matter (abstract books, indexes, tables of contents, news) | 21 |
| R4 no DOI and no source | 2 |
| R5 repository copies and preprints without a publisher DOI | 31 |
| R6 non-English titles despite the "en" tag | 5 |
| R7 duplicate titles (kept the version with DOI and venue) | 9 |

Every removed record and its rule: `results/removed_records.tsv`.

## Repository layout

```
data/raw/            raw OpenAlex snapshot (never edited) + SNAPSHOT.md provenance
scripts/
  merge.py           raw snapshot -> one record per search hit
  clean.py           cleaning rules R1–R7
  relevant.py        dataset 2: chosen papers, themes, reasons; snowballed seeds
  build.py           CSV / BibTeX / RIS export
  reproduce.sh       runs the three steps above
  verify.py          checksums + criteria + counts
  fetch_openalex.py  live re-run against OpenAlex and comparison
  queries_pdf.py     builds search/search_queries.pdf
results/             generated datasets (do not edit; rebuild instead)
search/              queries (JSON, PDF) and the search log
presentation/        slides and speaker notes used to present the assignment
CHECKSUMS.sha256     SHA-256 of raw and result files
```

## Limitations

- **Browser-based retrieval.** The API was queried from a web browser, so the
  raw data was saved from there. `data/raw/SNAPSHOT.md` describes the transfer
  and the per-part checksums used to confirm nothing changed in transit.
- **Snapshot in time.** Hit counts are from 17–19 October 2026. OpenAlex
  changes, so `fetch_openalex.py` measures overlap and does not expect
  identical results.
- **One scrapped query is described, not quoted.** The exact wording of b3v2
  was not saved. Its structure and hit count are recorded.
- **Years** are OpenAlex publication years (first online publication). A few
  journal papers carry the year before their print issue.
- **Abstracts** exist only for records from run 1. 30 of the 50 relevant
  papers have none.
- **Screening** for dataset 2 was done by hand. The reasons are in
  `scripts/relevant.py` and the `why_relevant` column.
- **Next:** re-run the same four queries in Scopus / Web of Science when access
  is approved, then merge by DOI.

## Licence

Code: MIT (see `LICENSE`). Bibliographic data: from OpenAlex, released under
CC0.
