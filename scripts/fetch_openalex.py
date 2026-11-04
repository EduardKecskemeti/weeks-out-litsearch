"""Re-run the final search queries live against the OpenAlex API and compare
the result with the archived snapshot (data/raw/blockmap_v2.txt).

    python scripts/fetch_openalex.py                 # all final blocks
    python scripts/fetch_openalex.py --block b2      # one block
    python scripts/fetch_openalex.py --save live/    # also write the fetched IDs

Optional environment variables:
    OPENALEX_API_KEY   your OpenAlex API key (raises rate limits)
    OPENALEX_MAILTO    your e-mail, for OpenAlex's polite pool

Standard library only. OpenAlex keeps growing and re-indexing, so a re-run
months later will not match exactly: expect most of the archived IDs to come
back, plus some newly indexed records. The report shows both directions.
"""
import argparse, json, os, sys, time, urllib.parse, urllib.request, urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API = 'https://api.openalex.org/works'

def get(params, tries=5):
    url = API + '?' + urllib.parse.urlencode(params)
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'weeks-out-litsearch'}), timeout=60) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 429 and i < tries - 1:      # rate limited: back off and retry
                time.sleep(2 ** i * 2)
                continue
            raise
    raise RuntimeError('unreachable')

def fetch(query, filters):
    flt = f'title_and_abstract.search:{query},{filters}'
    base = {'filter': flt, 'per-page': 200, 'select': 'id'}
    if os.environ.get('OPENALEX_API_KEY'):
        base['api_key'] = os.environ['OPENALEX_API_KEY']
    if os.environ.get('OPENALEX_MAILTO'):
        base['mailto'] = os.environ['OPENALEX_MAILTO']
    ids, page, total = [], 1, None
    while True:
        j = get(dict(base, page=page))
        total = j['meta']['count']
        ids += [w['id'].rsplit('/', 1)[1] for w in j['results']]
        if len(ids) >= total or not j['results']:
            break
        page += 1
        time.sleep(0.5)
    return total, ids

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--block', help='only this block, e.g. b2')
    ap.add_argument('--save', help='directory to write live_<block>.txt ID lists')
    a = ap.parse_args()

    Q = json.load(open(os.path.join(ROOT, 'search', 'queries.json'), encoding='utf-8'))
    archived = {}
    for tok in open(os.path.join(ROOT, 'data', 'raw', 'blockmap_v2.txt'), encoding='utf-8').read().split():
        wid, blocks = tok.split(':')
        for b in blocks.split('+'):
            archived.setdefault(b, set()).add(wid)

    print(f"filters: {Q['filters']}\n")
    print(f"{'block':6} {'archived':>8} {'live':>6} {'both':>6} {'only archived':>14} {'only live':>10}")
    union_live = set()
    for q in Q['final']:
        b = q['block']
        if a.block and b != a.block:
            continue
        total, ids = fetch(q['query'], Q['filters'])
        live, old = set(ids), archived.get(b, set())
        union_live |= live
        print(f"{b:6} {len(old):8} {total:6} {len(live & old):6} {len(old - live):14} {len(live - old):10}")
        if a.save:
            os.makedirs(a.save, exist_ok=True)
            open(os.path.join(a.save, f'live_{b}.txt'), 'w', encoding='utf-8').write('\n'.join(sorted(live)) + '\n')
    if not a.block:
        old_union = set().union(*archived.values())
        print(f"\nunion: archived {len(old_union)}, live {len(union_live)}, "
              f"recovered {len(old_union & union_live) / len(old_union):.1%} of the archived records")

if __name__ == '__main__':
    try:
        main()
    except urllib.error.URLError as e:
        sys.exit(f'Could not reach OpenAlex: {e}')
