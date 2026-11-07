"""Export the broad and relevant datasets as CSV, BibTeX and RIS."""
import json, csv, re, os, unicodedata, collections
from relevant import REL, SNOWBALL, THEMES

R = json.load(open('build/combined.json', encoding='utf-8'))

def tidy(s):
    """Drop invisible/private-use characters from OpenAlex strings; U+FFFD only occurs in a hyphenated initial."""
    if not s:
        return s
    s = s.replace('�', '-')
    s = ''.join(ch for ch in s if unicodedata.category(ch) not in ('Cf', 'Cc', 'Co', 'Cs'))
    return re.sub(r'\s+', ' ', s).strip()

# Venues missing in OpenAlex, filled from the DOI prefix / proceedings name
VENUE_FIX = {'W3090535222': ('International Joint Conference on Neural Networks (IJCNN)', 'conference', 'IEEE')}

for r in R:
    r['title'] = tidy(r['title'])
    r['authors'] = [tidy(a) for a in r['authors'] if tidy(a)]
    r['source'] = tidy(r['source'])
    r['publisher'] = tidy(r['publisher'])
    if r['id'] in VENUE_FIX:
        r['source'], r['source_type'], r['publisher'] = VENUE_FIX[r['id']]
by = {r['id']: r for r in R}
r_db = lambda i: by[i]['databases']
oa_url = lambda r: ('https://openalex.org/' + r['openalex_id']) if r.get('openalex_id') else ''
os.makedirs('results', exist_ok=True)

TYPE_RIS = {'article': 'JOUR', 'review': 'JOUR', 'conference-paper': 'CPAPER', 'book-chapter': 'CHAP'}
TYPE_BIB = {'article': 'article', 'review': 'article', 'conference-paper': 'inproceedings', 'book-chapter': 'incollection'}

def pages(r):
    a, b = r.get('first_page'), r.get('last_page')
    if a and b and a != b:
        return f'{a}--{b}'
    return a or ''

def key(r, used):
    au = r['authors'][0] if r['authors'] else 'anon'
    last = unicodedata.normalize('NFKD', au.split()[-1]).encode('ascii', 'ignore').decode()
    last = re.sub(r'[^A-Za-z]', '', last).lower() or 'anon'
    w = [x for x in re.findall(r'[A-Za-z]+', r['title']) if len(x) > 3]
    k = f"{last}{r['year']}{(w[0].lower() if w else '')}"
    base, i = k, 1
    while k in used:
        i += 1
        k = f'{base}{chr(96 + i)}'
    used.add(k)
    return k

def bibesc(s):
    return (s or '').replace('\\', '').replace('{', '').replace('}', '').replace('&', r'\&').replace('%', r'\%').replace('_', r'\_').replace('#', r'\#')

def write_all(rows, stem, extra_cols=()):
    cols = ['id', 'doi', 'title', 'authors', 'year', 'type', 'source', 'source_type', 'publisher',
            'volume', 'issue', 'pages', 'cited_by', 'blocks', 'databases', 'scopus_eid', 'wos_ut', 'keywords', 'abstract',
            *extra_cols, 'openalex_url', 'doi_url']
    with open(f'results/{stem}.csv', 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f)
        w.writerow(cols)
        for r in rows:
            base = dict(id=r['id'], doi=r['doi'] or '', title=r['title'], authors='; '.join(r['authors']),
                        year=r['year'], type=r['type'], source=r['source'] or '', source_type=r['source_type'] or '',
                        publisher=r['publisher'] or '', volume=r['volume'] or '', issue=r['issue'] or '',
                        pages=pages(r).replace('--', '-'), cited_by=r['cited_by'], blocks='+'.join(r['blocks']),
                        databases=r['databases'], scopus_eid=r['scopus_eid'], wos_ut=r['wos_ut'],
                        keywords='; '.join(r.get('keywords') or []), abstract=r.get('abstract') or '',
                        openalex_url=oa_url(r),
                        doi_url=('https://doi.org/' + r['doi']) if r['doi'] else '')
            for c in extra_cols:
                base[c] = r.get(c, '')
            w.writerow([base[c] for c in cols])
    used = set()
    with open(f'results/{stem}.bib', 'w', encoding='utf-8', newline='\n') as f:
        for r in rows:
            t = TYPE_BIB[r['type']]
            venue = 'journal' if t == 'article' else 'booktitle'
            fl = [('title', '{' + bibesc(r['title']) + '}'), ('author', bibesc(' and '.join(r['authors']))),
                  ('year', str(r['year'])), (venue, bibesc(r['source'])), ('publisher', bibesc(r['publisher'])),
                  ('volume', r['volume']), ('number', r['issue']), ('pages', pages(r)), ('doi', r['doi']),
                  ('url', oa_url(r) or (('https://doi.org/' + r['doi']) if r['doi'] else '')),
                  ('note', 'Found in ' + r['databases'] + ' (' + r['id'] + '); blocks ' + '+'.join(r['blocks']))]
            if r.get('abstract'):
                fl.append(('abstract', bibesc(re.sub(r'\s+', ' ', r['abstract']))))
            f.write(f'@{t}{{{key(r, used)},\n')
            f.write(',\n'.join(f'  {k} = {{{v}}}' for k, v in fl if v) + '\n}\n\n')
    with open(f'results/{stem}.ris', 'w', encoding='utf-8', newline='\n') as f:
        for r in rows:
            f.write(f"TY  - {TYPE_RIS[r['type']]}\n")
            f.write(f"TI  - {r['title']}\n")
            for a in r['authors']:
                f.write(f'AU  - {a}\n')
            f.write(f"PY  - {r['year']}\n")
            if r['source']:
                f.write(f"{'JO' if r['type'] in ('article', 'review') else 'T2'}  - {r['source']}\n")
            for tag, k in (('PB', 'publisher'), ('VL', 'volume'), ('IS', 'issue'), ('SP', 'first_page'), ('EP', 'last_page'), ('DO', 'doi')):
                if r.get(k):
                    f.write(f'{tag}  - {r[k]}\n')
            if r.get('abstract'):
                f.write('AB  - ' + re.sub(r'\s+', ' ', r['abstract']) + '\n')
            for kw in r.get('keywords') or []:
                f.write(f'KW  - {kw}\n')
            if oa_url(r):
                f.write(f"UR  - {oa_url(r)}\n")
            f.write(f"N1  - Found in {r['databases']} ({r['id']}); search blocks: {'+'.join(r['blocks'])}\n")
            f.write('ER  - \n\n')

# Broad set: OpenAlex + Scopus + WoS + the 4 snowballed seeds (merged by merge_db.py),
# sorted by block then citations
order = {'b2': 0, 'b4': 1, 'b1': 2, 'b1v3': 3, 'b3v4': 4, 'snowball': 5}
broad = sorted(R, key=lambda r: (min(order[b] for b in r['blocks']), -(r['cited_by'] or 0), r['id']))
assert len({r['id'] for r in broad}) == len(broad)
write_all(broad, 'dataset1_broad')

# Relevant set
rel = []
missing = [i for i, _, _ in REL if i not in by]
assert not missing, missing
for i, th, why in REL:
    r = dict(by[i]); r['theme'] = th; r['theme_name'] = THEMES[th]; r['why_relevant'] = why; r['found_by'] = 'database search (' + r['databases'] + ')'
    rel.append(r)
for s in SNOWBALL:
    r = dict(by[s['id']], theme=s['theme'], theme_name=THEMES[s['theme']], why_relevant=s['why'],
             found_by='snowballing (Scholar Labs seed)' + ('' if r_db(s['id']) == 'snowball' else '; also in ' + r_db(s['id'])))
    rel.append(r)
assert {r['id'] for r in rel} <= {r['id'] for r in broad}
assert len({r['id'] for r in rel}) == len(rel) <= 50
rel.sort(key=lambda r: (r['theme'], -r['year']))
write_all(rel, 'dataset2_relevant', extra_cols=('theme', 'theme_name', 'why_relevant', 'found_by'))

print('broad', len(broad), collections.Counter(r['type'] for r in broad))
print('broad years', sorted(collections.Counter(r['year'] for r in broad).items()))
bc = collections.Counter(b for r in broad for b in r['blocks']); print('broad blocks', bc)
print('relevant', len(rel), collections.Counter(r['theme'] for r in rel), collections.Counter(r['type'] for r in rel))
print('relevant no abstract', sum(1 for r in rel if not r.get('abstract')))
