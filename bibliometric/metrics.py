"""Quantitative (performance) analysis of the screened Scopus set.

Reads the licensed Scopus exports (licensed/scopus_ta/) and the screening
decisions (results/screening_scopus.tsv). Writes only aggregate tables and
figures (no abstracts or reference lists) to results/bibliometrics/.

Metrics follow Donthu et al. (2021), "How to conduct a bibliometric analysis",
J. Business Research 133:285-296 (performance analysis):
  publication-related   TP, NCA, SA, CA, NAY, PAY
  citation-related      TC, AC
  combined              CI, CC, NCP, PCP, CCP, h, g, i10, i100
Citation counts are the Scopus "Cited by" values on the export date.
"""
import collections, csv, json, math, os, re, statistics
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

csv.field_size_limit(10**9)
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = 'results/bibliometrics'
os.makedirs(OUT, exist_ok=True)
BLOCKS = ['b1v4', 'b2', 'b3v5', 'b4', 'b5']
LABEL = {'b1v4': 'b1v4: body composition\nor shape from images', 'b2': 'b2: physique-sport\npreparation',
         'b3v5': 'b3v5: ranking and ordinal\nmethods on images', 'b4': 'b4: AI in\nbodybuilding',
         'b5': 'b5: validation of\nphoto-based estimates'}
EXPORT_DATE = '2026-11-07'

# ---------------------------------------------------------------- load
decision = {}
for line in open('results/screening_scopus.tsv', encoding='utf-8').read().strip().split('\n')[1:]:
    f = line.split('\t')
    decision[f[0]] = f[3]
recs = {}
for b in BLOCKS:
    for r in csv.DictReader(open(f'licensed/scopus_ta/scopus_{b}.csv', encoding='utf-8-sig')):
        x = recs.setdefault(r['EID'], dict(r, blocks=[]))
        x['blocks'].append(b)
ALL = list(recs.values())
INC = [r for r in ALL if decision[r['EID']] == 'include']
# a record included through one block may also sit in another block where it was excluded;
# for per-block figures, count a record under each block in which it was retrieved
def block_of(r):
    return [b for b in r['blocks']]

def authors(r):
    ids = [a.strip() for a in r['Author(s) ID'].split(';') if a.strip()]
    if not ids or r['Authors'].strip() in ('[No author name available]', ''):
        return []
    return ids

def country_of(aff):
    c = aff.rsplit(',', 1)[-1].strip()
    return {'United States': 'USA', 'United Kingdom': 'UK', 'Russian Federation': 'Russia',
            'South Korea': 'Korea', 'Republic of Korea': 'Korea', 'Viet Nam': 'Vietnam',
            'Czech Republic': 'Czechia', 'Taiwan': 'Taiwan'}.get(c, c)

def countries(r):
    """Countries per author from 'Authors with affiliations' (one entry per author)."""
    out = []
    for a in r['Authors with affiliations'].split('; '):
        a = a.strip()
        if ',' in a:
            out.append(country_of(a))
    return out

def corr_country(r):
    ca = r['Correspondence Address']
    if not ca:
        return None
    part = ca.split(';')[1] if ';' in ca else ca
    part = re.sub(r'email:.*', '', part).strip().strip(';').strip()
    return country_of(part) if part else None

def kw(r, col):
    return [k.strip().lower() for k in r[col].split(';') if k.strip()]

def cites(r):
    return int(r['Cited by'] or 0)

# ---------------------------------------------------------------- performance metrics
def perf(rs):
    tp = len(rs)
    au = [authors(r) for r in rs]
    nca = len({a for al in au for a in al})
    sa = sum(1 for al in au if len(al) == 1)
    ca = sum(1 for al in au if len(al) > 1)
    years = sorted({int(r['Year']) for r in rs})
    nay = len(years)
    c = sorted((cites(r) for r in rs), reverse=True)
    tc = sum(c)
    h = sum(1 for i, x in enumerate(c, 1) if x >= i)
    g = 0
    for i in range(1, tp + 1):
        if sum(c[:i]) >= i * i:
            g = i
    ncp = sum(1 for x in c if x > 0)
    # collaboration index (Elango & Rajendran): authors of multi-authored papers / multi-authored papers
    ci = sum(len(al) for al in au if len(al) > 1) / ca if ca else 0
    # collaboration coefficient (Ajiferuke et al. 1988): 1 - mean(1/j)
    cc = 1 - sum(1 / len(al) for al in au if al) / sum(1 for al in au if al)
    # authors of the h-core and of the i10 papers
    ranked = sorted(rs, key=cites, reverse=True)
    h_auth = len({a for r in ranked[:h] for a in authors(r)})
    i10_auth = len({a for r in rs if cites(r) >= 10 for a in authors(r)})
    intl = sum(1 for r in rs if len(set(countries(r))) > 1)
    return dict(TP=tp, NCA=nca, SA=sa, CA=ca, NAY=nay, PAY=round(tp / nay, 2) if nay else 0,
                TC=tc, AC=round(tc / tp, 2) if tp else 0, CI=round(ci, 2), CC=round(cc, 3),
                NCP=ncp, PCP=round(ncp / tp, 3) if tp else 0, CCP=round(tc / ncp, 2) if ncp else 0,
                h=h, g=g, i10=sum(1 for x in c if x >= 10), i100=sum(1 for x in c if x >= 100),
                i200=sum(1 for x in c if x >= 200), median_citations=statistics.median(c) if c else 0,
                authors_in_h_core=h_auth, authors_in_i10=i10_auth,
                authors_per_paper=round(sum(len(al) for al in au) / tp, 2) if tp else 0,
                international_coauthorship=round(intl / tp, 3) if tp else 0)

metrics = {'retrieved (all blocks, before screening)': perf(ALL), 'screened set (included)': perf(INC)}
for b in BLOCKS:
    metrics[f'{b} included'] = perf([r for r in INC if b in r['blocks']])
json.dump(dict(export_date=EXPORT_DATE, database='Scopus', fields='TITLE-ABS', years='2016-2025',
               metrics=metrics), open(f'{OUT}/performance_metrics.json', 'w'), indent=1)

def write_tsv(name, header, rows):
    with open(f'{OUT}/{name}', 'w', encoding='utf-8', newline='\n') as f:
        f.write('\t'.join(header) + '\n')
        for row in rows:
            f.write('\t'.join(str(x) for x in row) + '\n')

cols = list(metrics['screened set (included)'].keys())
write_tsv('performance_metrics.tsv', ['set'] + cols, [[k] + [v[c] for c in cols] for k, v in metrics.items()])

# ---------------------------------------------------------------- distributions
years = list(range(2016, 2026))
by_year = {b: collections.Counter(int(r['Year']) for r in INC if b in r['blocks']) for b in BLOCKS}
tot_year = collections.Counter(int(r['Year']) for r in INC)
write_tsv('year_distribution.tsv', ['year'] + BLOCKS + ['all_included', 'citations'],
          [[y] + [by_year[b][y] for b in BLOCKS] + [tot_year[y], sum(cites(r) for r in INC if int(r['Year']) == y)]
           for y in years])

doc = collections.Counter(r['Document Type'] for r in INC)
write_tsv('document_types.tsv', ['type', 'n'], doc.most_common())

src = collections.Counter(r['Source title'] for r in INC)
src_c = collections.Counter()
for r in INC:
    src_c[r['Source title']] += cites(r)
write_tsv('top_sources.tsv', ['source', 'TP', 'TC'], [(s, n, src_c[s]) for s, n in src.most_common(25)])

# countries: whole counting (a paper counts once for each country among its authors)
ctry = collections.Counter()
ctry_c = collections.Counter()
for r in INC:
    for c in set(countries(r)):
        ctry[c] += 1
        ctry_c[c] += cites(r)
corr = collections.Counter(corr_country(r) for r in INC if corr_country(r))
# single- vs multiple-country publications by corresponding-author country
scp, mcp = collections.Counter(), collections.Counter()
for r in INC:
    c = corr_country(r)
    if not c:
        continue
    (mcp if len(set(countries(r))) > 1 else scp)[c] += 1
write_tsv('countries.tsv', ['country', 'TP_whole_count', 'TC', 'corresponding_author', 'SCP', 'MCP'],
          [(c, n, ctry_c[c], corr[c], scp[c], mcp[c]) for c, n in ctry.most_common(30)])

# affiliations (uncleaned: name variants are merged only after the OpenRefine step)
aff = collections.Counter()
for r in INC:
    for a in {x.strip() for x in r['Affiliations'].split(';') if x.strip()}:
        aff[a] += 1
write_tsv('top_affiliations_uncleaned.tsv', ['affiliation', 'TP'], aff.most_common(30))

# authors by Scopus author ID (avoids most name-variant problems)
name_of, au_tp, au_tc = {}, collections.Counter(), collections.Counter()
for r in INC:
    names = [n.strip() for n in r['Author full names'].split(';')]
    for n in names:
        m = re.match(r'(.*)\((\d+)\)$', n)
        if m:
            name_of[m.group(2)] = m.group(1).strip()
    for a in authors(r):
        au_tp[a] += 1
        au_tc[a] += cites(r)
au_h = {}
for a in au_tp:
    c = sorted((cites(r) for r in INC if a in authors(r)), reverse=True)
    au_h[a] = sum(1 for i, x in enumerate(c, 1) if x >= i)
top_auth = sorted(au_tp, key=lambda a: (-au_tp[a], -au_tc[a]))[:25]
write_tsv('top_authors.tsv', ['author', 'scopus_author_id', 'TP', 'TC', 'h_in_set'],
          [(name_of.get(a, a), a, au_tp[a], au_tc[a], au_h[a]) for a in top_auth])
# Lotka-style productivity distribution
lot = collections.Counter(au_tp.values())
write_tsv('author_productivity.tsv', ['papers_per_author', 'authors'], sorted(lot.items()))

top_cited = sorted(INC, key=cites, reverse=True)[:20]
write_tsv('top_cited.tsv', ['eid', 'year', 'first_author', 'title', 'source', 'cited_by', 'blocks'],
          [(r['EID'], r['Year'], r['Authors'].split(';')[0], re.sub(r'\s+', ' ', r['Title']), r['Source title'],
            cites(r), '+'.join(r['blocks'])) for r in top_cited])

# keywords
akw = collections.Counter(k for r in INC for k in set(kw(r, 'Author Keywords')))
ikw = collections.Counter(k for r in INC for k in set(kw(r, 'Index Keywords')))
write_tsv('author_keywords_top.tsv', ['keyword', 'papers'], akw.most_common(40))
write_tsv('index_keywords_top.tsv', ['keyword', 'papers'], ikw.most_common(40))
# keyword evolution: share of papers using a keyword, 2016-2020 vs 2021-2025
p1 = [r for r in INC if int(r['Year']) <= 2020]
p2 = [r for r in INC if int(r['Year']) >= 2021]
k1 = collections.Counter(k for r in p1 for k in set(kw(r, 'Author Keywords')))
k2 = collections.Counter(k for r in p2 for k in set(kw(r, 'Author Keywords')))
keys = sorted(set(k for k, _ in akw.most_common(40)), key=lambda k: -(k1[k] + k2[k]))
write_tsv('author_keywords_by_period.tsv', ['keyword', '2016-2020', '2021-2025', 'share_2016-2020', 'share_2021-2025'],
          [(k, k1[k], k2[k], round(k1[k] / len(p1), 3), round(k2[k] / len(p2), 3)) for k in keys])

# block overlap
ov = collections.Counter('+'.join(r['blocks']) for r in INC)
write_tsv('block_overlap.tsv', ['blocks', 'n'], ov.most_common())

# screening summary per block
scr = collections.Counter()
for r in ALL:
    for b in r['blocks']:
        scr[(b, 'retrieved')] += 1
        scr[(b, 'included')] += decision[r['EID']] == 'include'
write_tsv('screening_summary.tsv', ['block', 'retrieved', 'included', 'precision'],
          [(b, scr[(b, 'retrieved')], scr[(b, 'included')], round(scr[(b, 'included')] / scr[(b, 'retrieved')], 2))
           for b in BLOCKS] + [('all (unique)', len(ALL), len(INC), round(len(INC) / len(ALL), 2))])

# ---------------------------------------------------------------- figures
S1, S2, S3, S4, S5 = '#2a78d6', '#eb6834', '#1baf7a', '#eda100', '#e87ba4'   # categorical slots 1-5 (fixed order)
INK, INK2, GRID = '#0b0b0b', '#52514e', '#e4e3df'
COL = dict(zip(BLOCKS, [S1, S2, S3, S4, S5]))
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9, 'axes.edgecolor': INK2, 'axes.labelcolor': INK2,
                     'xtick.color': INK2, 'ytick.color': INK2, 'axes.spines.top': False, 'axes.spines.right': False})

def save(fig, name):
    fig.savefig(f'{OUT}/{name}.png', dpi=200, bbox_inches='tight')
    fig.savefig(f'{OUT}/{name}.pdf', bbox_inches='tight')
    plt.close(fig)

# 1. publications per year, small multiples per block (one axis each, same y-scale)
fig, axes = plt.subplots(1, 5, figsize=(10.5, 2.4), sharey=True)
ymax = max(max(by_year[b].values()) for b in BLOCKS)
for ax, b in zip(axes, BLOCKS):
    vals = [by_year[b][y] for y in years]
    ax.bar(years, vals, color=COL[b], width=0.72, edgecolor='white', linewidth=1)
    ax.set_title(LABEL[b], fontsize=8, color=INK, loc='left')
    ax.set_xticks([2016, 2018, 2020, 2022, 2024]); ax.set_xticklabels(['16', '18', '20', '22', '24'])
    ax.set_ylim(0, ymax * 1.15)
    ax.yaxis.grid(True, color=GRID, linewidth=0.6); ax.set_axisbelow(True)
    ax.text(0.02, 0.92, f'n = {sum(vals)}', transform=ax.transAxes, fontsize=8, color=INK2)
axes[0].set_ylabel('papers')
save(fig, 'fig_year_by_block')

# 2. total per year with citations (two separate panels, never dual axis)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.4, 2.5))
a1.bar(years, [tot_year[y] for y in years], color=S1, width=0.72)
a1.set_title('Included papers per year', loc='left', fontsize=9, color=INK)
a2.bar(years, [sum(cites(r) for r in INC if int(r['Year']) == y) for y in years], color=S1, width=0.72)
a2.set_title('Citations to papers of each year', loc='left', fontsize=9, color=INK)
for a in (a1, a2):
    a.set_xticks(years[::2]); a.yaxis.grid(True, color=GRID, linewidth=0.6); a.set_axisbelow(True)
save(fig, 'fig_year_totals')

# 3. top countries (whole counting), horizontal bars
top_c = ctry.most_common(15)[::-1]
fig, ax = plt.subplots(figsize=(4.6, 3.6))
ax.barh([c for c, _ in top_c], [n for _, n in top_c], color=S1, height=0.7)
for i, (c, n) in enumerate(top_c):
    ax.text(n + 0.5, i, str(n), va='center', fontsize=8, color=INK2)
ax.set_xlabel('papers with at least one author from the country')
ax.xaxis.grid(True, color=GRID, linewidth=0.6); ax.set_axisbelow(True)
save(fig, 'fig_countries')

# 4. top author keywords
top_k = akw.most_common(20)[::-1]
fig, ax = plt.subplots(figsize=(4.6, 4.2))
ax.barh([k for k, _ in top_k], [n for _, n in top_k], color=S1, height=0.7)
for i, (k, n) in enumerate(top_k):
    ax.text(n + 0.3, i, str(n), va='center', fontsize=8, color=INK2)
ax.set_xlabel('papers using the author keyword')
ax.xaxis.grid(True, color=GRID, linewidth=0.6); ax.set_axisbelow(True)
save(fig, 'fig_author_keywords')

# 5. citation distribution (log-binned counts)
bins = [0, 1, 5, 10, 25, 50, 100, 250, 10**6]
lab = ['0', '1-4', '5-9', '10-24', '25-49', '50-99', '100-249', '250+']
cnt = [sum(1 for r in INC if bins[i] <= cites(r) < bins[i + 1]) for i in range(len(lab))]
fig, ax = plt.subplots(figsize=(4.6, 2.4))
ax.bar(lab, cnt, color=S1, width=0.72)
for i, n in enumerate(cnt):
    ax.text(i, n + 1, str(n), ha='center', fontsize=8, color=INK2)
ax.set_xlabel('citations (Scopus, ' + EXPORT_DATE + ')'); ax.set_ylabel('papers')
ax.yaxis.grid(True, color=GRID, linewidth=0.6); ax.set_axisbelow(True)
save(fig, 'fig_citation_distribution')

print(json.dumps(metrics, indent=1))
print('countries', ctry.most_common(10))
print('sources', src.most_common(8))
print('akw', akw.most_common(15))

# ---------------------------------------------------------------- links between blocks
# co-authorship: authors (Scopus ID) whose included papers fall in more than one block;
# citations: an included paper cites another included paper when the cited title
# (first 60 letters/digits) appears in its reference list (approximate matching)
first_block = {r['EID']: r['blocks'][0] for r in INC}
au_blocks = collections.defaultdict(set)
for r in INC:
    for a in authors(r):
        au_blocks[a].add(first_block[r['EID']])
norm = lambda t: re.sub(r'[^a-z0-9]', '', t.lower())
tkey = {r['EID']: norm(r['Title'].split(';')[0])[:60] for r in INC if len(norm(r['Title'])) > 30}
links = collections.Counter()
for r in INC:
    ref = norm(r['References'])
    for e, t in tkey.items():
        if e != r['EID'] and t in ref:
            links[(first_block[r['EID']], first_block[e])] += 1
rows = [('authors_in_more_than_one_block', '', sum(1 for v in au_blocks.values() if len(v) > 1))]
rows += [('authors_in_blocks', '+'.join(sorted(k)), n) for k, n in
         sorted(collections.Counter(frozenset(v) for v in au_blocks.values() if len(v) > 1).items(), key=lambda x: -x[1])]
rows += [('citations', f'{a}->{b}', n) for (a, b), n in sorted(links.items())]
write_tsv('block_links.tsv', ['link', 'citing->cited', 'n'], rows)
print('block links', rows)
