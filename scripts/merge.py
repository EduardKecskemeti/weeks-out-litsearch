"""Merge v1 export (with abstracts) and the v2 new records into one v2 dataset."""
import json, glob, collections, os

v1 = json.load(open('data/raw/openalex_broad_2016-2025.json', encoding='utf-8'))
v1rows = {r['openalex'].rsplit('/', 1)[1]: r for r in v1['rows']}

bm = {}
for tok in open('data/raw/blockmap_v2.txt', encoding='utf-8').read().split():
    wid, b = tok.split(':')
    bm[wid] = b.split('+')

def nz(x):
    return x if x != '' else None

new = {}
for f in sorted(glob.glob('data/raw/new_chunk*.txt')):
    for line in open(f, encoding='utf-8').read().strip().split('\n'):
        p = line.split('¦')
        assert len(p) == 15, (f, len(p), line[:60])
        wid = p[0]
        new[wid] = dict(openalex='https://openalex.org/' + wid, doi=nz(p[1]), title=p[2],
                        year=int(p[3]), date=None, type=p[4], language='en', source=nz(p[5]),
                        source_type=nz(p[6]), publisher=nz(p[7]),
                        authors=[a for a in p[8].split('; ') if a],
                        cited_by=int(p[9]) if p[9] else 0, volume=nz(p[10]), issue=nz(p[11]),
                        first_page=nz(p[12]), last_page=nz(p[13]), keywords=[], abstract=None,
                        blocks=p[14].split('+'))

rows = []
for wid, blocks in bm.items():
    if wid in new:
        r = new[wid]
    else:
        r = dict(v1rows[wid])
        if r.get('doi'):
            r['doi'] = r['doi'].replace('https://doi.org/', '')
    r['blocks'] = blocks
    r['id'] = wid
    rows.append(r)

print('merged', len(rows), 'from v1', sum(1 for w in bm if w not in new), 'new', len(new))
print(collections.Counter(r['type'] for r in rows))
os.makedirs('build', exist_ok=True)
json.dump(rows, open('build/merged_v2.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
