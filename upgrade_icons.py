"""Run from repository root. Updates champion.html, preserving its CSP."""
from pathlib import Path
import re, hashlib, base64
p=Path('champion.html')
s=p.read_text(encoding='utf-8')
old='else{nameCell.textContent=name}tr.append(nameCell)'
new=r'''else if(['equip','rune','skill'].includes(kind)){const wrap=el('div','');wrap.className='asset-list';for(const id of String(r[idkey]??'').split(',').map(x=>x.trim()).filter(Boolean)){const item=el('div','');item.className='asset-item';const label=catalog[kind]?.[id]?.name_ja||catalog[kind]?.[id]?.name_zh||'ID '+id;if(/^\d{1,16}$/.test(id)){const pic=document.createElement('img');pic.src='./assets/'+kind+'/'+id+'.png';pic.alt='';pic.loading='lazy';pic.onerror=()=>pic.remove();item.append(pic)}item.append(el('span',label));wrap.append(item)}nameCell.append(wrap)}else{nameCell.textContent=name}tr.append(nameCell)'''
assert s.count(old)==1, 'Unexpected HTML version; no changes made'
s=s.replace(old,new)
css='.asset-list{display:flex;flex-wrap:wrap;gap:8px 4px;align-items:flex-start}.asset-item{display:flex;flex-direction:column;align-items:center;text-align:center;flex:1 1 46px;max-width:90px;min-width:0;font-size:11px;line-height:1.3;overflow-wrap:anywhere}.asset-item img{width:36px;height:36px;margin:0 0 4px;object-fit:contain}'
assert s.count('</style>')==1
s=s.replace('</style>',css+'</style>')
for tag,directive in [('script','script-src'),('style','style-src')]:
    body=re.search(r'<'+tag+r'>(.*?)</'+tag+r'>',s,re.S).group(1)
    digest=base64.b64encode(hashlib.sha256(body.encode()).digest()).decode()
    s,n=re.subn(r"("+directive+r" 'sha256-)[^']+(')",lambda m:m[1]+digest+m[2],s)
    assert n==1
p.write_text(s,encoding='utf-8')
print('Updated champion.html; CSP hashes refreshed')
