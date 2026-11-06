import json,sys,math
from collections import Counter
d=json.load(open(sys.argv[1],encoding='utf-8'))
def w(k,n,z=1.959964):
    if not n: return None
    p=k/n;q=1+z*z/n;c=(p+z*z/(2*n))/q;h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/q
    return round(100*p,1),round(100*(c-h),1),round(100*(c+h),1)
print({k:v for k,v in d.items() if k!='details'})
for lb in ('phishing','clean'):
    r=[x for x in d['details'] if x['label']==lb]; n=len(r)
    print(lb,n,Counter(x['verdict'] for x in r)); print(Counter(x['decided_by'] for x in r))
    print(' C clean',sum(x['c_label']=='clean' for x in r),' B',sum(x['b_flag'] is True for x in r))
    print(' D usable',sum(x['llm_unusable'] is False for x in r),'unusable',sum(x['llm_unusable'] is True for x in r),'not called',sum(x['llm_unusable'] is None for x in r))
    dd=[x for x in r if x['llm_unusable'] is False]
    print(' D verdicts',Counter(x['llm_verdict'] for x in dd))
    s=sum(x['verdict']=='clean' for x in r); print(' safe rate',s,w(s,n))
    u=[x for x in r if x['decided_by'].startswith('D_llm')]; sd=sum(x['verdict']=='clean' for x in u); print(' D decided',len(u),'safe',sd,w(sd,len(u)))
    l=sorted(x['latency_s'] for x in r if x.get('latency_s') is not None); print(' lat p50,p95',l[len(l)//2],l[int(len(l)*.95)])
print('errors',[x['decided_by'] for x in d['details'] if x['verdict'] is None][:5])
print('missed',[ (x['url'][:70].replace('.','[.]'),x['decided_by'],x['c_score']) for x in d['details'] if x['label']=='phishing' and x['verdict']=='clean'])
print('clean flagged',[ (x['url'][:60],x['verdict'],x['decided_by']) for x in d['details'] if x['label']=='clean' and x['verdict'] in('phishing',)])
