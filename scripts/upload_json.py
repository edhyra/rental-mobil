#!/usr/bin/env python3
import json
import sys
from urllib.request import Request, urlopen
from urllib.error import HTTPError

if len(sys.argv) < 3:
    print('Usage: upload_json.py <collection> <json_file>')
    sys.exit(2)

collection = sys.argv[1]
fn = sys.argv[2]
with open(fn, 'r', encoding='utf-8') as f:
    data = json.load(f)

payload = json.dumps({'collection': collection, 'doc': data}).encode('utf-8')
req = Request('http://127.0.0.1:8081/insert', data=payload, headers={'Content-Type': 'application/json'})
try:
    with urlopen(req) as resp:
        print('Response:', resp.status, resp.read().decode())
except HTTPError as e:
    print('HTTP Error:', e.code, e.read().decode())

