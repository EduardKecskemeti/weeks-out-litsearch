"""Apply screening_decisions.py to the licensed Scopus exports -> results/screening_scopus.tsv (EID, title, decision)."""
import csv, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from screening_decisions import INCLUDE, EXCLUDE_CODE, DEFAULT_EXCLUDE, EXCL_RULES, NOT_BLOCK
csv.field_size_limit(10**9)
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BLOCKS = ['b1v4', 'b2', 'b3v5', 'b4', 'b5']
# b3v5 = b3v4 export (7 Nov 2026) followed by the records the added ranking phrases bring in (9 Nov 2026)
with open('licensed/scopus_ta/scopus_b3v5.csv', 'w', encoding='utf-8-sig', newline='') as out:
    parts = [list(csv.reader(open(f'licensed/scopus_ta/{n}.csv', encoding='utf-8-sig'))) for n in ('scopus_b3v4', 'scopus_b3v5_added')]
    assert parts[0][0] == parts[1][0]
    w = csv.writer(out, quoting=csv.QUOTE_ALL)
    w.writerows(parts[0] + parts[1][1:])
# b1v4 = b1v3 export without the records the NOT-block removes (decisions keep their b1v3 positions)
b1 = list(csv.reader(open('licensed/scopus_ta/scopus_b1v3.csv', encoding='utf-8-sig')))
ti, ab = b1[0].index('Title'), b1[0].index('Abstract')
keep = [i for i, r in enumerate(b1[1:]) if not re.search(NOT_BLOCK, r[ti] + ' ' + r[ab], re.I)]
assert len(b1) - 1 - len(keep) == 74 and not set(INCLUDE['b1v3']) - set(keep)
with open('licensed/scopus_ta/scopus_b1v4.csv', 'w', encoding='utf-8-sig', newline='') as out:
    csv.writer(out, quoting=csv.QUOTE_ALL).writerows([b1[0]] + [b1[1 + i] for i in keep])
POS = {'b1v4': keep}   # file row -> position used in screening_decisions
KEY = {'b1v4': 'b1v3'}
recs = {}
for b in BLOCKS:
    rows = list(csv.DictReader(open(f'licensed/scopus_ta/scopus_{b}.csv', encoding='utf-8-sig')))
    for j, r in enumerate(rows):
        i, k = (POS[b][j] if b in POS else j), KEY.get(b, b)
        if i in INCLUDE[k]:
            d = 'include'
        elif k == 'b1v3':
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
