import json, datetime as d, urllib.request, pathlib, os, re, math
p=pathlib.Path('data.json'); now=d.datetime.now(d.timezone.utc)
old=json.loads(p.read_text()) if p.exists() else {}
if os.getenv('FORCE','').lower()!='true' and old.get('updated') and now-d.datetime.fromisoformat(old['updated'])<d.timedelta(days=14):
 print('Not due yet'); raise SystemExit(0)
def get(url):
 print('Fetching:',url,flush=True)
 with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0','Accept':'application/json, */*'}),timeout=45) as r: return json.load(r)
s=get('https://mlol.qt.qq.com/go/lgame_battle_info/hero_rank_list_v2')
assert str(s['result'])=='0', 'API error'
h=get('https://game.gtimg.cn/images/lgamem/act/lrlib/js/heroList/hero_list.js')
heroes=h['heroList']; heroes=heroes.values() if isinstance(heroes,dict) else heroes
base='https://ddragon.leagueoflegends.com/'
version=get(base+'api/versions.json')[0]
localized=get(base+'cdn/'+version+'/data/ja_JP/champion.json')['data']
names={k.lower():v['name'] for k,v in localized.items()}
names.update({'monkeyking':'ウーコン','norra':'ノラ'})
lookup={}
for x in heroes:
 key=re.search(r'/([^/]+)_\d+\.[a-zA-Z]+(?:\?.*)?$',x.get('poster',''))
 lookup[str(x['heroId'])]=names.get(key.group(1).lower(),key.group(1)) if key else x.get('name',str(x['heroId']))
lanes={}; dates=set()
for k,role in [('top','2'),('jungle','5'),('mid','1'),('ad','3'),('support','4')]:
 a=[]
 for x in s['data']['1'][role]:
  uid=str(x['hero_id']); dates.add(str(x['dtstatdate']))
  r={'id':uid,'name':lookup[uid]}
  for field,src in [('wr','win'),('pr','appear'),('br','forbid')]:
   v=float(x[src+'_rate'])*100
   assert math.isfinite(v) and 0<=v<=100,(field,v); r[field]=round(v,2)
  a.append(r)
 assert len(a)>=10 and len({r['id'] for r in a})==len(a)
 for r in a:
  r['score']=round(sum(w*sum((q[f]<r[f])+.5*(q[f]==r[f]) for q in a if q is not r)/(len(a)-1) for f,w in [('wr',60),('pr',25),('br',15)]),2)
 a.sort(key=lambda r:(-r['score'],-r['wr'],r['id']))
 prev={str(r['id']):r['rank'] for r in old.get('lanes',{}).get(k,[])}
 for i,r in enumerate(a,1):
  r['rank']=i;r['delta']=prev[r['id']]-i if r['id'] in prev else None
  r['tier']=next(t for v,t in [(80,'S+'),(65,'S'),(50,'A'),(35,'B'),(0,'C')] if r['score']>=v)
 lanes[k]=a
assert len(dates)==1, dates
raw=dates.pop(); date=d.datetime.strptime(raw[:8],'%Y%m%d').date() if re.fullmatch(r'\d{8}',raw[:8]) else d.date.fromisoformat(raw[:10])
assert -1<=(now.date()-date).days<=4,'Stale statistics'
out={'updated':now.isoformat(),'date':date.isoformat(),'lanes':lanes,'source':'Tencent China ranked stats'}
tmp=p.with_suffix('.tmp');tmp.write_text(json.dumps(out,ensure_ascii=False,indent=2));tmp.replace(p)
print('Saved',date, {k:len(v) for k,v in lanes.items()})
