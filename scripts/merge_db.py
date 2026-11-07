"""Merge the cleaned OpenAlex set with the Scopus and Web of Science results.

Inputs
    build/merged_v2.json   all 1,251 OpenAlex hits (from merge.py)
    build/clean_v2.json    OpenAlex hits kept by clean.py (rules R1-R7)
    data/raw/scopus_ta.tsv Scopus TITLE-ABS hits (identifiers and citation fields only)
    data/raw/wos_ta.tsv    Web of Science TI/AB hits (identifiers and citation fields only)
    scripts/relevant.py    SNOWBALL: 4 seed papers added by hand

Records are grouped when they share a DOI or a normalised title (union-find).
Each group becomes one record. Its metadata comes from OpenAlex when available
(it carries abstracts and keywords), otherwise from Scopus, otherwise from WoS.

Scopus/WoS-only groups go through the same cleaning as OpenAlex plus:
    D1 publication year outside 2016-2025 (WoS early-access records dated 2026)
    D2 retracted publication
    D3 same work as an OpenAlex record removed by R1, R2, R3 or R6 (removed for the
       same reason). Works removed under R4/R5 (no DOI and no venue; repository copy
       or preprint) are kept when Scopus or WoS index the published version.
    D4 not a research contribution (hand-checked; list below)

Outputs
    build/combined.json        dataset 1 before export
    results/removed_records.tsv (appended: D-rule removals)
    results/flow.tsv           PRISMA-style record flow
"""
import csv, json, re, collections
from relevant import SNOWBALL

norm = lambda t: re.sub(r'[^a-z0-9]', '', (t or '').lower())

ALL = json.load(open('build/merged_v2.json', encoding='utf-8'))
KEPT = json.load(open('build/clean_v2.json', encoding='utf-8'))
kept_ids = {r['id'] for r in KEPT}
removed_rule = {}
for line in open('results/removed_records.tsv', encoding='utf-8').read().strip().split('\n')[1:]:
    rule, i, _ = line.split('\t', 2)
    removed_rule[i] = rule

def load_tsv(path):
    return list(csv.DictReader(open(path, encoding='utf-8'), delimiter='\t', quoting=csv.QUOTE_NONE))
S = load_tsv('data/raw/scopus_ta.tsv')
W = load_tsv('data/raw/wos_ta.tsv')

# --- union-find over all records -------------------------------------------------
nodes = [('openalex', r['id'], (r['doi'] or '').lower(), r['title']) for r in ALL]
nodes += [('snowball', s['id'], s['doi'].lower(), s['title']) for s in SNOWBALL]
nodes += [('scopus', r['id'], r['doi'], r['title']) for r in S]
nodes += [('wos', r['id'], r['doi'], r['title']) for r in W]
parent = {}
def find(a):
    while parent.setdefault(a, a) != a:
        parent[a] = parent[parent[a]]
        a = parent[a]
    return a
first = {}
for src, i, doi, title in nodes:
    n = (src, i)
    find(n)
    keys = ([('doi', doi)] if doi else []) + ([('title', norm(title))] if len(norm(title)) > 20 else [])
    for k in keys:
        if k in first:
            parent[find(n)] = find(first[k])
        else:
            first[k] = n
groups = collections.defaultdict(list)
for src, i, _, _ in nodes:
    groups[find((src, i))].append((src, i))

# --- turn a Scopus / WoS row into a dataset record ---------------------------------
def doctype(src, dt):
    d = dt.lower()
    if 'book chapter' in d:
        return 'book-chapter'
    if 'conference paper' in d or 'proceedings paper' in d:
        return 'conference-paper'
    if 'review' in d:
        return 'review'
    return 'article'

SMALL = {'of', 'and', 'the', 'in', 'on', 'for', 'to', 'a', 'an', 'at', 'by', 'with', 'from'}
def tidy_caps(s):
    """WoS gives venue names in capitals; convert to title case."""
    if not s or s != s.upper():
        return s
    out = []
    for k, w in enumerate(s.split(' ')):
        lw = w.lower()
        if re.search(r'\d', w) or (len(w) <= 5 and w.strip('(),:-').isalpha() and w.startswith('(')):
            out.append(lw if re.match(r'^\d+(st|nd|rd|th)$', lw) else w)
        elif k and lw in SMALL:
            out.append(lw)
        else:
            out.append(lw[:1].upper() + lw[1:])
    return ' '.join(out)

def from_db(src, r):
    return dict(id=r['id'], doi=r['doi'] or None, title=r['title'], year=int(r['year']) if r['year'] else None,
                date=None, type=doctype(src, r['doctype']), language='en',
                source=tidy_caps(r['source']) or None, source_type=None, publisher=tidy_caps(r['publisher']) or None,
                authors=[a for a in r['authors'].split('; ') if a], cited_by=int(r['cited_by'] or 0),
                volume=r['volume'] or None, issue=r['issue'] or None, first_page=r['first_page'] or None,
                last_page=r['last_page'] or None, keywords=[], abstract=None,
                blocks=r['blocks'].split('+'), doctype_raw=r['doctype'])

BY = {('openalex', r['id']): r for r in ALL}
BY.update({('snowball', s['id']): dict(s, language='en', keywords=[], abstract=None, blocks=['snowball']) for s in SNOWBALL})
BY.update({('scopus', r['id']): from_db('scopus', r) for r in S})
BY.update({('wos', r['id']): from_db('wos', r) for r in W})

D3_RULES = {'R1', 'R2', 'R3', 'R6'}

# D4: hand-checked Scopus/WoS-only records that are not research contributions
NOT_RESEARCH = {
    '2-s2.0-85188140912': 'encyclopedia entry ("Ephedra", Encyclopedia of Toxicology)',
}

out, removed, flow_dupes = [], [], 0
for members in groups.values():
    srcs = {s for s, _ in members}
    oa_kept = [BY[m] for m in members if m[0] == 'openalex' and m[1] in kept_ids]
    oa_removed = [m[1] for m in members if m[0] == 'openalex' and m[1] not in kept_ids]
    snow = [BY[m] for m in members if m[0] == 'snowball']
    sc = [BY[m] for m in members if m[0] == 'scopus']
    wo = [BY[m] for m in members if m[0] == 'wos']
    if oa_kept or snow:
        base = dict((oa_kept or snow)[0])
    elif srcs == {'openalex'}:
        continue                                   # removed by clean.py, already logged
    else:
        base = dict((sc or wo)[0])
        rep = (base['id'], base['title'])
        if oa_removed and removed_rule[oa_removed[0]].split(' ')[0] in D3_RULES:
            removed.append(('D3 same work as removed OpenAlex record (' + removed_rule[oa_removed[0]].split(' ')[0] + ')', *rep)); continue
        if not 2016 <= (base['year'] or 0) <= 2025 or any(x['year'] and not 2016 <= x['year'] <= 2025 for x in wo + sc):
            removed.append(('D1 year outside 2016-2025', *rep)); continue
        if any('retract' in x['doctype_raw'].lower() or re.match(r'\s*retract', x['title'], re.I) for x in sc + wo):
            removed.append(('D2 retracted', *rep)); continue
        if base['id'] in NOT_RESEARCH:
            removed.append(('D4 not a research contribution', *rep)); continue
    # a kept record matched by a retracted WoS/Scopus entry is also dropped
    if any('retract' in x['doctype_raw'].lower() for x in sc + wo):
        removed.append(('D2 retracted', base['id'], base['title'])); continue
    blocks = []
    for m in members:
        if m[0] == 'openalex' and m[1] not in kept_ids:
            continue
        blocks += [b for b in BY[m]['blocks'] if b not in blocks]
    base['blocks'] = blocks
    base['databases'] = '+'.join(d for d in ('openalex', 'scopus', 'wos') if d in srcs and
                                 (d != 'openalex' or oa_kept)) or 'snowball'
    base['scopus_eid'] = '; '.join(x['id'] for x in sc)
    base['wos_ut'] = '; '.join(x['id'] for x in wo)
    base['openalex_id'] = (oa_kept or snow)[0]['id'] if (oa_kept or snow) else ''
    if not base.get('doi'):
        base['doi'] = next((x['doi'] for x in sc + wo if x['doi']), None)
    base.pop('doctype_raw', None)
    out.append(base)

with open('results/removed_records.tsv', 'a', encoding='utf-8', newline='\n') as f:
    for x in removed:
        f.write('\t'.join(x) + '\n')

# --- flow ----------------------------------------------------------------------------
n_o, n_s, n_w = len(ALL), len(S), len(W)
removed_oa = len(ALL) - len(KEPT)
merged_db = sum(1 for g in groups.values() if {s for s, _ in g} - {'openalex', 'snowball'})
flow = [
    ('identified', 'OpenAlex (title_and_abstract.search)', n_o),
    ('identified', 'Scopus (TITLE-ABS)', n_s),
    ('identified', 'Web of Science (TI/AB)', n_w),
    ('identified', 'Snowballing (Scholar Labs seeds)', len(SNOWBALL)),
    ('identified', 'Total records', n_o + n_s + n_w + len(SNOWBALL)),
    ('deduplicated', 'Unique works after matching DOI and title', len(groups)),
    ('screened-out', 'Works found only by OpenAlex and removed by R1-R7', sum(1 for g in groups.values() if {s for s, _ in g} == {'openalex'} and not any(m[1] in kept_ids for m in g))),
    ('screened-out', 'Removed by D1-D4 (Scopus/WoS records)', len(removed)),
    ('included', 'Dataset 1', len(out)),
]
with open('results/flow.tsv', 'w', encoding='utf-8', newline='\n') as f:
    f.write('stage\tstep\trecords\n')
    for x in flow:
        f.write('\t'.join(map(str, x)) + '\n')
for x in flow:
    print(f'{x[0]:13} {x[1]:45} {x[2]}')
print(collections.Counter(r['databases'] for r in out))
print(collections.Counter(x[0] for x in removed))
json.dump(out, open('build/combined.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
