from pathlib import Path
import re, hashlib, base64
p=Path('index.html'); s=p.read_text()
assert 'id="tabs"' in s and 'function render()' in s
s=s.replace('<nav id="tabs"></nav>','<nav id="tabs"></nav><section><label>チャンピオン検索 <input id="query" type="search" placeholder="日本語名称"></label> <label><input id="all" type="checkbox"> 全レーン一覧</label> <label><input id="full" type="checkbox"> TOP20圏外も表示</label><p id="count"></p></section>')
s=s.replace('</style>','input[type=search]{background:#18263a;color:white;border:1px solid #41536c;border-radius:8px;padding:10px;max-width:100%}a.champ{color:inherit;text-decoration:none}a.champ:hover{text-decoration:underline}</style>')
s=s.replace("const a=[...data.lanes[lane]].sort((a,b)=>b[k]-a[k]||a.rank-b.rank).slice(0,20);", "const q=$('query').value.trim().normalize('NFKC').toLowerCase();const all=$('all').checked;const full=$('full').checked||!!q||all;const pool=all?[...new Map(roles.flatMap(([key])=>data.lanes[key]).sort((a,b)=>b[k]-a[k]).map(r=>[String(r.id),r]).reverse()).values()]:data.lanes[lane];const filtered=pool.filter(r=>r.name.normalize('NFKC').toLowerCase().includes(q)).sort((a,b)=>b[k]-a[k]||a.rank-b.rank);const a=full?filtered:filtered.slice(0,20);$('heading').textContent=(all?'全レーン（各指標の最高値を持つ行）':label)+(full?' 一覧':' TOP20');$('count').textContent=a.length+' / '+filtered.length+' 件';")
s=s.replace("document.createElement('span');wrap.className='champ';", "document.createElement('a');wrap.className='champ';wrap.href='./champion.html?id='+encodeURIComponent(r.id);")
s=s.replace("$('sort').onchange=render;", "$('sort').onchange=render;$('query').oninput=render;$('all').onchange=render;$('full').onchange=render;")
s=s.replace('全5レーン・ランキング TOP20','全5レーン・ランキング / チャンピオン検索')
for tag in ('script','style'):
 body=re.search(r'<'+tag+r'>(.*?)</'+tag+r'>',s,re.S).group(1)
 h=base64.b64encode(hashlib.sha256(body.encode()).digest()).decode()
 s=re.sub(r"("+tag+r"-src )'sha256-[^']+'",lambda m:m[1]+"'sha256-"+h+"'",s)
p.write_text(s)
print('Search upgrade complete')
