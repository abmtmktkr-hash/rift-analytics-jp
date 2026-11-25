"""Download approved Wild Rift icons locally. No automatic publishing."""
import argparse
import json
import re
import time
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import Request, build_opener, HTTPRedirectHandler

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        raise ValueError('Redirect refused')

opener = build_opener(NoRedirect())
LIMIT = 500_000

def allowed(url):
    if not isinstance(url, str):
        return False
    u = urlsplit(url)
    return (u.scheme == 'https' and u.netloc == 'game.gtimg.cn'
            and u.path.startswith('/images/lgamem/act/lrlib/img/')
            and '%' not in u.path and '..' not in u.path)

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--catalog', default='assets/catalog.json')
    p.add_argument('--output', default='assets-test')
    p.add_argument('--approved', action='store_true', help='Confirm permission to download and use these assets')
    a = p.parse_args()
    catalog = json.loads(Path(a.catalog).read_text(encoding='utf-8'))
    jobs = [(kind, ident, row.get('icon_source')) for kind in ('equip','rune','skill')
            for ident,row in catalog.get(kind,{}).items()
            if re.fullmatch(r'[0-9]{1,16}',ident) and allowed(row.get('icon_source'))]
    print('Eligible icons:',len(jobs))
    if not a.approved:
        print('Dry run only. No images downloaded.')
        return
    saved = skipped = failed = 0
    for kind, ident, url in jobs:
        dest = Path(a.output)/kind/(ident+'.png')
        if dest.is_file() and dest.stat().st_size <= LIMIT and dest.read_bytes().startswith(b'\x89PNG\r\n\x1a\n'):
            skipped += 1
            continue
        try:
            time.sleep(0.5)
            with opener.open(Request(url,headers={'User-Agent':'RiftAnalyticsJP/1.0'}),timeout=20) as r:
                raw = r.read(LIMIT+1)
            if len(raw)>LIMIT or not raw.startswith(b'\x89PNG\r\n\x1a\n'):
                raise ValueError('Not an accepted PNG')
            dest.parent.mkdir(parents=True,exist_ok=True)
            tmp = dest.with_suffix('.tmp')
            tmp.write_bytes(raw)
            tmp.replace(dest)
            saved += 1
        except Exception as exc:
            failed += 1
            print(kind,ident,type(exc).__name__,str(exc))
    print(f'Saved {saved}; skipped {skipped}; failed {failed}')
    if failed:
        raise SystemExit(1)

if __name__ == '__main__':
    main()
