"""Check that the raw snapshot and the result files match CHECKSUMS.sha256,
and that the datasets satisfy the assignment criteria.

    python scripts/verify.py            # verify files as they are
    python scripts/verify.py --rebuild  # rebuild from data/raw first, then verify

Exit code 0 means everything matches.
"""
import csv, hashlib, os, re, subprocess, sys, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
ok = True

def fail(msg):
    global ok
    ok = False
    print('  FAIL', msg)

if '--rebuild' in sys.argv:
    subprocess.run(['bash', 'scripts/reproduce.sh'], check=True)

print('1. Checksums (CHECKSUMS.sha256)')
n = 0
for line in open('CHECKSUMS.sha256', encoding='utf-8'):
    if not line.strip() or line.startswith('#'):
        continue
    digest, path = line.split(maxsplit=1)
    path = path.strip().lstrip('*')
    if not os.path.exists(path):
        fail(f'missing {path}')
        continue
    h = hashlib.sha256(open(path, 'rb').read()).hexdigest()
    n += 1
    if h != digest:
        fail(f'{path} differs from recorded checksum')
print(f'  {n} files checked')

print('2. Assignment criteria')
def load(p):
    return list(csv.DictReader(open(p, encoding='utf-8-sig')))
broad = load('results/dataset1_broad.csv')
rel = load('results/dataset2_relevant.csv')
ALLOWED = {'article', 'review', 'conference-paper', 'book-chapter'}
for name, rows, limit in (('dataset 1', broad, 1500), ('dataset 2', rel, 50)):
    if len(rows) > limit:
        fail(f'{name} has {len(rows)} records (limit {limit})')
    bad_type = [r['id'] for r in rows if r['type'] not in ALLOWED]
    bad_year = [r['id'] for r in rows if not 2016 <= int(r['year']) <= 2025]
    dup_id = [k for k, v in collections.Counter(r['id'] for r in rows).items() if v > 1]
    dup_doi = [k for k, v in collections.Counter(r['doi'].lower() for r in rows if r['doi']).items() if v > 1]
    for label, bad in (('type', bad_type), ('year', bad_year), ('duplicate id', dup_id), ('duplicate DOI', dup_doi)):
        if bad:
            fail(f'{name}: {label} problems: {bad[:5]}')
    print(f'  {name}: {len(rows)} records, types {dict(collections.Counter(r["type"] for r in rows))}')
if not {r['id'] for r in rel} <= {r['id'] for r in broad}:
    fail('dataset 2 is not a subset of dataset 1')
if any(re.search(r'[Ѐ-ӿ]', r['title']) for r in broad):
    fail('Cyrillic (non-English) title found')

print('3. Record flow adds up (results/flow.tsv)')
flow = {r['step']: int(r['records']) for r in csv.DictReader(open('results/flow.tsv', encoding='utf-8'), delimiter='\t')}
ident = [v for k, v in flow.items() if k != 'Total records' and k in (
    'OpenAlex (title_and_abstract.search)', 'Scopus (TITLE-ABS)', 'Web of Science (TI/AB)', 'Snowballing (Scholar Labs seeds)')]
removed = open('results/removed_records.tsv', encoding='utf-8').read().strip().split('\n')[1:]
d_rules = sum(1 for x in removed if x.startswith('D'))
uniq = flow['Unique works after matching DOI and title']
oa_only = flow['Works found only by OpenAlex and removed by R1-R7']
print(f'  identified {sum(ident)} = total {flow["Total records"]}')
print(f'  {uniq} unique - {oa_only} (R1-R7) - {d_rules} (D1-D4) = {uniq - oa_only - d_rules}; dataset 1 has {len(broad)}')
if sum(ident) != flow['Total records'] or uniq - oa_only - d_rules != len(broad) or flow['Dataset 1'] != len(broad):
    fail('record counts do not add up')
if flow['Removed by D1-D4 (Scopus/WoS records)'] != d_rules:
    fail('D-rule count in flow.tsv differs from removed_records.tsv')
for col in ('databases',):
    if any(not r[col] for r in broad):
        fail('record without source database')

print('\nALL CHECKS PASSED' if ok else '\nSOME CHECKS FAILED')
sys.exit(0 if ok else 1)
