"""Second pass on the OpenRefine affiliations (11 Nov 2026).

The OpenRefine rule took the first segment that named a university OR a college, so an
affiliation such as 'School of X, College of Y, University of Z, City, Country' became
'College of Y, Country'. For every cleaned institution that is still a sub-unit
(College/School/Faculty/Department/Institute of ...), the original affiliation of the same
record is re-read and the university or hospital segment is taken instead, when there is one.
Overwrites licensed/analysis/scopus_included_cleaned.csv and appends to cleaning_map.tsv.
"""
import csv, os, re
csv.field_size_limit(10**9)
os.chdir(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
P = 'licensed/analysis/scopus_included_cleaned.csv'
R = list(csv.DictReader(open(P, encoding='utf-8-sig')))
import glob
O = {}
for g in glob.glob('licensed/scopus_ta/scopus_*.csv'):
    for r in csv.DictReader(open(g, encoding='utf-8-sig')):
        O.setdefault(r['EID'], r)
SUB = re.compile(r'^(College|School|Faculty|Department|Dept\.?|Institute) ', re.I)
UNI = re.compile(r'universit|univ\.|universidad|universidade|universiti|hospital|institute of technology|vidyapeetham|eth z', re.I)
# values whose original string had no country, or a campus prefix
FINAL = {'Texas A and M International University, Texas A and M International University': 'Texas A and M International University, United States',
         'Coimbatore Amrita Vishwa Vidyapeetham, India': 'Amrita Vishwa Vidyapeetham, India'}
log = []
for r in R:
    new = []
    for inst in [a.strip() for a in r['Affiliations'].split(';') if a.strip()]:
        if SUB.match(inst):
            unit = inst.rsplit(',', 1)[0].strip()
            for orig in O[r['EID']]['Affiliations'].split(';'):
                if unit.lower() in orig.lower():
                    segs = [s.strip() for s in orig.split(',')]
                    u = [s for s in segs if UNI.search(s) and not SUB.match(s)]
                    if u:
                        fixed = f'{u[0]}, {segs[-1]}'
                        log.append((inst, fixed)); inst = fixed
                    break
        new.append(inst)
    new = [FINAL.get(i, i) for i in new]
    r['Affiliations'] = '; '.join(dict.fromkeys(new))
with open(P, 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.DictWriter(f, fieldnames=R[0].keys(), quoting=csv.QUOTE_ALL); w.writeheader(); w.writerows(R)
with open('bibliometric/openrefine/cleaning_map.tsv', 'a', encoding='utf-8', newline='\n') as f:
    for a, b in sorted(set(log)):
        f.write(f'Affiliations (second pass)\t{a}\t{b}\t{log.count((a, b))}\n')
print(len(log), 'fixed'); print(*sorted(set(log)), sep='\n')
