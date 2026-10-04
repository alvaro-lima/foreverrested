"""Cache public Forever pages for action-location review (no automatic imports)."""
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import re
from urllib.request import Request,urlopen
ROOT=Path(__file__).resolve().parents[1]
CACHE=Path(os.environ['TEMP'])/'ForeverRested-LocationResearch'

def fetch(kind,identity):
    CACHE.mkdir(exist_ok=True)
    path=CACHE/f'{kind}-{identity}.html'
    url=f'https://www.wowhead.com/forever/{kind}={identity}'
    if not path.exists():
        with urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=25) as response:
            path.write_bytes(response.read())
    raw=path.read_text(encoding='utf-8')
    mapper=re.search(r'var g_mapperData\s*=\s*',raw)
    data=json.JSONDecoder().raw_decode(raw[mapper.end():])[0] if mapper else None
    # Related entity tables identify acquisition sources for manual review.
    tables=re.findall(r'new Listview\((.{0,180})',raw)
    return dict(kind=kind,id=identity,url=url,mapper=data,tables=tables)

if __name__=='__main__':
    ref=json.loads((ROOT/'Data/alliance-reference.json').read_text(encoding='utf-8'))['quests']
    missing=json.loads((ROOT/'Data/MISSING_QUEST_LOCATIONS.json').read_text())['missing']
    requests={('quest',r['questID']) for r in missing}
    for r in missing:
        for o in ref[str(r['questID'])].get('objectives',[]):
            if o.get('kind')=='item':requests.add(('item',o['id']))
    requests.update({('item',1972),('object',665282)})
    with ThreadPoolExecutor(max_workers=6) as pool:
        jobs=[pool.submit(fetch,*key) for key in sorted(requests)]
        for job in jobs:
            try:print(json.dumps(job.result()))
            except Exception as error:print(json.dumps({'error':str(error)}))
