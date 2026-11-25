#!/usr/bin/env python3
"""Manual, bounded Wild Rift detail collector. Python standard library only."""
import argparse
import datetime as dt
import json
import pathlib
import re
import time
import urllib.request
import urllib.error

ROOT = pathlib.Path(__file__).resolve().parent
BASE = 'https://mlol.qt.qq.com/go/lgame_battle_info/'
ROSTER = 'https://game.gtimg.cn/images/lgamem/act/lrlib/js/heroList/hero_list.js'
ENDPOINTS = ('hero_counter_point', 'hero_best_partner', 'hero_equip_core', 'hero_equip_shoe', 'hero_equip_rune', 'hero_equip_skill')


def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'RiftAnalyticsJP/2.0', 'Accept': 'application/json'})
    with urllib.request.urlopen(req, timeout=25) as r:
        raw = r.read(2000001)
    if len(raw) > 2000000:
        raise ValueError('Response too large')
    return json.loads(raw)


def validate(endpoint, obj):
    data = obj.get('data')
    expected = list if endpoint == 'hero_counter_point' else dict
    if obj.get('result') != 0 or not isinstance(data, expected) or not data:
        raise ValueError('Unexpected or empty API data')
    if endpoint.startswith('hero_equip_') and not data.get('classic'):
        raise ValueError('Missing classic data')
    if endpoint == 'hero_best_partner' and not data.get('partner_list'):
        raise ValueError('Missing partner list')
    return data


def save(path, obj):
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(obj, ensure_ascii=False, separators=(',', ':'), allow_nan=False), encoding='utf-8')
    tmp.replace(path)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--limit', type=int, default=3)
    p.add_argument('--all', action='store_true', help='Enable only after confirming bulk access and reuse permission')
    p.add_argument('--force', action='store_true')
    args = p.parse_args()
    if args.limit < 1 or (args.limit > 3 and not args.all):
        p.error('Use --all only after confirming permission')
    roster = fetch(ROSTER)['heroList']
    ids = sorted((str(k) for k in roster if re.fullmatch(r'[0-9]{1,10}', str(k))), key=int)
    if not ids:
        raise ValueError('Empty roster')
    out = ROOT / 'details'
    out.mkdir(exist_ok=True)
    now = dt.datetime.now(dt.timezone.utc)
    pending = []
    for hid in ids:
        path = out / (hid + '.json')
        if not args.force and path.exists():
            try:
                old = json.loads(path.read_text())
                age = now - dt.datetime.fromisoformat(old['fetched_at'])
                if dt.timedelta(0) <= age < dt.timedelta(days=14) and all(k in old['data'] for k in ENDPOINTS):
                    continue
            except (ValueError, KeyError, TypeError):
                pass
        pending.append(hid)
    targets = pending if args.all else pending[:args.limit]
    print(f'Roster: {len(ids)}; pending: {len(pending)}; selected: {len(targets)}', flush=True)
    failures = 0
    for hid in targets:
        data = {}
        try:
            for endpoint in ENDPOINTS:
                try:
                    data[endpoint] = validate(endpoint, fetch(BASE + endpoint + '?hero_id=' + hid))
                finally:
                    time.sleep(3)
            save(out / (hid + '.json'), {'hero_id': hid, 'fetched_at': dt.datetime.now(dt.timezone.utc).isoformat(), 'source': 'Tencent CN', 'data': data})
            print(f'PASS {hid}', flush=True)
        except urllib.error.HTTPError as exc:
            failures += 1
            print(f'FAIL {hid}: HTTP {exc.code}; previous file preserved', flush=True)
            if exc.code in (401, 403, 429) or exc.code >= 500:
                print('Stopping to avoid additional load', flush=True)
                break
        except (OSError, ValueError, TypeError, KeyError) as exc:
            failures += 1
            print(f'FAIL {hid}: {type(exc).__name__}; previous file preserved', flush=True)
            break
    print(f'Finished; failures={failures}', flush=True)
    return bool(failures)


if __name__ == '__main__':
    raise SystemExit(main())
