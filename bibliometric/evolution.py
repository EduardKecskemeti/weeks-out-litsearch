"""Evolution of collaboration and spread of the field, final set (182 papers), cleaned data.

Writes results/bibliometrics/evolution_by_period.tsv (per period: papers, distinct
institutions, distinct countries, new institutions, authors per paper, international
share) and corresponding_institutions.tsv (institution of the corresponding author).
"""
import csv, collections, os, re
csv.field_size_limit(10**9)
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
final = {l.split('\t')[0] for l in open('results/screening_scopus.tsv', encoding='utf-8').read().split('\n')[1:]
         if l and l.split('\t')[3] == 'include'}
R = [r for r in csv.DictReader(open('licensed/analysis/scopus_included_cleaned.csv', encoding='utf-8-sig')) if r['EID'] in final]
assert len(R) == len(final)
FIX = {'United States': 'USA', 'United Kingdom': 'UK', 'South Korea': 'Korea'}
def insts(r): return {a.strip() for a in r['Affiliations'].split(';') if a.strip()}
def countries(r): return {FIX.get(a.split(',')[-1].strip(), a.split(',')[-1].strip()) for a in insts(r)}
def nauth(r): return len([a for a in r['Authors'].split(';') if a.strip()])
PERIODS = [(2016, 2018), (2019, 2021), (2022, 2023), (2024, 2025)]
rows, seen = [], set()
for a, b in PERIODS:
    P = [r for r in R if a <= int(r['Year']) <= b]
    I = set().union(*[insts(r) for r in P]); C = set().union(*[countries(r) for r in P])
    rows.append((f'{a}-{b}', len(P), len(I), len(I - seen), len(C),
                 round(sum(map(nauth, P)) / len(P), 2), round(sum(len(countries(r)) > 1 for r in P) / len(P), 3)))
    seen |= I
os.makedirs('results/bibliometrics', exist_ok=True)
with open('results/bibliometrics/evolution_by_period.tsv', 'w', encoding='utf-8', newline='\n') as f:
    f.write('period\tpapers\tinstitutions\tnew_institutions\tcountries\tauthors_per_paper\tinternational_share\n')
    for x in rows: f.write('\t'.join(map(str, x)) + '\n')
# corresponding author institution: match the correspondence address to one of the cleaned institutions
corr = collections.Counter()
for r in R:
    ca = r['Correspondence Address'].lower()
    hit = [i for i in insts(r) if i.split(',')[0].lower() in ca]
    if hit: corr[sorted(hit, key=len)[-1]] += 1
with open('results/bibliometrics/corresponding_institutions.tsv', 'w', encoding='utf-8', newline='\n') as f:
    f.write('institution\tpapers\n')
    for k, v in corr.most_common(20): f.write(f'{k}\t{v}\n')
print(*rows, sep='\n'); print('matched corresponding:', sum(corr.values()), 'of', len(R)); print(corr.most_common(8))
