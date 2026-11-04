# Raw snapshot: where each file came from

Everything in `results/` is generated from the files in this folder by
`scripts/reproduce.sh`. Nothing in this folder is edited by hand. Its SHA-256
checksums are in `CHECKSUMS.sha256` at the repository root.

All records come from the **OpenAlex API** (`https://api.openalex.org/works`).
OpenAlex data is released under CC0. The searches were run from a web browser,
because OpenAlex was the only search database reachable from the tools used.

## Files

| File | Records | What it is |
|---|---|---|
| `openalex_broad_2016-2025.json` | 881 | **Run 1**, exported 2026-10-19 15:10 UTC. Full records, including abstracts and keywords. Queries b1, b2 and b3 (original), filter `type:article\|book-chapter\|review` (conference papers missing). The queries and filter are stored in the file's `meta` field. |
| `blockmap_v2.txt` | 1,251 | **Run 2**, same day: the final four queries (b1v3, b2, b3v4, b4, plus b1 as a label) with the corrected filter that includes conference papers. One token per record: `<OpenAlex ID>:<blocks that matched it>`. This file defines which records are in the search result. |
| `new_chunk0.txt` … `new_chunk5.txt` | 559 | Records in run 2 that were not already in run 1. One record per line, 15 fields separated by `¦`: id, DOI, title, year, type, source, source type, publisher, authors (`; `), cited-by count, volume, issue, first page, last page, blocks. Abstracts were not exported for these. |

`scripts/merge.py` builds the run-2 result set: for each of the 1,251 IDs in
`blockmap_v2.txt` it takes the full run-1 record if there is one (692 records)
and the `new_chunk` record otherwise (559 records). The 189 run-1 records that
the final queries no longer match are left out.

## How the run-2 records were transferred

The browser could not save a second download, so the 559 new records were
copied out as text in six parts. Each part was checked against a checksum
computed in the browser before it was accepted (DJB2-xor over UTF-16 code
units: `h = 5381; h = ((h * 33) ^ code) mod 2^32`, on the text with surrounding
whitespace stripped):

| Part | Characters | Checksum |
|---|---|---|
| new_chunk0.txt | 30,085 | 1750003194 |
| new_chunk1.txt | 30,365 | 448180224 |
| new_chunk2.txt | 31,584 | 3262611459 |
| new_chunk3.txt | 33,861 | 2374000768 |
| new_chunk4.txt | 30,109 | 761297125 |
| new_chunk5.txt | 28,464 | 799116228 |
| blockmap_v2.txt | 21,965 | 847944873 |

All seven match.

## Added outside the search

Four seed papers found during term refinement (Google Scholar Labs) did not
match any query. Their metadata was looked up in OpenAlex by title on
2026-10-19 and is written out in `scripts/relevant.py` (`SNOWBALL`). For
Liu et al. 2018, the author order was corrected to the order printed in the
CVPR paper.

## How to check it independently

- Every record has an OpenAlex ID: `https://openalex.org/W…` opens the record.
- Most records have a DOI: `https://doi.org/…` opens the publisher's page.
- `scripts/fetch_openalex.py` re-runs the final queries live and reports how
  many archived records come back. The index grows over time, so expect a
  high overlap, not an exact match.
