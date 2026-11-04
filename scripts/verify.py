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
broad = load('results/dataset1_broad_openalex.csv')
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

print('3. Cleaning log adds up')
removed = open('results/removed_records.tsv', encoding='utf-8').read().strip().split('\n')[1:]
snow = sum(1 for r in broad if r['blocks'] == 'snowball')
print(f'  1251 retrieved - {len(removed)} removed + {snow} snowballed = {1251 - len(removed) + snow}')
if 1251 - len(removed) + snow != len(broad):
    fail('record counts do not add up')

print('\nALL CHECKS PASSED' if ok else '\nSOME CHECKS FAILED')
sys.exit(0 if ok else 1)
