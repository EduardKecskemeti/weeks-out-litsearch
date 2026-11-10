"""Build VOSviewer (Online) network files from the final 182-paper set (cleaned in OpenRefine).

- results/vosviewer/keywords_cooccurrence.json: author keywords with >= 3 occurrences, full
  counting of co-occurrence, scores = average publication year and average citations
- results/vosviewer/countries_coauthorship.json: countries with >= 3 papers, links = papers
  co-authored by both countries
Layout and clustering are left to VOSviewer (default VOS parameters). Aggregates only.
"""
import csv, collections, itertools, json, os, re
csv.field_size_limit(10**9)
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CLEAN = 'licensed/analysis/scopus_included_cleaned.csv'
final = {l.split('\t')[0] for l in open('results/screening_scopus.tsv', encoding='utf-8').read().split('\n')[1:]
         if l and l.split('\t')[3] == 'include'}
R = [r for r in csv.DictReader(open(CLEAN, encoding='utf-8-sig')) if r['EID'] in final]
assert len(R) == len(final)

def network(sets, years, cites, min_occ, terms):
    occ = collections.Counter(k for s in sets for k in s)
    keep = sorted(k for k, v in occ.items() if v >= min_occ)
    idx = {k: i + 1 for i, k in enumerate(keep)}
    yr, ct = collections.defaultdict(list), collections.defaultdict(list)
    link = collections.Counter()
    for s, y, c in zip(sets, years, cites):
        s = sorted(k for k in s if k in idx)
        for k in s:
            yr[k].append(y); ct[k].append(c)
        for a, b in itertools.combinations(s, 2):
            link[(idx[a], idx[b])] += 1
    items = [{'id': idx[k], 'label': k,
              'weights': {terms: occ[k], 'Links': sum(1 for (a, b) in link if idx[k] in (a, b)),
                          'Total link strength': sum(v for (a, b), v in link.items() if idx[k] in (a, b))},
              'scores': {'Avg. pub. year': round(sum(yr[k]) / len(yr[k]), 2),
                         'Avg. citations': round(sum(ct[k]) / len(ct[k]), 2)}} for k in keep]
    links = [{'source_id': a, 'target_id': b, 'strength': v} for (a, b), v in sorted(link.items())]
    return {'network': {'items': items, 'links': links}}, len(items), len(links)

years = [int(r['Year']) for r in R]
cites = [int(r['Cited by'] or 0) for r in R]
kw = [{k.strip().lower() for k in r['Author Keywords'].split(';') if k.strip()} for r in R]
COUNTRY_FIX = {'United States': 'USA', 'United Kingdom': 'UK', 'South Korea': 'Korea', 'Russian Federation': 'Russia'}
co = [{COUNTRY_FIX.get(a.split(',')[-1].strip(), a.split(',')[-1].strip()) for a in r['Affiliations'].split(';') if a.strip()} for r in R]
os.makedirs('results/vosviewer', exist_ok=True)
for name, sets, m, t in (('keywords_cooccurrence', kw, 3, 'Occurrences'), ('countries_coauthorship', co, 3, 'Documents')):
    net, ni, nl = network(sets, years, cites, m, t)
    json.dump(net, open(f'results/vosviewer/{name}.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print(name, ni, 'items', nl, 'links')
