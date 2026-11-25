"""Build a local Wild Rift catalog. No image downloads or publication by default."""
import argparse, json, pathlib, urllib.request, time
from urllib.parse import urlsplit
BASE='https://game.gtimg.cn/images/lgamem/act/lrlib/js/'
KINDS=('equip','rune','skill')
# Conservative starter translations; unreviewed entries retain their original names.
NAMES={'equip':{'2104':'増魔の書','2121':'女神の涙','2122':'シーン','2141':'ライアンドリーの仮面','2143':'リッチ ベイン','2145':'ラバドン デスキャップ','2201':'ロング ソード','2242':'ルインドキング ブレード','2244':'トリニティ フォース','2245':'インフィニティ エッジ'},'rune':{'572111001':'不死者の握撃','572112001':'征服者','572113001':'電撃','572114001':'エアリー召喚','572115001':'フェイズラッシュ','572116001':'フリートフットワーク','572120001':'リーサルテンポ','572122001':'ファーストストライク','572124001':'秘儀の彗星','572312001':'ボーンアーマー','572318001':'息継ぎ'},'skill':dict(zip(['81010101','81030101','81050101','81060101','81070101','81090101','81100101','81110101'],['ゴースト','ヒール','バリア','イグゾースト','クレンズ','フラッシュ','イグナイト','スマイト']))}
def build(load):
    out={}
    for kind in KINDS:
        rows=load(kind)[kind+'List']; result={}
        for row in rows:
            ident=str(row[kind+'Id']); name=row['name']; icon=row['iconPath']; u=urlsplit(icon)
            if not ident.isascii() or not ident.isdecimal() or not isinstance(name,str): raise ValueError('Invalid catalog row')
            if u.scheme!='https' or u.hostname!='game.gtimg.cn' or not u.path.startswith('/images/lgamem/act/lrlib/img/'): icon=None
            if ident in result: raise ValueError('Duplicate ID: '+ident)
            result[ident]={'name_zh':name,'name_ja':NAMES[kind].get(ident),'icon_source':icon}
        if not result: raise ValueError('Empty catalog')
        out[kind]=result
        print(kind,len(result),'Japanese starter names:',sum(bool(x['name_ja']) for x in result.values()))
    return out

def main():
    p=argparse.ArgumentParser(); p.add_argument('--har'); p.add_argument('--output',default='assets-test/catalog.json'); a=p.parse_args()
    if a.har:
        entries=json.loads(pathlib.Path(a.har).read_text())['log']['entries']
        def load(k):
            url=BASE+k+'/'+k+'.js'
            return json.loads(next(e['response']['content']['text'] for e in entries if e['request']['url'].split('?')[0]==url))
    else:
        def load(k):
            time.sleep(3)
            req=urllib.request.Request(BASE+k+'/'+k+'.js',headers={'User-Agent':'RiftAnalyticsJP-API-Test/1.0'})
            with urllib.request.urlopen(req,timeout=20) as r:
                raw=r.read(2000001)
            if len(raw)>2000000: raise ValueError('Catalog too large')
            return json.loads(raw)
    out=build(load); dest=pathlib.Path(a.output); dest.parent.mkdir(parents=True,exist_ok=True); tmp=dest.with_suffix('.tmp'); tmp.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8'); tmp.replace(dest)
if __name__=='__main__': main()
