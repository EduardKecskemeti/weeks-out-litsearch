"""Recall of the Scopus blocks against the 50 papers of dataset 2 (results/dataset2_relevant.csv).

A paper counts as retrieved if its DOI (or normalised title) is in one of the Scopus
block exports; the decision comes from results/screening_scopus.tsv. Notes for the
misses were checked by hand in Scopus on 9 Nov 2026. Writes results/gold_recall.tsv.
"""
import csv, os, re, sys
csv.field_size_limit(10**9)
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, 'bibliometric')
from screen import BLOCKS  # noqa: E402  (re-runs screen.py; cheap)
norm = lambda t: re.sub(r'[^a-z0-9]', '', (t or '').lower())[:80]
dec = {l.split('\t')[0]: l.split('\t')[3] for l in open('results/screening_scopus.tsv', encoding='utf-8').read().strip().split('\n')[1:]}
by_doi, by_title = {}, {}
for b in BLOCKS:
    for r in csv.DictReader(open(f'licensed/scopus_ta/scopus_{b}.csv', encoding='utf-8-sig')):
        for key, m in ((r['DOI'].lower(), by_doi), (norm(r['Title']), by_title)):
            if key:
                m.setdefault(key, (r['EID'], []))[1].append(b)
NOTES = {
    'come back skinfolds': 'in Scopus; no physique-population term (b2 column 1)',
    'constrained deep neural network': 'in Scopus; no progression/target term (b3v5 column 2)',
    'uncovering developmental time': 'in Scopus; no ranking/ordinal term (b3v5 column 1)',
    'role of artificial intelligence in bodybuilding': 'not indexed in Scopus',
    'detection of body shape changes in obesity monitoring': 'in Scopus; no method term (b1v4 column 3)',
    'lean body mass and maximal strength': 'outside window (Scopus dates it 2026)',
}
rows, hit = [], 0
for g in csv.DictReader(open('results/dataset2_relevant.csv', encoding='utf-8-sig')):
    m = by_doi.get((g['doi'] or '').lower()) or by_title.get(norm(g['title']))
    if m:
        hit += 1
        rows.append([g['id'], g['doi'], g['year'], '+'.join(m[1]), dec[m[0]], '', g['title']])
    else:
        note = next((v for k, v in NOTES.items() if k in g['title'].lower()), 'not retrieved; check if indexed in Scopus')
        rows.append([g['id'], g['doi'], g['year'], '', 'not retrieved', note, g['title']])
with open('results/gold_recall.tsv', 'w', encoding='utf-8', newline='\n') as f:
    f.write('openalex_id\tdoi\tyear\tscopus_blocks\tdecision\tnote\ttitle\n')
    for r in rows:
        f.write('\t'.join(r) + '\n')
print('retrieved', hit, 'of', len(rows), '| included', sum(r[4] == 'include' for r in rows))
for r in rows:
    if r[4] != 'include':
        print(r[4], '|', r[5], '|', r[6][:80])
