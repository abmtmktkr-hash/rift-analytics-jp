import json, datetime as d, urllib.request, pathlib, os, math
p=pathlib.Path('data.json'); now=d.datetime.now(d.timezone.utc)
old=json.loads(p.read_text()) if p.exists() else {}
if os.getenv('FORCE')!='true' and old.get('updated') and now-d.datetime.fromisoformat(old['updated'])<d.timedelta(days=14): raise SystemExit(0)
def get(url):
 with urllib.request.urlopen(url,timeout=30) as r: return json.load(r)
s=get('https://ry2x.github.io/WildRift-Merged-Stats-Data/heroStats.json'); names={x['id']:x['name'] for x in get('https://ry2x.github.io/WildRift-Merged-Champion-Data/data_ja_JP.json')}
date=d.datetime.fromisoformat(s['date'].replace('Z','+00:00')); assert d.timedelta(days=-1)<=now-date<d.timedelta(days=4), 'Stale statistics'
lanes={}
for k in ['top','jungle','mid','ad','support']:
 a=[]
 for x in s['data']['diamond_plus'][k]:
  r={'id':x['id'],'name':names[x['id']]}
  for field,src in [('wr','win'),('pr','appear'),('br','forbid')]:
   v=float(x[src+'_rate_percent'].rstrip('%')); assert math.isfinite(v) and 0<=v<=100; r[field]=v
  a.append(r)
 assert len(a)>=10 and len({r['id'] for r in a})==len(a)
 for r in a:
  r['score']=round(sum(w*sum((q[f]<r[f])+.5*(q[f]==r[f]) for q in a if q is not r)/(len(a)-1) for f,w in [('wr',60),('pr',25),('br',15)]),2)
 a.sort(key=lambda r:(-r['score'],-r['wr'],r['id']))
 prev={r['id']:r['rank'] for r in old.get('lanes',{}).get(k,[])}
 for i,r in enumerate(a,1):
  r['rank']=i;r['delta']=prev[r['id']]-i if r['id'] in prev else None
  r['tier']=next(t for v,t in [(80,'S+'),(65,'S'),(50,'A'),(35,'B'),(0,'C')] if r['score']>=v)
 lanes[k]=a
out={'updated':now.isoformat(),'date':s['date'],'lanes':lanes}; tmp=p.with_suffix('.tmp');tmp.write_text(json.dumps(out,ensure_ascii=False,indent=2));tmp.replace(p)
