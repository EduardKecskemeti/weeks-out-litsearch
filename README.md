# How many weeks out do you look? Literature search

[![reproduce](../../actions/workflows/reproduce.yml/badge.svg)](../../actions/workflows/reproduce.yml)

The bibliographic search behind a paper on estimating **"apparent weeks out"**
(how close to contest condition a physique competitor looks) from ordinary
photos, using **pairwise ranking**. Built for *Methodology of Research*,
Assignment 2 (Eduard Kecskemeti, October–November 2026).

The same four queries were run in **OpenAlex, Scopus and Web of Science**. This
repository holds the queries, the raw search results (for Scopus and WoS:
identifiers and citation fields only, see Licence), the scripts that turn them
into the two datasets, and checksums. **Anyone can rebuild every result file from
the raw data and get byte-identical output.**

## Results

| Step | Records | |
|---|---|---|
| Identified | 2,631 | OpenAlex 1,251 · Scopus 810 · Web of Science 566 · snowballing 4 |
| After de-duplication (DOI, then title) | 1,338 | 488 works are in all three databases |
| Removed: OpenAlex-only works, rules R1–R7 | −63 | `results/removed_records.tsv` |
| Removed: Scopus/WoS records, rules D1–D4 | −6 | `results/removed_records.tsv` |
| **Dataset 1: broad** (limit 1,500) | **1,269** | `results/dataset1_broad.csv` / `.bib` / `.ris` |
| **Dataset 2: relevant** (limit about 50) | **50** | `results/dataset2_relevant.csv` / `.bib` / `.ris` |

The flow is also in `results/flow.tsv`. Dataset 1: 931 articles, 20 reviews, 283
conference papers, 35 book chapters; English; 2016–2025. Each record lists the
databases that found it and its Scopus EID / WoS UT. Dataset 2 is a screened subset
with a theme and a reason for each paper:

| Theme | Papers |
|---|---|
| A. Body composition from ordinary photos | 15 |
| B. Body shape, weight and BMI from images | 8 |
| C. Body composition during contest preparation | 11 |
| D. Learning order, rank or progression from images | 13 |
| E. AI applied to bodybuilding | 3 |

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
3. **Counts:** the record flow in `results/flow.tsv` adds up to dataset 1.

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

Scopus and Web of Science need an institutional subscription. Their exact query
strings are in `search/queries.json`; the EIDs and UTs they returned are in
`data/raw/scopus_ta.tsv` and `data/raw/wos_ta.tsv` for comparison.

## Search strategy

- **Question:** how has progress toward contest leanness, or body composition
  in general, been estimated from ordinary photographs?
  - Q1 body composition and shape from 2D images
  - Q2 body composition during contest preparation
  - Q3 learning an order or progression from images without absolute labels
- **Term refinement:** Google Scholar Labs, one natural-language prompt per
  sub-question, used only for vocabulary and seed papers.
- **Databases**, all searching title and abstract:
  - OpenAlex, `title_and_abstract.search` (17–19 Oct 2026);
  - Scopus, `TITLE-ABS(...)` (7 Nov 2026, through the university library);
  - Web of Science Core Collection, `(TI=(...) OR AB=(...))` per concept (7 Nov 2026).

  Google Scholar has no type or language filters and no export.
- **Filters:** 2016–2025; English; article, review, conference paper, book chapter
  (each database's own syntax, see `search/queries.json`).

| Block | Question | OpenAlex | Scopus | WoS | |
|---|---|---|---|---|---|
| b1v3 | Q1 | 804 | 534 | 345 | final |
| b2 | Q2 | 294 | 176 | 137 | final |
| b3v4 | Q3 | 138 | 90 | 75 | final |
| b4 | AI in bodybuilding | 18 | 10 | 9 | final |
| Scopus/WoS with keywords | all | | 1,422 | 766 | scrapped: about 1,970 works after merging, over 1,500 |
| b1 | Q1, narrower | 436 | | | subset of b1v3; used only as a label |
| run 1 | all, no conference papers | 881 | | | scrapped: conference papers missing |
| b1 without 3rd concept | Q1 | 3,991 | | | scrapped: too broad |
| b3 original | Q3 | 292 | | | scrapped: "siamese" matched Thai/Siam studies |
| b3v2 | Q3 | 46 | | | scrapped: too narrow |
| b3v3 | Q3 | 703 | | | scrapped: no image term, off-topic |

Full query strings: [`search/queries.json`](search/queries.json) (machine
readable) and [`search/search_queries.pdf`](search/search_queries.pdf).
Reasoning for each change: [`search/search_log.md`](search/search_log.md).

### Cleaning rules

OpenAlex records (`scripts/clean.py`):

| Rule | Removed |
|---|---|
| R1 commercial spam (supplement adverts on Zenodo, ad pages) | 11 |
| R2 retracted articles and retraction notices | 5 |
| R3 front matter (abstract books, indexes, tables of contents, news) | 21 |
| R4 no DOI and no source | 2 |
| R5 repository copies and preprints without a publisher DOI | 31 |
| R6 non-English titles despite the "en" tag | 5 |
| R7 duplicate titles (kept the version with DOI and venue) | 9 |

Scopus and WoS records that are not in the cleaned OpenAlex set (`scripts/merge_db.py`):

| Rule | Removed |
|---|---|
| D1 year outside 2016–2025 (WoS early access dated 2026) | 1 |
| D2 retracted (WoS "Retracted Publication"; two had been kept from OpenAlex) | 3 |
| D3 same work as an OpenAlex record removed by R1, R2, R3 or R6 | 1 |
| D4 not a research contribution (encyclopedia entry) | 1 |

Works dropped from OpenAlex under R4/R5 come back when Scopus or WoS index the
published version. Every removed record and its rule: `results/removed_records.tsv`.

## Bibliometric analysis (Scopus, task 2)

The quantitative analysis uses **Scopus as primary database** (title + abstract
queries, 2016–2025; exported 7 Nov 2026; refined 9 Nov 2026: ranking block extended,
NOT-block on b1, new validation sub-query b5).

| Step | Records |
|---|---|
| Retrieved: b1v4 460, b2 176, b3v5 115, b4 10, b5 58 (unique EIDs) | 819 |
| Excluded at title/abstract screening | −498 |
| **Screened set** | **321** |

Scope is ordinary 2D photographs: depth-camera, 3D-scanner and point-cloud studies are
excluded (code E11, 39 records; decision of 10 Nov 2026).

Recall against the 50 papers of dataset 2: 44 retrieved and included; of the 6 misses one is
not in Scopus and one is dated 2026, so recall on the 48 that could be found is 0.92
(`results/gold_recall.tsv`, `bibliometric/gold_recall.py`).

- `bibliometric/keyword_matrix.md`: keyword matrices with MeSH and ACM CCS mapping
- `bibliometric/vocabulary_tests.tsv`: candidate terms from the vocabularies tested
  in Scopus; adopted: specific ranking phrases (b3v4 → b3v5, +25 records), NOT-block
  on b1 (b1v3 → b1v4, −74 records, 0 relevant lost), validation sub-query b5 (+58)
- `bibliometric/screening_decisions.py`: inclusion criteria, exclusion codes, decisions
- `results/screening_scopus.tsv`: decision per record (EID, title, reason code)
- `results/bibliometrics/`: performance metrics (TP, NCA, TC, h, g, i10 …), year,
  country, source, author, keyword tables, citation links between blocks, figures
- `bibliometric/vosviewer/thesaurus_keywords.txt`: first keyword thesaurus for VOSviewer

`bibliometric/screen.py`, `metrics.py` and `export_for_tools.py` need the licensed
Scopus exports in `licensed/`, which are not distributed. They are not part of the
CI rebuild; their outputs are committed as they were produced.

## Repository layout

```
data/raw/            raw OpenAlex snapshot, Scopus/WoS identifier tables (never edited) + SNAPSHOT.md
scripts/
  merge.py           raw snapshot -> one record per search hit
  clean.py           cleaning rules R1–R7
  merge_db.py        add Scopus + WoS, de-duplicate, rules D1–D4, record flow
  extract_db.py      licensed Scopus/WoS exports -> public identifier tables (author only)
  relevant.py        dataset 2: chosen papers, themes, reasons; snowballed seeds
  build.py           CSV / BibTeX / RIS export
  reproduce.sh       runs merge, clean, merge_db and build
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
- **Abstracts** exist only for OpenAlex records from run 1; Scopus/WoS abstracts
  are licensed and not published here. 32 of the 50 relevant papers have none in
  the public files.
- **Screening** for dataset 2 was done by hand. The reasons are in
  `scripts/relevant.py` and the `why_relevant` column.
- **Scopus/WoS exports are not in the repository.** `scripts/extract_db.py`
  documents how the public tables were made from them; anyone with access can
  re-run the queries and compare EIDs / UTs.
- **De-duplication** uses DOI and exact normalised title. Works without a DOI
  whose titles differ between databases may appear twice.

## Licence

Code: MIT (see `LICENSE`). Bibliographic data: OpenAlex records are CC0. For
Scopus (Elsevier) and Web of Science (Clarivate) only identifiers and basic
citation fields are published; abstracts, keywords and cited references from those
exports are licensed and are kept out of the repository (`licensed/` is
git-ignored).
