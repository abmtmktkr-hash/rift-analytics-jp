import json, pathlib, re, urllib.request
base='https://ddragon.leagueoflegends.com/'
def fetch(url, limit=2000000):
    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'RiftAnalyticsJP/1.0'}),timeout=30) as r:
        b=r.read(limit+1)
        if len(b)>limit: raise ValueError('Response too large')
        return b
v=json.loads(fetch(base+'api/versions.json'))[0]
assert re.fullmatch(r'\d+\.\d+\.\d+',v)
ch=json.loads(fetch(base+'cdn/'+v+'/data/ja_JP/champion.json'))['data']
byname={c['name']:c['image']['full'] for c in ch.values()}
byname['ウーコン']='MonkeyKing.png'
rows={str(r['id']):r['name'] for a in json.loads(pathlib.Path('data.json').read_text())['lanes'].values() for r in a}
p=pathlib.Path('icons');p.mkdir(exist_ok=True)
for uid,name in rows.items():
    f=byname.get(name)
    if not re.fullmatch(r'\d{1,12}',uid) or not f or not re.fullmatch(r'[A-Za-z0-9_]+\.png',f): continue
    dest=p/(uid+'.png')
    if dest.exists(): continue
    try:
        b=fetch(base+'cdn/'+v+'/img/champion/'+f,500000)
        if not b.startswith(b'\x89PNG\r\n\x1a\n'): raise ValueError('Not PNG')
        tmp=dest.with_suffix('.tmp');tmp.write_bytes(b);tmp.replace(dest)
    except Exception as e: print('Icon unavailable:',uid,e)
print('Saved icons:',len(list(p.glob('*.png'))))
