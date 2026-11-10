# OpenRefine cleanup (10 Nov 2026)

Input: `licensed/analysis/scopus_included.csv` (321 included Scopus records, from
`export_for_tools.py`). Output: `licensed/analysis/scopus_included_cleaned.csv`
(same records and columns; both files are licensed and git-ignored).
OpenRefine 3.10, project "scopus included csv", 24 operations.

## Steps

1. EID moved to the first column (record key for multi-valued cells).
2. **Author Keywords**: split on `; `; fingerprint clusters merged (case, punctuation,
   hyphen variants); then plurals, acronyms with their full form (CNN, BMI, DXA, BIA,
   MRI, GAN, RED-S, MUAC, IGF-I) and typos merged; all values lower-cased except
   acronyms; nearest-neighbour (Levenshtein, radius 2) clusters reviewed by hand.
3. **Affiliations**: split on `; `; each reduced to institution + country (the first
   segment naming a university, college or hospital, else an institute, center,
   laboratory or company; departments and cities dropped); fingerprint and
   nearest-neighbour clusters and "The"/word-order variants merged.
4. **Index Keywords**: split on `; `; fingerprint clusters merged (MeSH and Emtree
   case variants), lower-cased.
5. **Source title**: whitespace trimmed; the two names of Lecture Notes in Computer
   Science and of the CVPR proceedings merged.
6. The three multi-valued columns joined again with `; ` and duplicates removed within
   each record.

## Decisions

Applied automatically: only unambiguous merges (see step 2).
Approved by the author: hypertrophy → muscle hypertrophy; mobile app → smartphone
application; visual estimation of BMI / visual analysis of body mass index → visual
BMI estimation; Louisiana State University System → Louisiana State University.
Kept separate on purpose: bodybuilding / bodybuilders; anthropometry / anthropometric;
energy availability / low energy availability / RED-S; learning to rank / ranking
learning; body image (psychology) / body images (photographs); Washington University /
University of Washington.

## Files

- `cleaning_map.tsv`: every original value that changed, its cleaned value and the
  number of papers (derived with `cleaning_map.py` from the before/after exports).
- `bibliometric/metrics.py` uses the cleaned keywords, affiliations and sources when
  the cleaned export is present.
