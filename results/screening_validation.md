# Screening validation in ASReview LAB (10 Nov 2026)

Both reviewers labelled all 321 included records independently in ASReview LAB 2
(separate projects on `scopus_included_cleaned.csv`), with the question "is this
paper relevant to estimating contest readiness from physique photos?". Claude's
labels were made without seeing the other reviewer's. Per-record labels:
`screening_validation_asreview.tsv`.

| | relevant (EK) | not relevant (EK) |
|---|---|---|
| relevant (Claude) | 110 | 72 |
| not relevant (Claude) | 46 | 93 |

Agreement 0.63, Cohen's kappa 0.27 ("fair"). By block: b1v4 κ 0.11, b2 0.44,
b3v5 0.14, b4 0.57, b5 0.00 (EK 14 / Claude 18 relevant of 18).

The disagreements are systematic, so they come from an unwritten criterion rather
than from random error:

- **b1v4**: EK counted any photo → body metric (face-based BMI, garment and apparel
  measurement, child malnutrition); Claude counted only full-body composition, weight
  or shape, and also 3D body-shape reconstruction from photos.
- **b2**: EK counted body-composition measurement studies; Claude also counted
  contest-preparation strategy papers (peak week, refeeds, energy deficit).
- **b3v5**: EK counted face-based age and attribute estimation; Claude counted
  ranking, ordinal and Siamese comparison methods in any image domain, including
  medical imaging.

Next: write the criterion down per block, re-screen the 118 disagreements together,
and report the consensus set.
