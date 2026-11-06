import json, sys
from datetime import datetime, timezone
from collections import Counter
import math
d=json.load(open(sys.argv[1],encoding='utf-8'))
LIST=datetime(2024,5,16,tzinfo=timezone.utc).timestamp()
def cat(r):
    x=r['rdap']
    if x.get('found')==0: return 'not_registered_now'
    if 'registered' in x: return 're_registered_after_listing' if x['registered']>LIST else 'registered_before_listing'
    return 'unknown'
def grp(r):
    if r['verdict']=='clean': return 'missed(safe)'
    if r['llm_unusable'] is True: return 'warned_fallback(no page)'
    return 'warned_by_D'
t=Counter((grp(r),cat(r)) for r in d)
for g in sorted({k[0] for k in t}):
    n=sum(v for k,v in t.items() if k[0]==g)
    print(g,n,{k[1]:v for k,v in t.items() if k[0]==g})
print('overall',Counter(cat(r) for r in d))
print([ (r['domain'],cat(r)) for r in d if r['verdict']=='clean'])
