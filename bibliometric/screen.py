"""Apply screening_decisions.py to the licensed Scopus exports -> results/screening_scopus.tsv (EID, title, decision)."""
import csv, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from screening_decisions import INCLUDE, EXCLUDE_CODE, DEFAULT_EXCLUDE, EXCL_RULES
csv.field_size_limit(10**9)
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BLOCKS = ['b1v3', 'b2', 'b3v5', 'b4']
# b3v5 = b3v4 export (7 Nov 2026) followed by the records the added ranking phrases bring in (9 Nov 2026)
with open('licensed/scopus_ta/scopus_b3v5.csv', 'w', encoding='utf-8-sig', newline='') as out:
    parts = [list(csv.reader(open(f'licensed/scopus_ta/{n}.csv', encoding='utf-8-sig'))) for n in ('scopus_b3v4', 'scopus_b3v5_added')]
    assert parts[0][0] == parts[1][0]
    w = csv.writer(out, quoting=csv.QUOTE_ALL)
    w.writerows(parts[0] + parts[1][1:])
recs = {}
for b in BLOCKS:
    rows = list(csv.DictReader(open(f'licensed/scopus_ta/scopus_{b}.csv', encoding='utf-8-sig')))
    assert max(INCLUDE[b]) < len(rows)
    for i, r in enumerate(rows):
        if i in INCLUDE[b]:
            d = 'include'
        elif b == 'b1v3':
            t = r['Title'].lower()
            d = next((c for c, p in EXCL_RULES if re.search(p, t)), 'E6')
        else:
            d = EXCLUDE_CODE.get(b, {}).get(i, DEFAULT_EXCLUDE[b])
        x = recs.setdefault(r['EID'], dict(eid=r['EID'], title=r['Title'], year=r['Year'], blocks=[], decisions=[]))
        x['blocks'].append(b); x['decisions'].append(f'{b}:{d}')
for x in recs.values():
    inc = any(d.endswith(':include') for d in x['decisions'])
    x['final'] = 'include' if inc else x['decisions'][0].split(':')[1]
os.makedirs('results', exist_ok=True)
with open('results/screening_scopus.tsv', 'w', encoding='utf-8', newline='\n') as f:
    f.write('eid\tyear\tblocks\tdecision\tper_block\ttitle\n')
    for x in recs.values():
        f.write('\t'.join([x['eid'], x['year'], '+'.join(x['blocks']), x['final'], ' '.join(x['decisions']),
                           re.sub(r'\s+', ' ', x['title'])]) + '\n')
import collections
print('records', len(recs), collections.Counter(x['final'] for x in recs.values()))
for b in BLOCKS:
    c = collections.Counter(d.split(':')[1] for x in recs.values() for d in x['decisions'] if d.startswith(b + ':'))
    print(b, dict(c))
