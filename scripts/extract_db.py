"""Reduce the licensed Scopus and Web of Science exports to public identifier tables.

The full exports (abstracts, keywords, cited references) are licensed by Elsevier
and Clarivate and are NOT in this repository. They sit in the git-ignored folder
licensed/ on the author's machine:

    licensed/scopus_ta/scopus_<block>.csv   Scopus CSV export, "all information"
    licensed/wos_ta/wos_<block>.txt         WoS tab-delimited, "Full Record and Cited References"

This script keeps only identifiers and basic citation fields (no abstracts,
keywords or references) and writes

    data/raw/scopus_ta.tsv
    data/raw/wos_ta.tsv

with one row per record and the blocks (queries) that retrieved it. It is run
once by the author; the rest of the pipeline starts from these two files.
"""
import csv, os, re, sys, unicodedata

csv.field_size_limit(10**9)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
BLOCKS = ['b1v3', 'b2', 'b3v4', 'b4']
COLS = ['id', 'doi', 'title', 'authors', 'year', 'doctype', 'source', 'publisher',
        'volume', 'issue', 'first_page', 'last_page', 'cited_by', 'blocks']

def clean(s):
    s = ''.join(ch for ch in (s or '') if unicodedata.category(ch) not in ('Cf', 'Cc', 'Co', 'Cs'))
    return re.sub(r'\s+', ' ', s).strip()

def first_last(name):
    """'Kim, Ijoon (60775139500)' -> 'Ijoon Kim'."""
    name = re.sub(r'\s*\(\d+\)$', '', clean(name))
    if ', ' in name:
        last, first = name.split(', ', 1)
        return f'{first} {last}'
    return name

def write(path, recs):
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\t'.join(COLS) + '\n')
        for r in recs.values():
            r['blocks'] = '+'.join(r['blocks'])
            f.write('\t'.join(clean(str(r[c])) for c in COLS) + '\n')

def scopus():
    out, hits = {}, {}
    for b in BLOCKS:
        rows = list(csv.DictReader(open(f'licensed/scopus_ta/scopus_{b}.csv', encoding='utf-8-sig')))
        hits[b] = len(rows)
        for r in rows:
            x = out.setdefault(r['EID'], dict(
                id=r['EID'], doi=r['DOI'].lower(), title=r['Title'],
                authors='; '.join(first_last(a) for a in r['Author full names'].split('; ') if a.strip()),
                year=r['Year'], doctype=r['Document Type'], source=r['Source title'], publisher=r['Publisher'],
                volume=r['Volume'], issue=r['Issue'], first_page=r['Page start'] or r['Art. No.'],
                last_page=r['Page end'], cited_by=r['Cited by'] or '0', blocks=[]))
            x['blocks'].append(b)
    write('data/raw/scopus_ta.tsv', out)
    return hits, len(out)

def wos():
    out, hits = {}, {}
    for b in BLOCKS:
        rows = list(csv.DictReader(open(f'licensed/wos_ta/wos_{b}.txt', encoding='utf-8-sig'),
                                   delimiter='\t', quoting=csv.QUOTE_NONE))
        hits[b] = len(rows)
        for r in rows:
            x = out.setdefault(r['UT'], dict(
                id=r['UT'], doi=(r['DI'] or '').lower(), title=r['TI'],
                authors='; '.join(first_last(a) for a in (r['AF'] or r['AU']).split('; ') if a.strip()),
                year=r['PY'], doctype=r['DT'], source=r['SO'], publisher=r['PU'],
                volume=r['VL'], issue=r['IS'], first_page=r['BP'] or r['AR'], last_page=r['EP'],
                cited_by=r['TC'] or '0', blocks=[]))
            x['blocks'].append(b)
    write('data/raw/wos_ta.tsv', out)
    return hits, len(out)

if __name__ == '__main__':
    if not os.path.isdir('licensed'):
        sys.exit('licensed/ not found: the full Scopus/WoS exports are not distributed (see data/raw/SNAPSHOT.md)')
    for name, fn in (('Scopus', scopus), ('Web of Science', wos)):
        hits, uniq = fn()
        print(f'{name}: hits per block {hits}, unique records {uniq}')
