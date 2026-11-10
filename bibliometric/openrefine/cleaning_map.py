"""Derive the value-level cleaning map from the OpenRefine export (10 Nov 2026).

Compares each included record before (licensed/analysis/scopus_included.csv) and after
(licensed/analysis/scopus_included_cleaned.csv) the OpenRefine cleanup and writes, for the
multi-valued columns, which original value became which cleaned value, with the number of
papers. Output: bibliometric/openrefine/cleaning_map.tsv (public; values only, no records).
"""
import csv, collections, difflib, os
csv.field_size_limit(10**9)
os.chdir(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
before = {r['EID']: r for r in csv.DictReader(open('licensed/analysis/scopus_included.csv', encoding='utf-8-sig'))}
after = {r['EID']: r for r in csv.DictReader(open('licensed/analysis/scopus_included_cleaned.csv', encoding='utf-8-sig'))}
assert set(before) == set(after)
# acronym merges that string similarity cannot recover (edits made in OpenRefine)
KNOWN = {'GAN': 'generative adversarial network', 'MRI': 'magnetic resonance imaging',
         'Three dimensional': '3D', 'Three-dimensional': '3D'}
# the cleaned value of an original value x must appear in the cleaned record of every
# paper that had x; among those candidates take the most similar string
mp = collections.Counter()
for col in ('Author Keywords', 'Index Keywords', 'Affiliations', 'Source title'):
    split = (lambda v: [x.strip() for x in v.split('; ') if x.strip()]) if col != 'Source title' else (lambda v: [v.strip()])
    cand, n = {}, collections.Counter()
    for e in before:
        a = set(split(after[e][col]))
        for x in set(split(before[e][col])):
            if x in a:
                continue
            cand[x] = cand[x] & a if x in cand else set(a)
            n[x] += 1
    for x, c in cand.items():
        hint = KNOWN.get(x)
        if hint in c:
            mp[(col, x, hint)] = n[x]
            continue
        best = max(c, key=lambda y: difflib.SequenceMatcher(None, x.lower(), y.lower()).ratio()) if c else '?'
        mp[(col, x, best)] = n[x]
with open('bibliometric/openrefine/cleaning_map.tsv', 'w', encoding='utf-8', newline='\n') as f:
    f.write('column\toriginal\tcleaned\tpapers\n')
    for (c, x, y), n in sorted(mp.items()):
        f.write(f'{c}\t{x}\t{y}\t{n}\n')
cnt = collections.Counter(c for c, _, _ in mp)
print('changed value pairs per column:', dict(cnt))
