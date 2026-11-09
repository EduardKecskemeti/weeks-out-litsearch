# Search log — "How Many Weeks Out Do You Look?"

Author: Eduard Kecskemeti. Started 17 Oct 2026; OpenAlex datasets built 19 Oct 2026;
Scopus and Web of Science added 7 Nov 2026 (section 5b).

## 1. Goal and questions

**Goal:** collect the published work the paper builds on or competes with.

**Main question:** how has progress toward contest leanness, or body composition in
general, been estimated from ordinary photographs?

Sub-questions:
- Q1. Which models estimate body fat, body composition or shape from 2D images, and on which populations?
- Q2. How is body composition tracked in physique athletes during contest preparation, and how accurate are the methods at very low body fat?
- Q3. Which methods learn an ordering or a progression stage from images without absolute labels?

**Inclusion criteria (from the assignment):** journal articles (including reviews),
conference papers, book chapters; English only; published 2016–2025 (the current
year, 2026, is excluded).

## 2. Term refinement with Google Scholar Labs (17 Oct 2026)

Each sub-question was asked in natural language; the ten results and their
summaries were used to collect vocabulary, not as the dataset.

| Q | Terms confirmed or added by Scholar Labs | Seed papers noticed |
|---|---|---|
| Q1 | "body fat percentage", "visual body composition", "digital anthropometry", "optical imaging", "2D photo", "single image", "silhouette", "smartphone"; DXA as the usual reference | Majmudar et al. 2022 (npj Digit. Med.); Farina et al. 2022 (Sensors); Ferreira et al. 2025 (npj Digit. Med.); Nascimento et al. 2024 (ShapedNet, Pattern Recognit. Lett.); Minetto et al. 2023 (Sci. Rep., youth athletes) |
| Q2 | "contest preparation", "physique athlete", "physique competitor", "natural / drug-free bodybuilder", "pre-competition", "four-compartment", "lean mass" | Bauer et al. 2023 (systematic review, J. Strength Cond. Res.); Tinsley et al. 2018/2019 (J. Strength Cond. Res.); Schoenfeld et al. 2020; Pardue et al. 2017; Kasper et al. 2021 (Nutrients) |
| Q3 | "temporal order", "image ordering", "longitudinal images", "pairwise ranking", "Siamese network", "ordinal regression", "disease progression", "self-supervised" | Kim & Sabuncu 2023 (PaIRNet); Li et al. 2020 (Siamese, npj Digit. Med.); Yang, Xie & Zisserman 2024 (ECCV, video ordering); Liu et al. 2018 (constrained ordinal CNN) |

Terms dropped: "body image" (psychology meaning dominates the results).

## 3. Database used and why

| Source | Status on 17–19 Oct 2026 | Use |
|---|---|---|
| Web of Science | Login failed | Not used yet |
| Scopus | Only Scopus Preview; institutional (e-nformation) account pending approval | Not used yet |
| Google Scholar / Scholar Labs | Works | Term refinement and seed papers (section 2). Scholar has no document-type or language filters and no bulk export, so it cannot produce the dataset itself. |
| **OpenAlex** (api.openalex.org) | Works, open | **Dataset source.** Same open index that Scholar-based tools such as Publish or Perish draw on; supports boolean title/abstract search, filters for year, language and type, and full export. |

**Plan:** when Scopus or Web of Science access is approved, the same four queries
will be re-run there (TITLE-ABS-KEY / TS fields, same filters), the results merged
with this set by DOI, and the relevant set re-screened.

## 4. Queries (OpenAlex `title_and_abstract.search`)

Filters on every query:
`publication_year:2016-2025, language:en, type:article|review|conference-paper|book-chapter`

| Block | Question | Query | Hits |
|---|---|---|---|
| b1v3 | Q1 | ("body fat" OR "body composition" OR adiposity OR "body shape" OR physique OR "body mass index" OR anthropometry OR anthropometric) AND (photograph OR photo OR "2D image" OR "single image" OR "RGB image" OR smartphone OR "computer vision" OR "image-based" OR silhouette OR "digital anthropometry") AND ("deep learning" OR "machine learning" OR "neural network" OR convolutional OR "artificial intelligence" OR "computer vision" OR automated OR "2D image" OR "two-dimensional") | 804 |
| b1 | Q1 (narrow, subset of b1v3) | same first two concepts AND ("deep learning" OR "machine learning" OR "neural network" OR convolutional) | 436 |
| b2 | Q2 | (bodybuilder OR bodybuilding OR "physique athlete" OR "physique competitor" OR "physique competition" OR "contest preparation" OR "competition preparation") AND ("body composition" OR "body fat" OR "fat loss" OR "weight loss" OR "energy restriction" OR "lean mass" OR "fat mass") | 294 |
| b3v4 | Q3 | ("ordinal regression" OR "learning to rank" OR "pairwise ranking" OR "siamese network" OR "siamese neural network" OR "temporal order" OR "image ordering") AND (longitudinal OR progression OR "age estimation" OR "temporal change" OR "disease severity") AND (image OR images OR photograph OR imaging) | 138 |
| b4 | link Q1–Q2 | (bodybuilding OR bodybuilder OR "physique athlete" OR "physique competitor") AND ("computer vision" OR "deep learning" OR "machine learning" OR "artificial intelligence" OR "pose estimation") | 18 |
| | | **Union (unique records)** | **1,251** |

### Refinement history

| Step | Change | Why |
|---|---|---|
| 1 | First run used types article / review / book-chapter only | Conference papers are a separate OpenAlex type and were missing; "conference-paper" added (ML work in Q1 and Q3 is mostly published at conferences). |
| 2 | b1 → b1v3 (third concept widened with "artificial intelligence", "computer vision", "automated", "2D image", "two-dimensional") | b1 missed seed papers that describe the method without ML words, e.g. Majmudar 2022 and Ferreira 2025. Dropping the third concept entirely gave 3,991 hits, too many. |
| 3 | b3 → b3v4 | The first b3 (292 hits) used a bare `siamese` (matched Thai/Siam studies) and "progression" without an image term (oncology). Requiring a neural-network word (b3v2) left only 46; dropping the image term (b3v3) gave 703. b3v4 uses the specific network phrases and requires an image term. |
| 4 | b4 added | Captures AI-in-bodybuilding work that falls between Q1 and Q2. |

Seed-paper recall after refinement: found Majmudar 2022, Ferreira 2025, Jiang & Guo
2019, Niu 2016, Yang et al. 2024 (Made to Order). Not found by any query (wording
outside the query terms, or no abstract in the index): Kasper 2021, Minetto 2023,
Liu 2018, Toulany 2023, and several 2025 items without abstracts; four of these were
added to the relevant set by snowballing (section 7). PaIRNet (arXiv only) and
DINOv2 (indexed as a preprint) do not meet the type criteria.

## 5. Cleaning (1,251 → 1,167 records)

| Rule | Removed |
|---|---|
| R1 commercial spam (supplement adverts posted to Zenodo, ad pages with no source) | 11 |
| R2 retracted articles and retraction notices | 5 |
| R3 front matter, not research (abstract-book supplements and their section headers, indexes, tables of contents, news, obituaries) | 21 |
| R4 no DOI and no source (cannot be identified) | 2 |
| R5 repository copies, theses and preprints without a publisher DOI | 31 |
| R6 non-English title despite the "en" language tag (Portuguese, Spanish, Indonesian, Ukrainian) | 5 |
| R7 duplicate titles (kept the version with DOI and venue) | 9 |
| **Total removed** | **84** |

Every removed record, with its rule, is in `removed_records.tsv`.

Invisible formatting characters and private-use symbols carried over from OpenAlex
author names were removed, and one missing venue (IJCNN 2020) was filled in from the
DOI.

**Dataset 1, OpenAlex version (19 Oct, superseded by section 5b):** 1,171 records — the 1,167 cleaned search records plus the 4
snowballed seed papers (block `snowball`), so that dataset 2 is a subset of dataset 1.
879 articles, 17 reviews, 242 conference papers, 33 book chapters; 2016–2025. It is
deliberately not screened: block b1v3 is broad and contains off-topic medical-imaging
and apparel work. Three records have no author list in OpenAlex; they are real papers
and were kept.

**Year convention:** the year is OpenAlex's publication year, which is the first
(online) publication date. A few journal papers therefore carry the year before their
print issue (e.g. Tinsley et al., online 2018, issue 33(7) 2019). The 2016–2025 filter
was applied to this year.

## 5b. Scopus and Web of Science (7 Nov 2026)

Access came through the university's e-nformation account (library proxy; Scopus
export needs a personal Elsevier sign-in on top). The four final blocks were run
with the same concept groups and the same filters (years 2016–2025, English;
article, review, conference paper / proceedings paper, book chapter).

**First run, title + abstract + keywords (scrapped).** Scopus `TITLE-ABS-KEY` gave
974 / 219 / 216 / 13 hits (b1v3 / b2 / b3v4 / b4; 1,422 unique) and WoS `TS=` gave
453 / 199 / 105 / 9 (766 unique). Merged with OpenAlex this came to about 1,970
works, over the 1,500 limit, so the field was narrowed to title and abstract.

**Final run, title + abstract only.** Scopus `TITLE-ABS(...)`; WoS each concept as
`(TI=(...) OR AB=(...))`. This is also the field OpenAlex searches, so the three
databases now search the same thing.

| Block | OpenAlex | Scopus | WoS |
|---|---|---|---|
| b1v3 | 804 | 534 | 345 |
| b2 | 294 | 176 | 137 |
| b3v4 | 138 | 90 | 75 |
| b4 | 18 | 10 | 9 |
| unique | 1,251 | 810 | 566 |

Exact strings: `queries.json` (`scopus_wos`). Each string was checked character by
character against the query the database actually ran (checksum of the query
stored by Scopus and of the WoS search history).

**Merging.** Records were grouped when they share a DOI or the same normalised title
(letters and digits only). OpenAlex metadata is kept when a work is in OpenAlex
(it carries abstracts); otherwise Scopus, otherwise WoS. Of 2,631 records
(1,251 + 810 + 566 + 4 snowballed) there are 1,338 distinct works; 488 are in all
three databases.

**Cleaning of Scopus / WoS records** (on top of R1–R7):

| Rule | Removed |
|---|---|
| D1 year outside 2016–2025 (WoS early-access record dated 2026) | 1 |
| D2 retracted (flagged "Retracted Publication" in WoS; two had been kept from OpenAlex) | 3 |
| D3 same work as an OpenAlex record removed by R1, R2, R3 or R6 | 1 |
| D4 not a research contribution (encyclopedia entry) | 1 |

Works removed from OpenAlex under R4/R5 (repository copies, preprints, no venue)
were kept when Scopus or WoS index the published version, with that metadata.

**Record flow:** 2,631 identified → 1,338 after de-duplication → −63 OpenAlex-only
works removed by R1–R7 → −6 removed by D1–D4 → **dataset 1: 1,269 records**
(931 articles, 20 reviews, 283 conference papers, 35 book chapters). 101 works come
only from Scopus and/or WoS. The flow is in `results/flow.tsv`.

**Licensing.** Scopus and WoS exports are licensed. The repository holds only
identifiers (EID, WoS UT, DOI) and citation fields (`data/raw/scopus_ta.tsv`,
`data/raw/wos_ta.tsv`); abstracts, keywords and cited references stay in the
git-ignored `licensed/` folder. Records found only through Scopus/WoS therefore have
no abstract in the public files.

## 6. Screening for the relevant set

Titles (and abstracts where present) of the broad set were screened. A record was
kept if it does at least one of:
- estimates body fat, body composition, weight or shape from 2D photos, with a
  validation against a reference method or a clear method contribution (Q1);
- measures body-composition change across contest preparation, or gives reference
  values for stage-ready physique athletes (Q2);
- learns an order, rank or progression stage from images, especially with pairwise
  or relative labels (Q3);
- applies AI directly to bodybuilding.

Excluded at screening: medical-imaging body composition from CT/MRI (different input
and setting), face-only BMI papers beyond one representative, nutrition, supplement,
hormone and psychology studies in bodybuilders without body-composition tracking,
apparel and avatar reconstruction without a body-composition goal, and conference
abstracts.

## 7. Dataset 2 (relevant): 50 records

| Theme | n |
|---|---|
| A. Body composition from ordinary photos (validation) | 15 |
| B. Body shape, weight and BMI from images | 8 |
| C. Body composition during contest preparation | 11 |
| D. Learning order, rank or progression from images | 13 |
| E. AI applied to bodybuilding | 3 |

42 were found by OpenAlex (34 of them also by Scopus and WoS), 4 only by Scopus
and/or WoS, and 4 by snowballing the Scholar Labs seeds (Liu et al. 2018 CVPR;
Minetto et al. 2023 Sci. Rep.; Kasper et al. 2021 Nutrients; Toulany et al. 2023
Nat. Methods). The reason for each inclusion is in the `why_relevant` column.

Re-screening after Scopus/WoS (7 Nov) added four works the OpenAlex queries missed:
body-fat estimation from frontal body photos (CASCON 2025),
pairwise ranking from images for dementia diagnosis (Multimedia Tools and
Applications 2016), a ranking-aware CLIP adapter for image ordering (ICLR 2025) and a
deep-learning scoring of beauty-pageant contestants from ramp-walk videos (IConSCEPT 2025). To stay at 50, four weaker
entries were dropped: a generic CNN body-measure paper, a second digital-imaging
validation study, a female prep study on diet and menstrual-cycle changes and a
general overview of natural contest preparation.

## 8. Refinement for the bibliometric analysis (Scopus, 9 Nov 2026)

Before cleanup, the Scopus blocks were refined with tests of the form
`(extended AND NOT base) AND filters`, reading the titles of every delta
(all tests: `bibliometric/vocabulary_tests.tsv`).

1. **b3v4 → b3v5**: nine specific ranking phrases (+25 records, 20 relevant).
2. **b1v3 → b1v4**: a NOT-block for the main noise sources found at screening
   (retina, fundus, livestock, fish, animals, CT, gait, action recognition):
   −74 records, none relevant; precision 0.28 → 0.33.
3. **New block b5**: b1 requires an ML term, so validation studies of smartphone and
   2D-photo body-composition apps were missed, including one dataset-2 paper. Widening
   b1's method column instead would add about 140 records at 0.14–0.20 precision; the
   separate sub-query adds 58 records, 18 included. Dedicated 3D optical scanner studies
   (19) were excluded as out of scope (E11, 2D photos only).
4. **Rejected**: body-composition subterms in b2 (+59, mostly steroids and case reports).

Recall against dataset 2: 44 of 50 retrieved and included (`results/gold_recall.tsv`);
one miss is not in Scopus and one is dated 2026, so recall is 44/48 = 0.92. The other
four lack a term from one concept column; widening those columns costs far more noise
than it recovers.

## 9. Files

| File | Content |
|---|---|
| `dataset1_broad.csv / .bib / .ris` | 1,269 records: search blocks, source databases, Scopus EID / WoS UT, abstracts where OpenAlex has them |
| `dataset2_relevant.csv / .bib / .ris` | 50 relevant records with theme, reason and how found |
| `removed_records.tsv` | removed records and the rule that removed each (R1–R7 OpenAlex, D1–D4 Scopus/WoS) |
| `flow.tsv` | PRISMA-style record flow |
| `search_log.md` | this log |

The .ris and .bib files import directly into Zotero, Mendeley or EndNote.
