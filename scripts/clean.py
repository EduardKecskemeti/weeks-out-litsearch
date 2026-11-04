"""Clean the merged OpenAlex set. Every removal is logged with its rule."""
import json, re, collections, csv

R = json.load(open('build/merged_v2.json', encoding='utf-8'))
removed = []          # (rule, id, title)

def drop(rule, keep_fn):
    global R
    k = []
    for r in R:
        if keep_fn(r):
            k.append(r)
        else:
            removed.append((rule, r['id'], r['title']))
    R = k

doi = lambda r: (r['doi'] or '').lower()
title = lambda r: r['title'] or ''

# R1 commercial spam (product adverts posted to Zenodo or ad pages without any source)
spam = re.compile(r'(gumm|capsule|booster|enhancement|scam|legit|drops|protein powders|clenbutrol|'
                  r'tips for better sleep|natural weight loss products|\(#1|\[get 100%)', re.I)
drop('R1 commercial spam', lambda r: not (spam.search(title(r)) and
     (r['source'] is None or (r['source'] or '').startswith('Zenodo'))))

# R2 retracted articles and retraction notices
drop('R2 retracted / retraction notice', lambda r: not re.match(r'\s*retract(ed|ion)\b', title(r), re.I))

# R3 front matter, abstract books, news, obituaries (not research contributions)
front = re.compile(r'(abstract supplement|abstracts supplement|selected abstracts|^this issue of|'
                   r'^research bites$|^manufacturers news$|^thomas h\. kunz$|table of contents|'
                   r'annual lambda alpha symposium|^update on technologies, medicines|'
                   r'^keyword index$|^title index$|^speakers. presentations$|^oral presentation s\d|'
                   r'^proceedings of the .* conference)', re.I)
# author-less section headers of abstract books (e.g. "Cardiac Surgery", "Bariatric/Foregut")
SECTION_HEADERS = {'W4414782254', 'W4414782054', 'W4414781784', 'W4414781808'}
drop('R3 front matter / non-research', lambda r: not front.search(title(r).strip()) and r['id'] not in SECTION_HEADERS)

# R4 no DOI and no source (cannot be identified as a published item)
drop('R4 no DOI and no source', lambda r: r['doi'] or r['source'])

# R5 repository copies with no publisher DOI (theses, local copies) and preprint DOIs
def ok_repo(r):
    d = doi(r)
    if d.startswith('10.48550') or d.startswith('10.5281'):
        return False
    if r['source_type'] == 'repository' and not d:
        return False
    return True
drop('R5 repository copy / preprint without publisher DOI', ok_repo)

# R6 non-English despite language tag (title in Portuguese, Spanish, Indonesian...)
non_en = re.compile(r'\b(de|da|dos|das|em|para|com|uma|um|relação|métodos|praticantes|'
                    r'musculação|avaliação|academias|influência|suplementação|consumo|alimentar|'
                    r'una|aproximación|clasificación|rostros|usando|antropometría|facial\b.*\bde|'
                    r'rekonstruksi|wajah|membangun|dari|tengkorak|universitários|fatores|'
                    r'utilização|suplementos|alimentares|por|klasifikasi|berbasis|melalui|'
                    r'pengolahan|citra|tubuh|estimasi)\b', re.I)
def is_en(r):
    t = title(r)
    if re.search(r'[Ѐ-ӿ]{3,}', t):      # Cyrillic-script title
        return False
    hits = len(non_en.findall(t))
    return hits < 2
drop('R6 non-English title', is_en)

# R7 duplicates by normalised title: keep record with DOI, then venue, then citations
def norm(t):
    return re.sub(r'[^a-z0-9]', '', t.lower())
groups = collections.defaultdict(list)
for r in R:
    groups[norm(title(r))].append(r)
def score(r):
    return (bool(r['doi']), r['source_type'] in ('journal', 'conference', 'book series'),
            r['type'] != 'review' or True, r['cited_by'] or 0)
keep_ids = set()
for g in groups.values():
    best = max(g, key=score)
    keep_ids.add(best['id'])
drop('R7 duplicate title', lambda r: r['id'] in keep_ids)

print('kept', len(R))
c = collections.Counter(x[0] for x in removed)
for k in sorted(c):
    print(f'{k}: {c[k]}')
with open('results/removed_records.tsv', 'w', encoding='utf-8', newline='\n') as f:
    f.write('rule\tid\ttitle\n')
    for x in removed:
        f.write('\t'.join(x) + '\n')
json.dump(R, open('build/clean_v2.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
